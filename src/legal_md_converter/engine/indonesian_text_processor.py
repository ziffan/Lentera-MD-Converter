"""
Indonesian Text Processor for Legal-MD-Converter.

Handles Indonesian-specific text processing rules for spell checking:
- Common abbreviations
- Ordinal numbers
- Diacritics normalization
- Proper noun detection
- Affix handling
"""

import re
import logging
from typing import List, Set, Tuple


logger = logging.getLogger(__name__)


# Common Indonesian legal abbreviations
INDONESIAN_ABBREVIATIONS = {
    'hlm', 'dst', 'dll', 'dsb', 'dr', 'thn', 'no', 'ttg', 'dgn', 'utk',
    'yg', 'pd', 'dlm', 'atas', 'kepada', 'dari', 'oleh', 'sbgn', 'tsb',
    'ttg', 'yg', 'krn', 'utk', 'dgn', 'jg', 'tp', 'blm', 'sdh', 'tlh',
    'ps', 'pasal', 'ayat', 'uu', 'pp', 'perpu', 'keppres', 'kepmen',
    'skb', 'sk', 'tgl', 'tgl', 'jln', 'jl', 'rt', 'rw', 'kel', 'kec',
    'kab', 'kota', 'prov', 'nkri', 'uhd', 'mkg', 'hrs', 'bkn', 'dpt',
}

# Indonesian ordinal patterns
ORDINAL_PATTERNS = [
    re.compile(r'\bke-\d+\b'),       # ke-1, ke-2, etc.
    re.compile(r'\bke\s+\d+\b'),     # ke 1, ke 2
]

# Indonesian diacritics map
DIACRITICS_MAP = {
    'é': 'e',
    'ë': 'e',
    'á': 'a',
    'í': 'i',
    'ó': 'o',
    'ú': 'u',
}


class IndonesianTextProcessor:
    """
    Processes Indonesian text for spell checking optimization.
    
    Handles:
    - Abbreviation recognition
    - Ordinal number detection
    - Diacritics normalization
    - Compound word splitting
    - Proper noun detection
    """
    
    def __init__(self) -> None:
        """Initialize the processor."""
        self._abbreviations = INDONESIAN_ABBREVIATIONS.copy()
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize Indonesian text (diacritics, whitespace).
        
        Args:
            text: Input text
            
        Returns:
            str: Normalized text
        """
        # Normalize diacritics
        for diacritic, replacement in DIACRITICS_MAP.items():
            text = text.replace(diacritic, replacement)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def is_abbreviation(self, word: str) -> bool:
        """
        Check if a word is a recognized Indonesian abbreviation.
        
        Args:
            word: Word to check
            
        Returns:
            bool: True if recognized abbreviation
        """
        return word.lower().rstrip('.') in self._abbreviations
    
    def is_ordinal(self, word: str) -> bool:
        """
        Check if a word is an Indonesian ordinal number.
        
        Args:
            word: Word to check
            
        Returns:
            bool: True if ordinal number
        """
        for pattern in ORDINAL_PATTERNS:
            if pattern.match(word.lower()):
                return True
        return False
    
    def is_proper_noun(self, word: str) -> bool:
        """
        Heuristic check if word might be a proper noun.
        
        Args:
            word: Word to check
            
        Returns:
            bool: True if likely a proper noun
        """
        # Starts with capital and contains capital
        if word[0].isupper() and any(c.isupper() for c in word[1:]):
            return True
        
        # Common legal document proper nouns
        legal_proper = {
            'Mahkamah', 'Konstitusi', 'Negeri', 'Republik', 'Indonesia',
            'Presiden', 'Menteri', 'Dewan', 'Perwakilan', 'Rakyat',
        }
        
        return word in legal_proper
    
    def should_skip_word(self, word: str) -> bool:
        """
        Check if a word should be skipped during spell checking.
        
        Args:
            word: Word to check
            
        Returns:
            bool: True if word should be skipped
        """
        word_clean = word.strip().lower()
        
        # Skip numbers
        if word.isdigit():
            return True
        
        # Skip abbreviations
        if self.is_abbreviation(word_clean):
            return True
        
        # Skip ordinals
        if self.is_ordinal(word_clean):
            return True
        
        # Skip mixed alphanumeric (article references like "Pasal 12A")
        if re.match(r'^[a-z]+\d+[a-z]?$', word_clean, re.IGNORECASE):
            return True
        
        # Skip very short words (particles)
        if len(word_clean) <= 2:
            return True
        
        return False
    
    def extract_compound_parts(self, word: str) -> List[str]:
        """
        Attempt to split compound Indonesian words.
        
        Common prefixes: ber-, me-, di-, ter-, pe-, per-, se-, ke-
        Common suffixes: -kan, -an, -i, -lah, -kah, -pun, -nya
        
        Args:
            word: Compound word
            
        Returns:
            List[str]: Possible root word parts
        """
        parts = []
        word_lower = word.lower()
        
        # Common prefixes
        prefixes = ['ber', 'me', 'di', 'ter', 'pe', 'per', 'se', 'ke', 'meng', 'peng']
        # Common suffixes
        suffixes = ['kan', 'an', 'i', 'lah', 'kah', 'pun', 'nya', 'wan', 'wati']
        
        for prefix in prefixes:
            if word_lower.startswith(prefix) and len(word_lower) > len(prefix) + 2:
                root = word_lower[len(prefix):]
                parts.append(root)
                
                # Try removing suffix too
                for suffix in suffixes:
                    if root.endswith(suffix) and len(root) > len(suffix) + 1:
                        parts.append(root[:-len(suffix)])
        
        return parts
    
    def tokenize_legal_text(self, text: str) -> List[str]:
        """
        Tokenize Indonesian legal text with special handling.
        
        Args:
            text: Legal document text
            
        Returns:
            List[str]: Tokenized words
        """
        # Normalize
        text = self.normalize_text(text)
        
        # Extract tokens
        tokens = re.findall(r'\b[\w\']+\b', text, re.UNICODE)
        
        # Filter out very short tokens but keep meaningful ones
        tokens = [t for t in tokens if len(t) >= 2]
        
        return tokens
    
    def get_skip_reason(self, word: str) -> str:
        """
        Get reason why a word would be skipped.
        
        Args:
            word: Word to check
            
        Returns:
            str: Skip reason or empty string if not skipped
        """
        if word.isdigit():
            return "angka"
        if self.is_abbreviation(word):
            return "singkatan"
        if self.is_ordinal(word):
            return "bilangan tingkat"
        if len(word) <= 2:
            return "partikel"
        if re.match(r'^[a-z]+\d+[a-z]?$', word.lower()):
            return "referensi pasal"
        
        return ""
