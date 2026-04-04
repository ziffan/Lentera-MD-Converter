"""Tests for Phase 3 - KBBI Spellcheck Integration."""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def app(qtbot):
    """Create a QApplication instance for testing."""
    from PySide6.QtWidgets import QApplication
    import sys
    
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
    return app


@pytest.fixture
def sample_indonesian_text():
    """Sample Indonesian legal text for testing."""
    return (
        "Mahkamah Konstitusi Republik Indonesia\n\n"
        "Putusan Nomor 123/PUU/2024\n\n"
        "Demi Keadilan Yang Berkeadilan\n\n"
        "Menimbang bahwa untuk melaksanakan ketentuan Pasal 10 Undang-Undang "
        "Nomor 24 Tahun 2003 tentang Mahkamah Konstitusi, perlu menetapkan "
        "Peraturan Mahkamah Konstitusi tentang Pedoman Beracara.\n\n"
        "Mengingat:\n"
        "1. Undang-Undang Dasar Negara Republik Indonesia Tahun 1945;\n"
        "2. Undang-Undang Nomor 24 Tahun 2003 tentang Mahkamah Konstitusi;\n\n"
        "Memperhatikan hasil sidang Mahkamah Konstitusi;\n\n"
        "MEMUTUSKAN:\n\n"
        "Menetapkan: PERATURAN MAHKAMAH KONSTITUSI TENTANG PEDOMAN BERACARA."
    )


# SpellCheckResult Tests

def test_typo_match_creation(app):
    """Test TypoMatch dataclass creation."""
    from legal_md_converter.engine.spell_check_result import TypoMatch
    
    typo = TypoMatch(
        word="konstitusii",
        start_pos=100,
        end_pos=113,
        suggestions=["konstitusi"],
        page_number=1,
        context="tentang Mahkamah Konstitusii tentang"
    )
    
    assert typo.word == "konstitusii"
    assert typo.start_pos == 100
    assert typo.end_pos == 113
    assert len(typo.suggestions) == 1
    assert typo.page_number == 1


def test_typo_match_display_text(app):
    """Test TypoMatch display text formatting."""
    from legal_md_converter.engine.spell_check_result import TypoMatch
    
    # With suggestions
    typo = TypoMatch(word="salah", start_pos=0, end_pos=5, suggestions=["benar"])
    assert typo.display_text == "salah → benar"
    
    # Without suggestions
    typo = TypoMatch(word="xyz", start_pos=0, end_pos=3)
    assert typo.display_text == "xyz"


def test_typo_match_position(app):
    """Test TypoMatch position matching."""
    from legal_md_converter.engine.spell_check_result import TypoMatch
    
    typo = TypoMatch(word="test", start_pos=10, end_pos=14)
    assert typo.matches_position(10)
    assert typo.matches_position(12)
    assert typo.matches_position(13)
    assert not typo.matches_position(9)
    assert not typo.matches_position(14)


def test_spell_check_result_creation(app):
    """Test SpellCheckResult creation."""
    from legal_md_converter.engine.spell_check_result import SpellCheckResult, TypoMatch
    
    typos = [
        TypoMatch(word="salah", start_pos=0, end_pos=5, suggestions=["benar"]),
    ]
    
    result = SpellCheckResult(
        total_words=100,
        typo_count=1,
        typos=typos,
        check_time_ms=150.5,
    )
    
    assert result.total_words == 100
    assert result.typo_count == 1
    assert not result.is_clean
    assert result.check_time_ms == 150.5


def test_spell_check_result_accuracy(app):
    """Test accuracy calculation."""
    from legal_md_converter.engine.spell_check_result import SpellCheckResult
    
    # Perfect accuracy
    result = SpellCheckResult(total_words=100, typo_count=0)
    assert result.accuracy == 100.0
    
    # 95% accuracy
    result = SpellCheckResult(total_words=100, typo_count=5)
    assert result.accuracy == 95.0
    
    # Zero words
    result = SpellCheckResult(total_words=0, typo_count=0)
    assert result.accuracy == 100.0


def test_spell_check_result_summary(app):
    """Test human-readable summary."""
    from legal_md_converter.engine.spell_check_result import SpellCheckResult
    
    # Clean document
    result = SpellCheckResult(total_words=50, typo_count=0)
    summary = result.summary()
    assert "✓" in summary
    assert "50" in summary
    
    # Document with errors
    result = SpellCheckResult(total_words=100, typo_count=5)
    summary = result.summary()
    assert "✗" in summary
    assert "5" in summary


def test_spell_check_result_unique_words(app):
    """Test unique word extraction."""
    from legal_md_converter.engine.spell_check_result import SpellCheckResult, TypoMatch
    
    typos = [
        TypoMatch(word="salah", start_pos=0, end_pos=5),
        TypoMatch(word="salah", start_pos=20, end_pos=25),  # Duplicate
        TypoMatch(word="lain", start_pos=30, end_pos=34),
    ]
    
    result = SpellCheckResult(total_words=100, typo_count=2, typos=typos)
    unique = result.get_unique_words()
    
    assert len(unique) == 2
    assert "salah" in unique
    assert "lain" in unique


# Indonesian Text Processor Tests

def test_indonesian_text_processor_normalization(app):
    """Test text normalization."""
    from legal_md_converter.engine.indonesian_text_processor import IndonesianTextProcessor
    
    processor = IndonesianTextProcessor()
    
    # Diacritics normalization
    assert processor.normalize_text("kafeé") == "kafee"
    
    # Whitespace normalization
    assert processor.normalize_text("hello   world") == "hello world"


