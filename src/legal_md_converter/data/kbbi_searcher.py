"""
KBBI Searcher for Legal-MD-Converter.

Optimized search implementation with FTS5, Bloom filter caching,
and LRU lookup cache for high-performance spellchecking.
"""

import sqlite3
import threading
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
import hashlib
import re


logger = logging.getLogger(__name__)


@dataclass
class KBBISuggestion:
    """Represents a spelling suggestion."""
    word: str
    is_correct: bool
    suggestions: List[str]
    definition: Optional[str] = None


class BloomFilterCache:
    """Bloom filter for fast negative lookups."""

    _warned = False  # Class-level flag to warn only once

    def __init__(self, capacity: int = 500_000, error_rate: float = 0.001):
        self.capacity = capacity
        self.error_rate = error_rate
        self._filter = None
        self._initialized = False

        # Try to import bloom filter library
        try:
            from bloom_filter2 import BloomFilter
            self.BloomFilter = BloomFilter
        except ImportError:
            self.BloomFilter = None
            if not BloomFilterCache._warned:
                logger.debug('bloom_filter2 not available, using SQL fallback')
                BloomFilterCache._warned = True

    def initialize(self, words: List[str]) -> None:
        """Initialize bloom filter with known correct words."""
        if not self.BloomFilter:
            self._initialized = False
            return

        self._filter = self.BloomFilter(max_elements=self.capacity, error_rate=self.error_rate)
        for word in words:
            self._filter.add(word.lower())
        self._initialized = True
        logger.info(f'Bloom filter initialized with {len(words)} words')
    
    def might_contain(self, word: str) -> bool:
        """Check if word might be in dictionary (fast negative check)."""
        if not self._initialized or not self._filter:
            return True  # Fallback to SQL lookup
        return word.lower() in self._filter
    
    def add(self, word: str) -> None:
        """Add word to filter (for dynamic updates)."""
        if self._filter:
            self._filter.add(word.lower())
    
    @property
    def initialized(self) -> bool:
        return self._initialized


