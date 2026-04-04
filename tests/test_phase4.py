"""Tests for Phase 4 - Markdown Export & Packaging."""

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
def sample_document_content():
    """Create sample DocumentContent for testing."""
    from legal_md_converter.engine.docling_parser import DocumentContent, Paragraph, Table
    
    paragraphs = [
        Paragraph(text="Pendahuluan", style="heading", level=1, page_number=1),
        Paragraph(text="Ini adalah dokumen hukum contoh.", style="normal", page_number=1),
        Paragraph(text="Pasal 1", style="heading", level=2, page_number=1),
        Paragraph(text="Setiap warga negara berhak mendapatkan perlindungan.", style="normal", page_number=2),
    ]
    
    tables = [
        Table(
            headers=["No", "Pasal", "Keterangan"],
            rows=[
                ["1", "Pasal 1", "Hak dasar"],
                ["2", "Pasal 2", "Kewajiban"],
            ],
            page_number=2,
        )
    ]
    
    metadata = {
        'source': '/path/to/document.pdf',
        'filename': 'document.pdf',
        'format': 'PDF',
        'pages': 2,
    }
    
    return DocumentContent(
        source_path=Path('/path/to/document.pdf'),
        title='Dokumen Hukum Contoh',
        paragraphs=paragraphs,
        tables=tables,
        metadata=metadata,
        raw_text='# Dokumen Hukum Contoh\n\nPendahuluan\n\nIni adalah dokumen hukum contoh.',
        word_count=15,
    )


# Template Loader Tests

def test_template_loader_init(app):
    """Test TemplateLoader initialization."""
    from legal_md_converter.engine.markdown_converter import TemplateLoader
    
    loader = TemplateLoader()
    assert loader is not None


def test_template_loader_available_templates(app):
    """Test that templates are loaded."""
    from legal_md_converter.engine.markdown_converter import TemplateLoader
    
    loader = TemplateLoader()
    templates = loader.get_available_templates()
    
    # Should have at least the templates we created
    assert 'legal' in templates or 'basic' in templates or 'academic' in templates


def test_template_loader_get_template(app):
    """Test getting a specific template."""
    from legal_md_converter.engine.markdown_converter import TemplateLoader
    
    loader = TemplateLoader()
    
    # At least one template should be available
    templates = loader.get_available_templates()
    if templates:
        template = loader.get_template(templates[0])
        assert template is not None
        assert len(template) > 0


# Markdown Exporter Tests

def test_markdown_exporter_basic(app, sample_document_content):
    """Test basic markdown export."""
    from legal_md_converter.engine.markdown_converter import MarkdownExporter
    
    exporter = MarkdownExporter()
    markdown = exporter.to_markdown(sample_document_content)
    
    assert isinstance(markdown, str)
    assert len(markdown) > 0
    assert 'Dokumen Hukum Contoh' in markdown


def test_markdown_exporter_with_template(app, sample_document_content):
    """Test markdown export with template."""
    from legal_md_converter.engine.markdown_converter import MarkdownExporter
    
    exporter = MarkdownExporter()
    
    # Try each available template
    templates = exporter._template_loader.get_available_templates()
    
    for template in templates:
        markdown = exporter.to_markdown(sample_document_content, template=template)
        assert isinstance(markdown, str)
        assert len(markdown) > 0


def test_markdown_exporter_save_file(app, sample_document_content):
    """Test saving markdown to file."""
    from legal_md_converter.engine.markdown_converter import MarkdownExporter
    
    exporter = MarkdownExporter()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / 'output.md'
        success = exporter.save_file(sample_document_content, output_path)
        
        assert success
        assert output_path.exists()
        
        content = output_path.read_text(encoding='utf-8')
        assert 'Dokumen Hukum Contoh' in content


# Markdown Preview Widget Tests

def test_markdown_preview_creation(app):
    """Test MarkdownPreview widget creation."""
    from legal_md_converter.ui.widgets.markdown_preview import MarkdownPreview
    
    preview = MarkdownPreview()
    assert preview is not None
    assert preview.get_content() == ""


def test_markdown_preview_set_content(app):
    """Test setting content in MarkdownPreview."""
    from legal_md_converter.ui.widgets.markdown_preview import MarkdownPreview
    
    preview = MarkdownPreview()
    test_markdown = '# Test\n\nThis is a test.'
    
    preview.set_content(test_markdown, 'Test Doc')
    
    assert preview.get_content() == test_markdown
    assert preview.word_count_label.text() == '5 kata'


def test_markdown_preview_clear(app):
    """Test clearing MarkdownPreview."""
    from legal_md_converter.ui.widgets.markdown_preview import MarkdownPreview
    
    preview = MarkdownPreview()
    preview.set_content('# Test', 'Test')
    preview.clear_preview()
    
    assert preview.get_content() == ""


# Template File Tests

def test_template_files_exist():
    """Test that template files exist."""
    template_dir = Path(__file__).parent.parent / 'assets' / 'templates'
    
    assert (template_dir / 'legal.md').exists()
    assert (template_dir / 'basic.md').exists()
    assert (template_dir / 'academic.md').exists()


def test_template_file_content():
    """Test template files have valid content."""
    template_dir = Path(__file__).parent.parent / 'assets' / 'templates'
    
    for template_file in template_dir.glob('*.md'):
        content = template_file.read_text(encoding='utf-8')
        assert len(content) > 0
        # Should have template variables
        assert '{{' in content and '}}' in content


# Build Script Tests

def test_build_app_py_exists():
    """Test that build script exists."""
    build_script = Path(__file__).parent.parent / 'build_app.py'
    assert build_script.exists()


def test_build_app_syntax():
    """Test that build script has valid Python syntax."""
    import ast
    
    build_script = Path(__file__).parent.parent / 'build_app.py'
    source = build_script.read_text(encoding='utf-8')
    
    # Should parse without errors
    ast.parse(source)


# Packaging Configuration Tests

def test_pyinstaller_spec_exists():
    """Test that PyInstaller spec file exists."""
    spec_file = Path(__file__).parent.parent / 'LegalMDConverter.spec'
    assert spec_file.exists()


def test_desktop_entry_exists():
    """Test that desktop entry file exists."""
    desktop_file = Path(__file__).parent.parent / 'legal-md-converter.desktop'
    assert desktop_file.exists()


def test_entitlements_file_exists():
    """Test that macOS entitlements file exists."""
    entitlements_file = Path(__file__).parent.parent / 'app.entitlements'
    assert entitlements_file.exists()


def test_pyproject_has_briefcase_config():
    """Test that pyproject.toml has Briefcase configuration."""
    import tomllib
    
    pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
    with open(pyproject_path, 'rb') as f:
        pyproject = tomllib.load(f)
    
    assert 'briefcase' in pyproject.get('tool', {})
    assert 'project_name' in pyproject['tool']['briefcase']
