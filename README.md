# Lentera MD

A cross-platform desktop application for converting legal documents (PDF, DOCX, DOC, TXT, RTF) to Markdown format with KBBI-powered spell checking.

> **Status:** ✅ Production Ready (64 files)
> **Built with:** PySide6 (Qt6) + Docling (IBM) + RapidOCR

## Features

- **Multi-format Support**: Convert PDF, DOCX, DOC, TXT, and RTF files to Markdown
- **Drag & Drop Interface**: Easy file loading with QTreeWidget-based drag-and-drop
- **Real-time Preview**: View converted Markdown content with syntax highlighting and Ctrl+F search
- **KBBI Spellchecker**: Indonesian dictionary with 71,093 words, FTS5 search, and Bloom Filter
- **Batch Processing**: Convert multiple documents simultaneously
- **Cross-Platform**: Runs on Windows, macOS, and Linux with native adapters
- **Template System**: Export with 3 built-in templates (Legal, Academic, Basic)
- **User Dictionary**: Persistent custom dictionary (SQLite) for domain-specific terms
- **Large File Support**: Chunked processing for files >50MB

## Requirements

- Python 3.12 or higher
- PySide6 >= 6.6.0
- Docling >= 1.0.0
- PyTorch (CPU-only recommended)

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd legal-md-converter

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install PyTorch CPU-only (avoids ~2GB CUDA download)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Fix torchvision if needed
pip uninstall -y torchvision
pip install torchvision --index-url https://download.pytorch.org/whl/cpu

# Install dependencies
pip install -e ".[dev]"

