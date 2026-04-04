"""
Spell Check Worker for Legal-MD-Converter.

QThread-based spellchecking with chunk-based processing for large documents.
"""

import logging
import time
from typing import Optional, List

from PySide6.QtCore import QThread, Signal

from legal_md_converter.data.kbbi_searcher import KBBISearcher
from legal_md_converter.engine.spell_check_result import SpellCheckResult, TypoMatch


logger = logging.getLogger(__name__)


class SpellCheckWorker(QThread):
    """
    QThread worker for non-blocking spell checking.
    
    Features:
    - Chunk-based processing for large documents
    - Progress reporting
    - Result caching
    - Cancel support
    
    Usage:
        worker = SpellCheckWorker(searcher, text)
        worker.progress.connect(on_progress)
        worker.result_ready.connect(on_result)
        worker.start()
    """
    
    # Signals
    progress = Signal(int, int)  # current_chunk, total_chunks
    result_ready = Signal(object)  # SpellCheckResult
    error_occurred = Signal(str)  # Error message
    
    # Chunk size for large document processing
    CHUNK_SIZE = 5000  # words per chunk
    
    def __init__(
        self,
        searcher: KBBISearcher,
        text: str,
        parent: Optional[QThread] = None
    ) -> None:
        super().__init__(parent)
        
        self._searcher = searcher
        self._text = text
        self._cancelled = False
        self._cache = {}  # Word -> (is_correct, suggestions)
    
    def run(self) -> None:
        """Execute spell checking in background thread."""
        start_time = time.time()
        
        try:
            import re
            
            # Tokenize
            words = re.findall(r'\b[\w\']+\b', self._text, re.UNICODE)
            words = [w for w in words if len(w) >= 2]
            
            if not words:
                result = SpellCheckResult(
                    total_words=0,
                    typo_count=0,
                    typos=[],
                    check_time_ms=0,
                )
                self.result_ready.emit(result)
                return
            
            total_words = len(words)
            unique_words = list(dict.fromkeys(words))  # Preserve order
            
            # Calculate chunks
            chunks = [
                unique_words[i:i + self.CHUNK_SIZE]
                for i in range(0, len(unique_words), self.CHUNK_SIZE)
            ]
            
            total_chunks = len(chunks)
            all_typos = []
            typo_set = set()  # Track unique typos
            
            for chunk_idx, chunk in enumerate(chunks):
                if self._cancelled:
                    logger.info('Spell check cancelled')
                    break
                
                self.progress.emit(chunk_idx + 1, total_chunks)
                
                # Process chunk
                chunk_typos = self._check_word_chunk(chunk, words)
                
                for typo in chunk_typos:
                    if typo.word.lower() not in typo_set:
                        all_typos.append(typo)
                        typo_set.add(typo.word.lower())
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            result = SpellCheckResult(
                total_words=total_words,
                typo_count=len(typo_set),
                typos=all_typos,
                check_time_ms=elapsed_ms,
            )
            
            if not self._cancelled:
                self.result_ready.emit(result)
                logger.info(
                    f'Spell check complete: {result.typo_count} typos in '
                    f'{result.check_time_ms:.0f}ms ({total_words} words)'
                )
        
        except Exception as e:
            logger.error(f'Spell check worker error: {e}', exc_info=True)
            self.error_occurred.emit(str(e))
    
    def _check_word_chunk(
        self,
        chunk: List[str],
        all_words: List[str]
    ) -> List[TypoMatch]:
        """
        Check a chunk of words for spelling errors.
        
        Args:
            chunk: Unique words to check
            all_words: All words in document (for position tracking)
            
        Returns:
            List of TypoMatch objects
        """
        typos = []
        
        for word in chunk:
            word_lower = word.lower()
            
            # Check cache
            if word_lower in self._cache:
                is_correct, suggestions = self._cache[word_lower]
            else:
                is_correct = self._searcher.check_word(word)
                suggestions = (
                    self._searcher.get_suggestions(word_lower)
                    if not is_correct else []
                )
                self._cache[word_lower] = (is_correct, suggestions)
            
            if not is_correct:
                # Find position in text
                pos = self._find_word_position(word, all_words)
                context = self._get_context(word, all_words)
                
                typos.append(TypoMatch(
                    word=word,
                    start_pos=pos,
                    end_pos=pos + len(word),
                    suggestions=suggestions[:5],
                    context=context,
                ))
        
        return typos
    
    def _find_word_position(self, word: str, all_words: List[str]) -> int:
        """
        Find the actual character position of a word in the original text.

        Args:
            word: Word to find
            all_words: List of all words (unused, kept for API compatibility)

        Returns:
            int: Character start position of the word in self._text, or 0
        """
        import re
        pattern = r'\b' + re.escape(word) + r'\b'
        match = re.search(pattern, self._text, re.IGNORECASE)
        return match.start() if match else 0
    
    def _get_context(self, word: str, all_words: List[str], radius: int = 3) -> str:
        """
        Get surrounding context for a word.
        
        Args:
            word: Target word
            all_words: All words in document
            radius: Number of words before/after
            
        Returns:
            str: Context string
        """
        target_lower = word.lower()
        
        for i, w in enumerate(all_words):
            if w.lower() == target_lower:
                start = max(0, i - radius)
                end = min(len(all_words), i + radius + 1)
                context_words = all_words[start:end]
                return ' '.join(context_words)
        
        return ""
    
    def cancel(self) -> None:
        """Request cancellation."""
        self._cancelled = True
        logger.info('Spell check cancellation requested')
    
    def is_cancelled(self) -> bool:
        """Check if cancelled."""
        return self._cancelled
    
    def get_cache_size(self) -> int:
        """Get number of cached word lookups."""
        return len(self._cache)
