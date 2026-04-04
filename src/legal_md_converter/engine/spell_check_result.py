"""
Spell Check Result data classes for Legal-MD-Converter.

Defines structured result types for spell checking operations.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TypoMatch:
    """
    Represents a single spelling error with context.
    
    Attributes:
        word: The misspelled word as it appears in text
        start_pos: Character position where word starts
        end_pos: Character position where word ends
        suggestions: List of suggested corrections from KBBI
        page_number: Page number where error was found (0 for non-paginated)
        context: Surrounding text for user context
    """
    word: str
    start_pos: int
    end_pos: int
    suggestions: List[str] = field(default_factory=list)
    page_number: int = 0
    context: str = ""
    
    @property
    def display_text(self) -> str:
        """Get formatted display text for UI."""
        if self.suggestions:
            return f"{self.word} → {self.suggestions[0]}"
        return self.word
    
    def matches_position(self, pos: int) -> bool:
        """Check if a character position falls within this typo."""
        return self.start_pos <= pos < self.end_pos


@dataclass
class SpellCheckResult:
    """
    Complete result from a spell check operation.
    
    Attributes:
        total_words: Total number of words checked
        typo_count: Number of unique typos found
        typos: List of all typo matches
        is_clean: True if no typos found
        check_time_ms: Time taken to perform check in milliseconds
    """
    total_words: int = 0
    typo_count: int = 0
    typos: List[TypoMatch] = field(default_factory=list)
    check_time_ms: float = 0.0
    
    @property
    def is_clean(self) -> bool:
        """Check if document has no typos."""
        return self.typo_count == 0
    
    @property
    def accuracy(self) -> float:
        """Calculate spelling accuracy percentage."""
        if self.total_words == 0:
            return 100.0
        correct = self.total_words - self.typo_count
        return max(0.0, (correct / self.total_words) * 100)
    
    def get_unique_words(self) -> List[str]:
        """Get list of unique misspelled words."""
        return list(dict.fromkeys(t.word for t in self.typos))
    
    def get_typos_for_page(self, page_number: int) -> List[TypoMatch]:
        """Get typos for a specific page."""
        return [t for t in self.typos if t.page_number == page_number]
    
    def summary(self) -> str:
        """Get human-readable summary."""
        if self.is_clean:
            return f"✓ Tidak ada kesalahan ejaan ({self.total_words} kata)"
        return (
            f"✗ Ditemukan {self.typo_count} kesalahan dari {self.total_words} kata "
            f"(akurasi: {self.accuracy:.1f}%)"
        )
