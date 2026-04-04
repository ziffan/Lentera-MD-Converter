"""
User Dictionary Manager for Legal-MD-Converter.

Manages user-added words that should be excluded from spell checking.
Persists across sessions using SQLite.
"""

import logging
import sqlite3
from pathlib import Path
from typing import List, Optional, Set


logger = logging.getLogger(__name__)


class UserDictionaryManager:
    """
    Manages user-added words for spell checking.
    
    Features:
    - SQLite-based persistence
    - Add/remove words
    - Batch operations
    - Import/export
    """
    
    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialize user dictionary.
        
        Args:
            db_path: Path to user dictionary database.
                     Defaults to platform-specific location.
        """
        if db_path is None:
            # Default location
            import platform
            system = platform.system()
            
            if system == "Windows":
                import os
                base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
            elif system == "Darwin":
                base = Path.home() / 'Library' / 'Application Support'
            else:
                base = Path.home() / '.local' / 'share'
            
            db_path = base / 'legal_md_converter' / 'user_dictionary.db'
        
        self._db_path = db_path
        self._cache: Set[str] = set()
        
        self._initialize()
    
    def _initialize(self) -> None:
        """Create database and tables if needed."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self._db_path))
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_words (
                word TEXT PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 1
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_words_lower
            ON user_words(LOWER(word))
        """)
        
        conn.commit()
        
        # Load cache
        cursor = conn.execute("SELECT word FROM user_words")
        self._cache = {row[0].lower() for row in cursor.fetchall()}
        conn.close()
        
        logger.info(f'User dictionary initialized: {len(self._cache)} words')
    
    def add_word(self, word: str) -> bool:
        """
        Add a word to user dictionary.
        
        Args:
            word: Word to add
            
        Returns:
            bool: True if added, False if already exists
        """
        word_lower = word.lower()
        
        if word_lower in self._cache:
            return False
        
        self._cache.add(word_lower)
        
        try:
            conn = sqlite3.connect(str(self._db_path))
            conn.execute(
                "INSERT OR IGNORE INTO user_words (word) VALUES (?)",
                (word_lower,)
            )
            conn.commit()
            conn.close()
            logger.debug(f'Added word to user dictionary: {word_lower}')
            return True
        except Exception as e:
            logger.error(f'Failed to add word: {e}')
            return False
    
    def remove_word(self, word: str) -> bool:
        """
        Remove a word from user dictionary.
        
        Args:
            word: Word to remove
            
        Returns:
            bool: True if removed
        """
        word_lower = word.lower()
        
        if word_lower not in self._cache:
            return False
        
        self._cache.discard(word_lower)
        
        try:
            conn = sqlite3.connect(str(self._db_path))
            conn.execute(
                "DELETE FROM user_words WHERE LOWER(word) = ?",
                (word_lower,)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f'Failed to remove word: {e}')
            return False
    
    def contains(self, word: str) -> bool:
        """
        Check if word is in user dictionary.
        
        Args:
            word: Word to check
            
        Returns:
            bool: True if word is in user dictionary
        """
        return word.lower() in self._cache
    
    def get_all_words(self) -> List[str]:
        """
        Get all words in user dictionary.
        
        Returns:
            List[str]: Sorted list of words
        """
        return sorted(self._cache)
    
    def word_count(self) -> int:
        """Get number of words in user dictionary."""
        return len(self._cache)
    
    def add_batch(self, words: List[str]) -> int:
        """
        Add multiple words at once.
        
        Args:
            words: Words to add
            
        Returns:
            int: Number of words added
        """
        added = 0
        
        conn = sqlite3.connect(str(self._db_path))
        
        for word in words:
            word_lower = word.lower()
            if word_lower not in self._cache:
                self._cache.add(word_lower)
                conn.execute(
                    "INSERT OR IGNORE INTO user_words (word) VALUES (?)",
                    (word_lower,)
                )
                added += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f'Added {added} words to user dictionary')
        return added
    
    def export_words(self, output_path: Path) -> bool:
        """
        Export user dictionary to text file.
        
        Args:
            output_path: Path to output file
            
        Returns:
            bool: True if successful
        """
        try:
            words = self.get_all_words()
            output_path.write_text('\n'.join(words), encoding='utf-8')
            logger.info(f'Exported {len(words)} words to {output_path}')
            return True
        except Exception as e:
            logger.error(f'Failed to export words: {e}')
            return False
    
    def import_words(self, input_path: Path) -> int:
        """
        Import words from text file.
        
        Args:
            input_path: Path to input file (one word per line)
            
        Returns:
            int: Number of words imported
        """
        try:
            words = input_path.read_text(encoding='utf-8').splitlines()
            words = [w.strip() for w in words if w.strip()]
            added = self.add_batch(words)
            logger.info(f'Imported {added} words from {input_path}')
            return added
        except Exception as e:
            logger.error(f'Failed to import words: {e}')
            return 0
    
    def clear(self) -> int:
        """
        Clear all words from user dictionary.
        
        Returns:
            int: Number of words removed
        """
        count = len(self._cache)
        
        try:
            conn = sqlite3.connect(str(self._db_path))
            conn.execute("DELETE FROM user_words")
            conn.commit()
            conn.close()
            
            self._cache.clear()
            logger.info(f'Cleared {count} words from user dictionary')
            return count
        except Exception as e:
            logger.error(f'Failed to clear user dictionary: {e}')
            return 0