class KBBISearcher:
    """
    High-performance KBBI spellchecker with multiple optimization layers.
    
    Optimizations:
    1. SQLite FTS5 (Full-Text Search) for fast matching
    2. Bloom filter for negative caching
    3. LRU cache for recent lookups
    4. Connection pooling for thread safety
    5. Batch processing for bulk operations
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._local = threading.local()
        self._bloom_cache = BloomFilterCache()
        self._query_cache = {}  # Simple LRU cache
        self._cache_max_size = 1000
        self._indexed = False
        self._total_words = 0
        
        # Initialize connection and bloom filter
        self._initialize()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0
            )
            # Performance optimizations
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
            self._local.conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def _initialize(self) -> None:
        """Initialize database and bloom filter."""
        try:
            conn = self._get_connection()
            
            # Check if kata table exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='kata'"
            )
            
            if not cursor.fetchone():
                logger.warning('KBBI kata table not found. Creating schema...')
                self._create_schema(conn)
            
            # Check if FTS5 index exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='kata_fts'"
            )
            
            if not cursor.fetchone():
                self._create_fts_index(conn)
            
            # Get total word count
            cursor = conn.execute("SELECT COUNT(*) as count FROM kata")
            row = cursor.fetchone()
            if row:
                self._total_words = row[0]
                self._indexed = True
            
            logger.info(f'KBBI Searcher initialized with {self._total_words} words')
            
        except Exception as e:
            logger.error(f'Failed to initialize KBBI searcher: {e}', exc_info=True)
            self._indexed = False
    
    def _create_schema(self, conn: sqlite3.Connection) -> None:
        """Create database schema."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kata (
                rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                kata TEXT NOT NULL,
                entry_id INTEGER,
                is_bloom_candidate INTEGER DEFAULT 0,
                frequency INTEGER DEFAULT 1
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_kata_lower ON kata(LOWER(kata))
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_kata_freq ON kata(frequency DESC)
        """)
        
        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_kata_unique ON kata(LOWER(kata))
        """)
        
        conn.commit()
        logger.info('KBBI schema created')
    
    def _create_fts_index(self, conn: sqlite3.Connection) -> None:
        """Create FTS5 virtual table for fast search."""
        logger.info('Creating FTS5 index (one-time operation)...')
        
        # Create FTS5 virtual table
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS kata_fts USING fts5(
                kata,
                content='kata',
                content_rowid='rowid',
                tokenize='unicode61 remove_diacritics 1'
            )
        """)
        
        # Populate FTS table
        conn.execute("""
            INSERT INTO kata_fts(rowid, kata)
            SELECT rowid, kata FROM kata
        """)
        
        # Create triggers for consistency
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS kata_ai AFTER INSERT ON kata BEGIN
                INSERT INTO kata_fts(rowid, kata) VALUES (new.rowid, new.kata);
            END
        """)
        
        conn.commit()
        logger.info('FTS5 index created successfully')
    
    def _ensure_bloom_initialized(self) -> None:
        """Lazily initialize bloom filter."""
        if self._bloom_cache.initialized:
            return
        
        conn = self._get_connection()
        cursor = conn.execute("""
            SELECT kata FROM kata
            WHERE LENGTH(kata) >= 3
            ORDER BY frequency DESC
            LIMIT 500000
        """)
        
        words = [row[0] for row in cursor.fetchall()]
        self._bloom_cache.initialize(words)
    
    def check_word(self, word: str) -> bool:
        """
        Check if a word is in KBBI dictionary.
        Uses Bloom filter for fast negative lookup.
        
        Args:
            word: Word to check
            
        Returns:
            bool: True if word is found in dictionary
        """
        word_lower = word.lower().strip()
        
        # Check cache first
        if word_lower in self._query_cache:
            return self._query_cache[word_lower]
        
        # Bloom filter check (fast negative)
        self._ensure_bloom_initialized()
        if not self._bloom_cache.might_contain(word_lower):
            self._update_cache(word_lower, False)
            return False
        
        # FTS5 exact match
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT 1 FROM kata WHERE kata = ? LIMIT 1",
            (word_lower,)
        )
        
        is_found = cursor.fetchone() is not None
        self._update_cache(word_lower, is_found)
        
        return is_found
    
    def _update_cache(self, word: str, result: bool) -> None:
        """Update LRU cache with bounded size."""
        if len(self._query_cache) >= self._cache_max_size:
            # Simple cache eviction (FIFO)
            keys_to_remove = list(self._query_cache.keys())[:100]
            for key in keys_to_remove:
                del self._query_cache[key]
        
        self._query_cache[word] = result
    
    def check_text(self, text: str, batch_size: int = 1000) -> List[Tuple[str, bool, List[str]]]:
        """
        Check spelling for entire text.
        
        Args:
            text: Text to check
            batch_size: Batch size for processing
            
        Returns:
            List of (word, is_correct, suggestions) tuples
        """
        # Tokenize Indonesian text
        words = re.findall(r'\b[\w\']+\b', text, re.UNICODE)
        words = [w for w in words if len(w) >= 2]  # Skip single chars
        unique_words = list(dict.fromkeys(words))  # Preserve order
        
        results = {}
        
        # Batch processing
        for i in range(0, len(unique_words), batch_size):
            batch = unique_words[i:i + batch_size]
            batch_results = self._batch_check(batch)
            results.update(batch_results)
        
        # Return in original order with suggestions
        output = []
        for word in words:
            word_lower = word.lower()
            if word_lower not in results:
                results[word_lower] = (False, [])
            
            is_correct, suggestions = results[word_lower]
            output.append((word, is_correct, suggestions))
        
        return output
    
    def _batch_check(self, words: List[str]) -> dict:
        """Batch check multiple words efficiently."""
        conn = self._get_connection()
        
        placeholders = ','.join('?' * len(words))
        query = f"""
            SELECT kata FROM kata
            WHERE kata IN ({placeholders})
        """
        
        cursor = conn.execute(query, [w.lower() for w in words])
        found_words = {row[0] for row in cursor.fetchall()}
        
        results = {}
        for word in words:
            word_lower = word.lower()
            is_correct = word_lower in found_words
            
            if is_correct:
                results[word_lower] = (True, [])
            else:
                suggestions = self.get_suggestions(word_lower)
                results[word_lower] = (False, suggestions[:5])  # Top 5
        
        return results
    
    def get_suggestions(self, word: str, max_suggestions: int = 5) -> List[str]:
        """Get spelling suggestions using Levenshtein distance."""
        conn = self._get_connection()
        
        # Use FTS5 for prefix matching + similarity
        try:
            cursor = conn.execute("""
                SELECT kata FROM kata
                WHERE kata_fts MATCH ?
                ORDER BY length(kata) - length(?) ABS
                LIMIT ?
            """, (f'"{word}"*', word, max_suggestions * 3))
            
            candidates = [row[0] for row in cursor.fetchall()]
        except Exception:
            # Fallback if FTS5 not available
            cursor = conn.execute("""
                SELECT kata FROM kata
                WHERE kata LIKE ?
                LIMIT ?
            """, (f'{word[:3]}%', max_suggestions * 3))
            candidates = [row[0] for row in cursor.fetchall()]
        
        # Calculate Levenshtein distance for ranking
        scored = []
        for candidate in candidates:
            distance = self._levenshtein_distance(word.lower(), candidate.lower())
            if distance <= 3:  # Max edit distance
                scored.append((distance, candidate))
        
        scored.sort(key=lambda x: x[0])
        return [wd for _, wd in scored[:max_suggestions]]
    
    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return KBBISearcher._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def get_word_count(self) -> int:
        """
        Get total number of words in dictionary.
        
        Returns:
            int: Word count
        """
        return self._total_words
    
    def is_ready(self) -> bool:
        """
        Check if searcher is ready.
        
        Returns:
            bool: True if initialized
        """
        return self._indexed
    
    def close(self) -> None:
        """Close database connection."""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            logger.info('KBBI database connection closed')