# Run the application
python -m legal_md_converter.main
```

## Usage

1. **Launch the application**:
   ```bash
   python -m legal_md_converter.main
   ```

2. **Add documents**:
   - Drag and drop files onto the application window
   - Click "Add Files..." to browse for documents
   - Use File > Open Files or File > Open Folder

3. **Convert to Markdown**:
   - Click "Convert to Markdown" in the toolbar
   - View the converted content in the preview panel

4. **Spell Check**:
   - Spellcheck auto-triggers after conversion
   - Use the spellcheck panel to replace, ignore, or add words to user dictionary

5. **Export**:
   - Click "Save Markdown" to export with template selection
   - Click "Copy to Clipboard" to copy the content

## Supported Formats

| Format | Extension | Support Level |
|--------|-----------|---------------|
| PDF | .pdf | Full (with OCR via Docling + RapidOCR) |
| Word | .docx, .doc | Full (via parse_generic) |
| Rich Text | .rtf | Full (via parse_generic) |
| Plain Text | .txt | Full (native) |
| PowerPoint | .pptx | Supported (via parse_generic) |
| Excel | .xlsx | Supported (via parse_generic) |
| HTML | .html | Supported (via parse_generic) |
| Markdown | .md | Supported (via parse_generic) |

## Architecture

### 4-Layer Architecture

```
┌──────────────────────────────────────────────────────────┐
│  PRESENTATION: MainWindow, Preview, Dialog, Dock Widgets │
├──────────────────────────────────────────────────────────┤
│  BUSINESS LOGIC: DocumentService, SpellCheckEngine,      │
│                  MarkdownExporter                        │
├──────────────────────────────────────────────────────────┤
│  DATA: KBBI SQLite (71K kata), AssetManager,             │
│        UserDictionary, KBBISearcher (FTS5 + Bloom)      │
├──────────────────────────────────────────────────────────┤
│  PLATFORM: WindowsAdapter, MacOSAdapter, LinuxAdapter    │
└──────────────────────────────────────────────────────────┘
```

### UI Layer (PySide6)
- **MainWindow**: Primary application window with menus, toolbars, status bar, split view, and dock widgets
- **FileDropWidget**: QTreeWidget-based drag-and-drop interface for file management
- **DocumentPreview**: Markdown content display with Ctrl+F search
- **PreviewWidget**: Enhanced preview with spellcheck highlights
- **SpellCheckPanel**: Spellcheck UI with replace/ignore/add-to-dict
- **ExportDialog**: Export configuration dialog with template selection
- **MarkdownPreview**: Live Markdown preview with syntax highlighting
- **ProgressDialog**: Thread-safe progress dialog
- **AppTheme**: Cross-platform Qt stylesheet

### Engine Layer
- **DocumentService**: Business logic layer coordinating parsing and conversion
- **DoclingParser**: Docling-based PDF/TXT/DOCX parser with async init and error handling
- **DocumentParser**: Legacy parser for backward compatibility
- **DoclingConfig**: Cross-platform model paths, OCR configuration
- **DocumentParserWorker**: QThread worker with progress reporting
- **LargeFileProcessor**: Chunked processing for files >50MB
- **MarkdownConverter**: Markdown exporter with TemplateLoader
- **SpellChecker**: KBBI spellcheck engine with document-level checking
- **SpellCheckWorker**: Chunk-based spellcheck worker
- **IndonesianTextProcessor**: Abbreviation detection, ordinal handling, diacritics
- **DependencyChecker**: Python + system dependency validation

### Data Layer
- **KBBISearcher**: FTS5 + Bloom Filter searcher (71,093 words)
- **KBBIDatabase**: KBBI database management
- **UserDictionary**: Persistent user dictionary (SQLite) for domain-specific terms
- **AssetManager**: Cross-platform asset bundling (templates, icons, KBBI DB)

### Platform Layer
- **BaseAdapter**: Abstract interface for platform-specific behavior
- **WindowsAdapter**: Windows paths, registry, theme detection
- **MacOSAdapter**: macOS paths, sandbox support, dark mode detection
- **LinuxAdapter**: XDG paths, GTK theme detection

### Utilities
- **ThreadWorker**: Background processing with QMutex-based cancel support
- **BatchWorker**: Multi-file batch processing
- **ThreadPool**: Thread pool for parallel operations
- **PathUtils**: Cross-platform path helpers

## Project Structure

```
legal-md-converter/
├── src/
│   └── legal_md_converter/
│       ├── __init__.py
│       ├── main.py                 # Entry point, high-DPI, frozen mode
│       ├── app.py                  # Briefcase entry point
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py      # MainWindow (menus, docks, workers, auto-spellcheck)
│       │   ├── widgets/
│       │   │   ├── __init__.py
│       │   │   ├── file_drop_widget.py      # Drag & drop (QTreeWidget)
│       │   │   ├── document_preview.py      # Markdown preview + Ctrl+F
│       │   │   ├── preview_widget.py        # Enhanced preview + spellcheck highlights
│       │   │   ├── spellcheck_panel.py      # Spellcheck UI (replace/ignore/add)
│       │   │   ├── export_dialog.py         # Export config dialog
│       │   │   ├── markdown_preview.py      # Live Markdown preview
│       │   │   └── progress_dialog.py       # Thread-safe progress dialog
│       │   └── styles/
│       │       ├── __init__.py
│       │       └── app_theme.py             # Cross-platform Qt stylesheet
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── docling_parser.py            # Docling PDF/TXT/DOCX parser
│       │   ├── docling_config.py            # OCR config, cross-platform model paths
│       │   ├── document_parser.py           # Legacy parser (backward compat)
│       │   ├── document_parser_worker.py    # QThread worker with progress
│       │   ├── document_service.py          # Business logic layer
│       │   ├── large_file_processor.py      # Chunked processing >50MB
│       │   ├── markdown_converter.py        # Markdown exporter + TemplateLoader
│       │   ├── spell_checker.py             # KBBI spellcheck engine
│       │   ├── spell_check_result.py        # TypoMatch + SpellCheckResult
│       │   ├── spell_check_worker.py        # Chunk-based spellcheck worker
│       │   └── indonesian_text_processor.py # Abbreviations, ordinals, diacritics
│       ├── data/
│       │   ├── __init__.py
│       │   ├── kbbi_database.py             # KBBI database management
│       │   ├── kbbi_searcher.py             # FTS5 + Bloom Filter searcher
│       │   ├── asset_manager.py             # Cross-platform asset bundling
│       │   └── user_dictionary.py           # Persistent user dictionary (SQLite)
│       ├── platform/
│       │   ├── __init__.py
│       │   ├── base_adapter.py              # Abstract interface
│       │   ├── windows_adapter.py           # Windows paths, registry
│       │   ├── macos_adapter.py             # macOS paths, sandbox
│       │   └── linux_adapter.py             # XDG paths, GTK theme
│       └── utils/
│           ├── __init__.py
│           ├── thread_worker.py             # Worker + cancel (QMutex), BatchWorker
│           ├── path_utils.py                # Cross-platform path helpers
│           └── dependency_checker.py        # Python + system dependency validation
├── assets/
│   ├── kbbi/
│   │   ├── kbbi.db                    # KBBI database (71,093 words, 4.3 MB)
│   │   └── schema.sql                 # KBBI database schema
│   ├── templates/
│   │   ├── legal.md                   # Legal document template
│   │   ├── academic.md                # Academic document template
│   │   └── basic.md                   # Basic template
│   └── icons/
│       ├── app_icon.png               # App icon PNG (256×256)
│       └── app_icon.ico               # App icon ICO (multi-size)
├── tests/
│   ├── test_ui.py                     # UI component tests
│   ├── test_phase2.py                 # Docling integration tests
│   ├── test_phase3.py                 # Spellcheck integration tests
│   └── test_phase4.py                 # Export & packaging tests
├── pyproject.toml                     # Project config + Briefcase config
├── LegalMDConverter.spec              # PyInstaller spec
├── build_app.py                       # Cross-platform build script
├── build_macos.sh                     # macOS build (DMG + codesign + notarize)
├── build_debian.sh                    # Debian .deb package build
├── legal-md-converter.desktop         # Linux desktop entry
├── app.entitlements                   # macOS sandbox entitlements
├── HOW_TO_USE.md                      # User guide (EN/ID)
├── README.md                          # This file
└── LAPORAN_PEKERJAAN.md               # Detailed work report
```

## Development

### Running Tests

```bash
pytest tests/
```

### Building Executables

```bash
# Cross-platform build (one-file)
python build_app.py

