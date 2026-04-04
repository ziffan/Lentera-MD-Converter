"""
Spell Checker for Legal-MD-Converter.

Integrates KBBI dictionary with document preview for real-time
spell checking, suggestions, and Indonesian text processing.
"""

import logging
import re
import time
from pathlib import Path
from typing import Optional, List, Tuple, Dict

from PySide6.QtCore import QObject, Signal, QThread

from legal_md_converter.data.kbbi_searcher import KBBISearcher, KBBISuggestion
from legal_md_converter.data.asset_manager import AssetManager
from legal_md_converter.data.user_dictionary import UserDictionaryManager
from legal_md_converter.engine.spell_check_result import SpellCheckResult, TypoMatch
from legal_md_converter.engine.indonesian_text_processor import IndonesianTextProcessor


logger = logging.getLogger(__name__)


class SpellCheckEngine(QObject):
    """
    Spell checking engine with KBBI integration.
    
    Features:
    - Word-by-word spell checking
    - Text-wide spell checking with SpellCheckResult
    - Indonesian text processing (abbreviations, ordinals, diacritics)
    - User dictionary support
    - Suggestion generation
    - Highlight position tracking
    """
    
    # Signals
    check_complete = Signal(object)  # SpellCheckResult
    error_occurred = Signal(str)
    
    def __init__(self, db_path: Optional[Path] = None) -> None:
        super().__init__()
        
        self._searcher: Optional[KBBISearcher] = None
        self._text_processor = IndonesianTextProcessor()
        self._user_dict = UserDictionaryManager()
        self._highlight_cache: Dict[str, bool] = {}
        
        # Initialize searcher
        if db_path:
            self._searcher = KBBISearcher(db_path)
        else:
            # Try to get from asset manager
            try:
                asset_manager = AssetManager()
                db_path = asset_manager.get_kbbi_db_runtime_path()
                if db_path.exists():
                    self._searcher = KBBISearcher(db_path)
            except Exception as e:
                logger.warning(f'Could not initialize KBBI searcher: {e}')
    
    def check_document(self, doc, text: Optional[str] = None) -> SpellCheckResult:
        """
        Check entire document and return structured result.
        
        Args:
            doc: DocumentContent object or text string
            text: Optional text string (used if doc is not DocumentContent)
            
        Returns:
            SpellCheckResult: Complete spell check result
        """
        # Handle both DocumentContent and str for backward compatibility
        if hasattr(doc, 'raw_text'):
            # It's a DocumentContent
            text = doc.raw_text
            paragraphs = getattr(doc, 'paragraphs', [])
        else:
            # It's a string (backward compatibility)
            text = doc
            paragraphs = []
        
        start_time = time.time()
        
        try:
            # Tokenize with Indonesian processing
            words = self._text_processor.tokenize_legal_text(text)
            
            typos = []
            typo_words = set()
            
            # Build position map from paragraphs for page numbers
            para_position_map = []
            current_pos = 0
            for para in paragraphs:
                para_text = getattr(para, 'text', '')
                para_page = getattr(para, 'page_number', 0)
                para_position_map.append((current_pos, current_pos + len(para_text), para_page))
                current_pos += len(para_text) + 1  # +1 for newline
            
            for word in words:
                # Skip known patterns
                if self._text_processor.should_skip_word(word):
                    continue
                
                # Check user dictionary
                if self._user_dict.contains(word):
                    continue
                
                # Check KBBI
                is_correct = self.check_word(word)
                
                if not is_correct and word.lower() not in typo_words:
                    suggestions = self.get_suggestions(word)
                    pos = text.find(word)
                    context = self._get_context(text, pos)
                    
                    # Determine page number from paragraph position
                    page_number = 0
                    for start, end, page in para_position_map:
                        if start <= pos < end:
                            page_number = page
                            break
                    
                    typo = TypoMatch(
                        word=word,
                        start_pos=pos,
                        end_pos=pos + len(word),
                        suggestions=suggestions[:5],
                        context=context,
                        page_number=page_number,
                    )
                    typos.append(typo)
                    typo_words.add(word.lower())
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            result = SpellCheckResult(
                total_words=len(words),
                typo_count=len(typo_words),
                typos=typos,
                check_time_ms=elapsed_ms,
            )
            
            self.check_complete.emit(result)
            logger.info(f'Document check: {result.summary()}')
            return result
        
        except Exception as e:
            logger.error(f'Document check error: {e}', exc_info=True)
            self.error_occurred.emit(str(e))
            return SpellCheckResult()
    
    def get_typos(self, text: str) -> List[TypoMatch]:
        """
        Get all typos in text with positions.
        
        Args:
            text: Text to check
            
        Returns:
            List[TypoMatch]: List of all typo matches
        """
        result = self.check_document(text)
        return result.typos
    
    def check_word(self, word: str) -> bool:
        """
        Check if a single word is correctly spelled.
        
        Args:
            word: Word to check
            
        Returns:
            bool: True if word is correct
        """
        if not self._searcher:
            logger.warning('KBBI searcher not available')
            return True
        
        return self._searcher.check_word(word)
    
    def check_text(self, text: str) -> List[Tuple[str, bool, List[str]]]:
        """
        Check spelling for entire text (legacy compatibility).
        
        Args:
            text: Text to check
            
        Returns:
            List of (word, is_correct, suggestions) tuples
        """
        result = self.check_document(text)
        return [
            (t.word, False, t.suggestions) for t in result.typos
        ]
    
    def get_suggestions(self, word: str, max_suggestions: int = 5) -> List[str]:
        """
        Get spelling suggestions for a word.
        
        Args:
            word: Misspelled word
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List[str]: Suggested corrections
        """
        if not self._searcher:
            return []
        
        return self._searcher.get_suggestions(word, max_suggestions)
    
    def get_error_positions(self, text: str) -> List[Tuple[int, int]]:
        """
        Get character positions of spelling errors in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (start, end) positions for errors
        """
        if not self._searcher:
            return []
        
        errors = []
        words = self._text_processor.tokenize_legal_text(text)
        
        for word in words:
            if self._text_processor.should_skip_word(word):
                continue
            
            if self._user_dict.contains(word):
                continue
            
            pos = text.find(word)
            if pos == -1:
                continue
            
            if not self._searcher.check_word(word):
                errors.append((pos, pos + len(word)))
        
        return errors
    
    def highlight_errors(self, text: str) -> str:
        """
        Highlight spelling errors in text with Markdown.
        
        Args:
            text: Text to process
            
        Returns:
            str: Text with errors highlighted using Markdown
        """
        if not self._searcher:
            return text
        
        words = self._text_processor.tokenize_legal_text(text)
        
        for word in words:
            if self._text_processor.should_skip_word(word):
                continue
            if self._user_dict.contains(word):
                continue
            if self._searcher.check_word(word):
                continue
            
            # Replace with strikethrough
            text = text.replace(word, f"~~{word}~~", 1)
        
        return text
    
    def add_to_user_dictionary(self, word: str) -> bool:
        """
        Add a word to the user dictionary.
        
        Args:
            word: Word to add
            
        Returns:
            bool: True if added
        """
        return self._user_dict.add_word(word)
    
    def remove_from_user_dictionary(self, word: str) -> bool:
        """
        Remove a word from the user dictionary.
        
        Args:
            word: Word to remove
            
        Returns:
            bool: True if removed
        """
        return self._user_dict.remove_word(word)
    
    def is_in_user_dictionary(self, word: str) -> bool:
        """Check if word is in user dictionary."""
        return self._user_dict.contains(word)
    
    def get_user_dictionary_words(self) -> List[str]:
        """Get all words in user dictionary."""
        return self._user_dict.get_all_words()
    
    def _get_context(self, text: str, pos: int, radius: int = 30) -> str:
        """
        Get surrounding text context for a position.
        
        Args:
            text: Full text
            pos: Character position
            radius: Characters before/after
            
        Returns:
            str: Context string
        """
        start = max(0, pos - radius)
        end = min(len(text), pos + radius)
        
        context = text[start:end]
        
        # Add ellipsis if truncated
        if start > 0:
            context = '...' + context
        if end < len(text):
            context = context + '...'
        
        return context
    
    def is_ready(self) -> bool:
        """
        Check if spell checker is ready.
        
        Returns:
            bool: True if KBBI searcher is available
        """
        return self._searcher is not None and self._searcher.is_ready()
    
    def close(self) -> None:
        """Close searcher resources."""
        if self._searcher:
            self._searcher.close()


class SpellCheckWorker(QThread):
    """
    QThread worker for non-blocking spellcheck.
    
    Usage:
        worker = SpellCheckWorker(searcher, text)
        worker.result_ready.connect(handle_results)
        worker.start()
    """
    
    progress = Signal(int)
    result_ready = Signal(list)
    error_occurred = Signal(str)
    
    def __init__(self, searcher: KBBISearcher, text: str):
        super().__init__()
        self.searcher = searcher
        self.text = text
    
    def run(self):
        try:
            results = self.searcher.check_text(self.text)
            self.result_ready.emit(results)
        except Exception as e:
            logger.error(f'Spell check worker error: {e}', exc_info=True)
            self.error_occurred.emit(str(e))
