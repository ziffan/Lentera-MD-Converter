"""Tests for Lentera MD UI components."""

import pytest
from pathlib import Path


@pytest.fixture
def app(qtbot):
    """Create a QApplication instance for testing."""
    from PySide6.QtWidgets import QApplication
    import sys
    
    # Ensure only one QApplication instance
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
    return app


def test_main_window_creation(app):
    """Test that main window can be created."""
    from legal_md_converter.ui.main_window import MainWindow
    
    window = MainWindow()
    assert window is not None
    assert window.windowTitle() == 'Lentera MD'
    assert window.isVisible() == False


def test_file_drop_widget_creation(app):
    """Test that file drop widget can be created."""
    from legal_md_converter.ui.widgets.file_drop_widget import FileDropWidget
    
    widget = FileDropWidget()
    assert widget is not None
    assert widget.file_count() == 0


def test_document_preview_creation(app):
    """Test that document preview can be created."""
    from legal_md_converter.ui.widgets.document_preview import DocumentPreview
    
    preview = DocumentPreview()
    assert preview is not None


def test_app_theme_stylesheet(app):
    """Test that app theme generates valid stylesheet."""
    from legal_md_converter.ui.styles.app_theme import AppTheme
    
    stylesheet = AppTheme.get_main_stylesheet()
    assert isinstance(stylesheet, str)
    assert len(stylesheet) > 0
    assert 'QMainWindow' in stylesheet


def test_file_drop_add_files(app):
    """Test adding files to the file drop widget."""
    from legal_md_converter.ui.widgets.file_drop_widget import FileDropWidget
    
    widget = FileDropWidget()
    
    # Create a temporary test file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b'Test content')
        test_file = f.name
    
    try:
        widget.add_files([test_file])
        assert widget.file_count() == 1
        assert test_file in widget.get_files()
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_file_drop_clear_files(app):
    """Test clearing files from the file drop widget."""
    from legal_md_converter.ui.widgets.file_drop_widget import FileDropWidget
    
    widget = FileDropWidget()
    
    # Create a temporary test file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b'Test content')
        test_file = f.name
    
    try:
        widget.add_files([test_file])
        assert widget.file_count() == 1
        
        widget.clear_files()
        assert widget.file_count() == 0
        assert len(widget.get_files()) == 0
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_document_preview_set_content(app):
    """Test setting content in document preview."""
    from legal_md_converter.ui.widgets.document_preview import DocumentPreview
    
    preview = DocumentPreview()
    test_markdown = '# Test Document\n\nThis is a test.'
    
    preview.set_content(test_markdown, 'test.md')
    assert preview.get_current_markdown() == test_markdown


def test_document_preview_clear(app):
    """Test clearing document preview."""
    from legal_md_converter.ui.widgets.document_preview import DocumentPreview
    
    preview = DocumentPreview()
    preview.set_content('# Test', 'test.md')
    preview.clear_preview()
    
    assert preview.get_current_markdown() == ''


def test_app_theme_button_style(app):
    """Test generating button styles."""
    from legal_md_converter.ui.styles.app_theme import AppTheme
    
    primary_style = AppTheme.get_button_style('primary')
    assert isinstance(primary_style, str)
    assert len(primary_style) > 0
    
    secondary_style = AppTheme.get_button_style('secondary')
    assert isinstance(secondary_style, str)
    assert secondary_style != primary_style