def test_indonesian_abbreviation_detection(app):
    """Test abbreviation recognition."""
    from legal_md_converter.engine.indonesian_text_processor import IndonesianTextProcessor
    
    processor = IndonesianTextProcessor()
    
    assert processor.is_abbreviation("hlm")
    assert processor.is_abbreviation("dst")
    assert processor.is_abbreviation("dll")
    assert processor.is_abbreviation("yg")
    assert not processor.is_abbreviation("mahkamah")


def test_indonesian_ordinal_detection(app):
    """Test ordinal number recognition."""
    from legal_md_converter.engine.indonesian_text_processor import IndonesianTextProcessor
    
    processor = IndonesianTextProcessor()
    
    assert processor.is_ordinal("ke-1")
    assert processor.is_ordinal("ke-2")
    assert processor.is_ordinal("ke 3")
    assert not processor.is_ordinal("pertama")


def test_indonesian_skip_word(app):
    """Test word skip logic."""
    from legal_md_converter.engine.indonesian_text_processor import IndonesianTextProcessor
    
    processor = IndonesianTextProcessor()
    
    # Should skip
    assert processor.should_skip_word("123")
    assert processor.should_skip_word("hlm")
    assert processor.should_skip_word("ke-1")
    assert processor.should_skip_word("di")
    assert processor.should_skip_word("ps12a")
    
    # Should not skip
    assert not processor.should_skip_word("mahkamah")
    assert not processor.should_skip_word("konstitusi")


def test_indonesian_tokenizer(app, sample_indonesian_text):
    """Test legal text tokenization."""
    from legal_md_converter.engine.indonesian_text_processor import IndonesianTextProcessor
    
    processor = IndonesianTextProcessor()
    tokens = processor.tokenize_legal_text(sample_indonesian_text)
    
    assert len(tokens) > 0
    assert "Mahkamah" in tokens
    assert "Konstitusi" in tokens


# User Dictionary Tests

def test_user_dictionary_creation(app):
    """Test user dictionary initialization."""
    from legal_md_converter.data.user_dictionary import UserDictionaryManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_user_dict.db"
        manager = UserDictionaryManager(db_path)
        
        assert manager.word_count() == 0


def test_user_dictionary_add_remove(app):
    """Test adding and removing words."""
    from legal_md_converter.data.user_dictionary import UserDictionaryManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_user_dict.db"
        manager = UserDictionaryManager(db_path)
        
        # Add word
        assert manager.add_word("Undang-Undang")
        assert manager.contains("Undang-Undang")
        assert manager.word_count() == 1
        
        # Add duplicate
        assert not manager.add_word("Undang-Undang")
        assert manager.word_count() == 1
        
        # Remove word
        assert manager.remove_word("Undang-Undang")
        assert not manager.contains("Undang-Undang")
        assert manager.word_count() == 0


def test_user_dictionary_batch_add(app):
    """Test batch adding words."""
    from legal_md_converter.data.user_dictionary import UserDictionaryManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_user_dict.db"
        manager = UserDictionaryManager(db_path)
        
        words = ["kata1", "kata2", "kata3"]
        added = manager.add_batch(words)
        
        assert added == 3
        assert manager.word_count() == 3


def test_user_dictionary_export_import(app):
    """Test export and import functionality."""
    from legal_md_converter.data.user_dictionary import UserDictionaryManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_user_dict.db"
        export_path = Path(tmpdir) / "words.txt"
        import_path = Path(tmpdir) / "import_words.txt"
        
        # Create and add words
        manager1 = UserDictionaryManager(db_path)
        manager1.add_batch(["word1", "word2", "word3"])
        manager1.export_words(export_path)
        
        # Create new manager and import
        manager2 = UserDictionaryManager(Path(tmpdir) / "test2.db")
        
        # Write import file
        import_path.write_text("word4\nword5\nword6\n")
        imported = manager2.import_words(import_path)
        
        assert imported == 3
        assert manager2.word_count() == 3


# SpellCheckEngine Tests

def test_spell_check_engine_init(app):
    """Test SpellCheckEngine initialization."""
    from legal_md_converter.engine.spell_checker import SpellCheckEngine
    
    engine = SpellCheckEngine()
    assert engine is not None
    # Searcher may not be ready without KBBI database
    # But engine should still initialize


def test_spell_check_engine_indonesian_processing(app, sample_indonesian_text):
    """Test Indonesian text processing in spell check."""
    from legal_md_converter.engine.spell_checker import SpellCheckEngine
    
    engine = SpellCheckEngine()
    
    # Even without KBBI, should return result structure
    result = engine.check_document(sample_indonesian_text)
    
    assert result.total_words > 0
    assert isinstance(result.typos, list)
    assert result.check_time_ms >= 0


def test_spell_check_engine_user_dictionary_integration(app):
    """Test user dictionary integration in spell checker."""
    from legal_md_converter.engine.spell_checker import SpellCheckEngine
    
    engine = SpellCheckEngine()
    
    # Add word to user dictionary
    engine.add_to_user_dictionary("testword")
    assert engine.is_in_user_dictionary("testword")
    
    # Remove word
    engine.remove_from_user_dictionary("testword")
    assert not engine.is_in_user_dictionary("testword")


# SpellCheckWorker Tests

def test_spell_check_worker_creation(app):
    """Test SpellCheckWorker creation."""
    from legal_md_converter.engine.spell_check_worker import SpellCheckWorker
    from legal_md_converter.data.kbbi_searcher import KBBISearcher
    import tempfile
    
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        # Create searcher (will create empty DB)
        searcher = KBBISearcher(db_path)

        worker = SpellCheckWorker(searcher, "test text")
        assert worker is not None
        assert not worker.is_cancelled()

        # Test cancel
        worker.cancel()
        assert worker.is_cancelled()

        # Close DB connection before tempdir cleanup (Windows requires this)
        searcher.close()