# Cross-platform build (directory bundle)
python build_app.py --onedir

# macOS build (with DMG + codesign + notarization)
chmod +x build_macos.sh && ./build_macos.sh

# Debian/Ubuntu build (.deb package)
chmod +x build_debian.sh && ./build_debian.sh
```

### Packaging with Briefcase

```bash
# Install Briefcase
pip install briefcase

# Create platform-specific packages
briefcase create
briefcase build
briefcase package
```

## Performance Benchmarks

| Step | Result | Time |
|------|--------|------|
| Parse PDF (13.8 MB) | ✅ 366 words | 189s (first run, downloads model) |
| Convert → Markdown | ✅ 3 templates | <1ms |
| Spellcheck (71K KBBI words) | ✅ 82 typos (74% accurate) | 12.3s |
| Export → File | ✅ 314 bytes | <1ms |

## Roadmap

### Phase 1 ✅ — Project Setup & UI Foundation
- [x] Project structure (18 files)
- [x] PySide6 UI foundation (MainWindow, menus, toolbars, docks)
- [x] FileDropWidget with QTreeWidget drag-and-drop
- [x] DocumentPreview + PreviewWidget with Ctrl+F search
- [x] AppTheme with cross-platform stylesheet
- [x] ThreadWorker for background processing
- [x] Platform adapters (Windows, macOS, Linux)
- [x] AssetManager and path utilities
- [x] Test suite

### Phase 2 ✅ — Docling Integration & Document Parsing
- [x] Docling parser with async init + error handling
- [x] OCR configuration and cross-platform model paths
- [x] Document parser worker with progress reporting
- [x] Large file processor (chunked processing >50MB)
- [x] Document service (business logic layer)
- [x] Dependency checker
- [x] Error handling: CorruptDocumentError, EncryptedDocumentError

### Phase 3 ✅ — KBBI Spellcheck Integration
- [x] SpellCheckResult dataclasses (TypoMatch, SpellCheckResult)
- [x] Spell check worker with chunk-based processing
- [x] Indonesian text processor (abbreviations, ordinals, diacritics)
- [x] User dictionary (persistent, SQLite)
- [x] Enhanced spell checker with check_document() and get_typos()
- [x] Auto-trigger spellcheck after conversion

### Phase 4 ✅ — Markdown Export & Packaging
- [x] 3 export templates (Legal, Academic, Basic)
- [x] Markdown preview with syntax highlighting
- [x] TemplateLoader in Markdown converter
- [x] PyInstaller spec and build scripts
- [x] Linux desktop entry
- [x] macOS sandbox entitlements
- [x] Briefcase configuration

### Future Enhancements
- [ ] Legal citation detection
- [ ] Document structure analysis
- [ ] Custom template editor
- [ ] Cloud sync capabilities
- [ ] Plugin system

## Troubleshooting

### torchvision CUDA Error
```
RuntimeError: operator torchvision::nms does not exist
```
**Fix:** Reinstall torchvision with CPU-only index:
```bash
pip uninstall -y torchvision
pip install torchvision --index-url https://download.pytorch.org/whl/cpu
```

### First Run Slow (Model Download)
- First PDF parsing downloads Docling models (~1-2 GB)
- Subsequent runs use cached models and are much faster

### Spellcheck Log Spam
- Fixed: Bloom filter warning now logs only once (DEBUG level)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Docling](https://github.com/DS4SD/docling) (IBM) for document conversion
- [RapidOCR](https://github.com/RapidAI/RapidOCR) for OCR engine
- [PySide6](https://www.qt.io/product/development-tools) for the UI framework
- KBBI for Indonesian dictionary standards (71,093 words)

## Support

For issues, questions, or contributions, please open an issue on GitHub.
