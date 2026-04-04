"""
Main window for Legal-MD-Converter.

Provides the primary application interface with menu bar,
tool bar, file drop area, and document preview.
Integrates DocumentParserWorker for non-blocking document parsing.
Auto-triggers spellcheck after document conversion.
"""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow,
    QMenuBar,
    QMenu,
    QToolBar,
    QStatusBar,
    QSplitter,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QDockWidget,
    QGroupBox,
    QCheckBox,
    QComboBox,
    QLabel,
    QPushButton,
    QDialog,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QAction, QKeySequence, QDragEnterEvent, QDropEvent, QPixmap, QDesktopServices

from legal_md_converter.ui.widgets.file_drop_widget import FileDropWidget
from legal_md_converter.ui.widgets.document_preview import DocumentPreview
from legal_md_converter.ui.widgets.progress_dialog import ProgressDialog
from legal_md_converter.ui.widgets.spellcheck_panel import SpellCheckPanel, TypoMatch
from legal_md_converter.ui.widgets.export_dialog import ExportDialog
from legal_md_converter.ui.styles.app_theme import AppTheme
from legal_md_converter.engine.document_parser_worker import DocumentParserWorker, SingleDocumentWorker
from legal_md_converter.engine.document_service import DocumentService
from legal_md_converter.engine.docling_config import DoclingConfig
from legal_md_converter.engine.spell_check_worker import SpellCheckWorker
from legal_md_converter.engine.spell_check_result import SpellCheckResult
from legal_md_converter.utils.dependency_checker import DependencyChecker


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window for Legal-MD-Converter."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Initialize services
        self.document_service = DocumentService()
        self.parser_worker: Optional[DocumentParserWorker] = None
        self.spellcheck_worker: Optional[SpellCheckWorker] = None
        self.progress_dialog: Optional[ProgressDialog] = None

        self._setup_ui()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_dock_widgets()
        self._apply_theme()
        self._connect_signals()

        logger.info('MainWindow initialized')
    
    def _setup_ui(self) -> None:
        """Set up the main UI layout."""
        self.setWindowTitle('Lentera MD')
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter for file drop and document preview
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # File drop area (left panel)
        self.file_drop = FileDropWidget()
        self.splitter.addWidget(self.file_drop)
        
        # Document preview (right panel)
        self.document_preview = DocumentPreview()
        self.splitter.addWidget(self.document_preview)
        
        # Set initial splitter sizes (30% file drop, 70% preview)
        self.splitter.setSizes([420, 980])
        
        main_layout.addWidget(self.splitter)


        # Accept drops on the main window
        self.setAcceptDrops(True)
    
    def _create_menu_bar(self) -> None:
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        self.action_open = QAction('&Open Files...', self)
        self.action_open.setShortcut(QKeySequence.StandardKey.Open)
        self.action_open.setStatusTip('Open legal documents for conversion')
        file_menu.addAction(self.action_open)
        
        self.action_open_folder = QAction('Open &Folder...', self)
        self.action_open_folder.setStatusTip('Open a folder containing legal documents')
        file_menu.addAction(self.action_open_folder)
        
        file_menu.addSeparator()

        self.action_save = QAction('&Save Markdown...', self)
        self.action_save.setShortcut(QKeySequence.StandardKey.Save)
        self.action_save.setStatusTip('Simpan hasil konversi ke file Markdown')
        file_menu.addAction(self.action_save)

        file_menu.addSeparator()
        
        self.action_check_deps = QAction('Check &Dependencies', self)
        self.action_check_deps.setStatusTip('Check if all dependencies are installed')
        file_menu.addAction(self.action_check_deps)
        
        file_menu.addSeparator()
        
        self.action_exit = QAction('E&xit', self)
        self.action_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.action_exit.setStatusTip('Exit the application')
        file_menu.addAction(self.action_exit)
        
        # Edit menu
        edit_menu = menubar.addMenu('&Edit')
        
        self.action_select_all = QAction('Select &All', self)
        self.action_select_all.setShortcut(QKeySequence.StandardKey.SelectAll)
        edit_menu.addAction(self.action_select_all)
        
        self.action_clear = QAction('&Clear', self)
        self.action_clear.setStatusTip('Clear all loaded documents')
        edit_menu.addAction(self.action_clear)
        
        # View menu
        view_menu = menubar.addMenu('&View')

        self.action_toggle_spellcheck = QAction('Spell Check Panel', self)
        self.action_toggle_spellcheck.setCheckable(True)
        self.action_toggle_spellcheck.setStatusTip('Toggle spell check panel')
        view_menu.addAction(self.action_toggle_spellcheck)

        self.action_toggle_settings = QAction('Settings Panel', self)
        self.action_toggle_settings.setCheckable(True)
        self.action_toggle_settings.setStatusTip('Toggle settings panel')
        view_menu.addAction(self.action_toggle_settings)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        self.action_convert = QAction('&Convert to Markdown', self)
        self.action_convert.setShortcut(QKeySequence('Ctrl+Return'))
        self.action_convert.setStatusTip('Convert all loaded documents to Markdown')
        tools_menu.addAction(self.action_convert)
        
        self.action_batch_convert = QAction('&Batch Convert', self)
        self.action_batch_convert.setStatusTip('Batch convert multiple documents')
        tools_menu.addAction(self.action_batch_convert)
        
        self.action_spellcheck = QAction('&Spell Check', self)
        self.action_spellcheck.setStatusTip('Check spelling in converted documents')
        tools_menu.addAction(self.action_spellcheck)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        self.action_about = QAction('&About', self)
        self.action_about.setStatusTip('About Legal-MD-Converter')
        help_menu.addAction(self.action_about)
    
    def _create_tool_bar(self) -> None:
        """Create the application toolbar."""
        toolbar = QToolBar('Main Toolbar')
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Add actions to toolbar
        toolbar.addAction(self.action_open)
        toolbar.addAction(self.action_convert)
        toolbar.addAction(self.action_save)
        toolbar.addSeparator()
        toolbar.addAction(self.action_clear)
    
    def _create_status_bar(self) -> None:
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Ready')
    
    def _create_dock_widgets(self) -> None:
        """Create dockable widgets."""
        # Spell check panel (dockable)
        self.spellcheck_panel = SpellCheckPanel()
        self.spellcheck_dock = QDockWidget('Pemeriksaan Ejaan', self)
        self.spellcheck_dock.setWidget(self.spellcheck_panel)
        self.spellcheck_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.spellcheck_dock.setVisible(False)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.spellcheck_dock)

        # Settings panel (dockable)
        self.settings_dock = QDockWidget('Pengaturan', self)
        self.settings_widget = self._create_settings_widget()
        self.settings_dock.setWidget(self.settings_widget)
        self.settings_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.settings_dock.setVisible(False)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.settings_dock)
    
    def _create_settings_widget(self) -> QWidget:
        """Create the settings panel widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # OCR Settings
        ocr_group = QGroupBox('Pengaturan OCR')
        ocr_layout = QVBoxLayout(ocr_group)
        
        self.enable_ocr = QCheckBox('Aktifkan OCR untuk dokumen scan')
        self.enable_ocr.setChecked(True)
        ocr_layout.addWidget(self.enable_ocr)
        
        ocr_lang_layout = QVBoxLayout()
        ocr_lang_layout.addWidget(QLabel('Bahasa OCR:'))
        self.ocr_lang_combo = QComboBox()
        self.ocr_lang_combo.addItem('Indonesia + Inggris', ['ind', 'eng'])
        self.ocr_lang_combo.addItem('Indonesia saja', ['ind'])
        self.ocr_lang_combo.addItem('Inggris saja', ['eng'])
        ocr_lang_layout.addWidget(self.ocr_lang_combo)
        ocr_layout.addLayout(ocr_lang_layout)
        
        layout.addWidget(ocr_group)
        
        # Export Settings
        export_group = QGroupBox('Pengaturan Ekspor')
        export_layout = QVBoxLayout(export_group)
        
        export_layout.addWidget(QLabel('Template default:'))
        self.default_template = QComboBox()
        self.default_template.addItem('Dokumen Hukum (Legal)', 'legal')
        self.default_template.addItem('Dokumen Akademik (Academic)', 'academic')
        self.default_template.addItem('Dasar (Basic)', 'basic')
        export_layout.addWidget(self.default_template)
        
        self.include_metadata_export = QCheckBox('Sertakan metadata saat ekspor')
        self.include_metadata_export.setChecked(True)
        export_layout.addWidget(self.include_metadata_export)
        
        layout.addWidget(export_group)
        
        # Spellcheck Settings
        spell_group = QGroupBox('Pengaturan Ejaan')
        spell_layout = QVBoxLayout(spell_group)
        
        self.auto_spellcheck = QCheckBox('Periksa ejaan otomatis setelah konversi')
        self.auto_spellcheck.setChecked(True)
        spell_layout.addWidget(self.auto_spellcheck)
        
        self.skip_abbreviations = QCheckBox('Lewati singkatan umum (hlm, dst, dll)')
        self.skip_abbreviations.setChecked(True)
        spell_layout.addWidget(self.skip_abbreviations)
        
        self.skip_ordinals = QCheckBox('Lewati bilangan tingkat (ke-1, ke-2)')
        self.skip_ordinals.setChecked(True)
        spell_layout.addWidget(self.skip_ordinals)
        
        layout.addWidget(spell_group)
        
        layout.addStretch()
        
        return widget
    
    def _apply_theme(self) -> None:
        """Apply application theme."""
        self.setStyleSheet(AppTheme.get_main_stylesheet())
    
    def _connect_signals(self) -> None:
        """Connect UI signals to handlers."""
        self.action_open.triggered.connect(self._on_open_files)
        self.action_open_folder.triggered.connect(self._on_open_folder)
        self.action_save.triggered.connect(self.document_preview._on_save_markdown)
        self.action_exit.triggered.connect(self.close)
        self.action_clear.triggered.connect(self._on_clear)
        self.action_convert.triggered.connect(self._on_convert)
        self.action_about.triggered.connect(self._on_about)
        self.action_check_deps.triggered.connect(self._on_check_dependencies)
        self.action_toggle_spellcheck.triggered.connect(self._on_toggle_spellcheck)
        self.action_toggle_settings.triggered.connect(self._on_toggle_settings)
        self.action_spellcheck.triggered.connect(self._on_spellcheck)
        
        # Connect file drop signals
        self.file_drop.files_dropped.connect(self._on_files_dropped)
        
        # Connect spellcheck panel signals
        self.spellcheck_panel.navigate_to_position.connect(self._on_navigate_to_error)
        self.spellcheck_panel.replace_word.connect(self._on_replace_word)
    
    def _check_file_size(self, file_path: str) -> bool:
        """
        Check if file is too large and warn user.
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if user wants to continue
        """
        path = Path(file_path)
        
        if DoclingConfig.is_file_too_large(path):
            size_mb = path.stat().st_size / (1024 * 1024)
            reply = QMessageBox.question(
                self,
                'File Besar Terdeteksi',
                f'Ukuran file: {size_mb:.1f} MB\n\n'
                f'File ini lebih besar dari 50 MB. '
                f'Proses parsing akan memakan waktu lebih lama.\n\n'
                f'Lanjutkan?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            return reply == QMessageBox.StandardButton.Yes
        
        return True
    
    def _start_parsing(self, file_paths: list[str]) -> None:
        """
        Start parsing documents using worker thread.
        
        Args:
            file_paths: List of files to parse
        """
        # Filter files that pass size check
        valid_paths = []
        for fp in file_paths:
            if self._check_file_size(fp):
                valid_paths.append(fp)
        
        if not valid_paths:
            return
        
        # Create progress dialog
        self.progress_dialog = ProgressDialog(
            title='Mengonversi Dokumen...',
            cancelable=True,
            show_details=True,
            parent=self
        )
        
        # Create and start worker
        self.parser_worker = DocumentParserWorker(valid_paths)
        
        # Connect worker signals
        self.parser_worker.progress.connect(self._on_parse_progress)
        self.parser_worker.document_parsed.connect(self._on_document_parsed)
        self.parser_worker.parsing_complete.connect(self._on_parsing_complete)
        self.parser_worker.error_occurred.connect(self._on_parse_error)
        self.parser_worker.page_progress.connect(self._on_page_progress)
        self.parser_worker.log_message.connect(self._on_parse_log)
        
        # Connect cancel button
        self.progress_dialog.cancel_button.clicked.connect(self.parser_worker.cancel)
        
        # Start worker
        self.parser_worker.start()
        
        # Show progress dialog
        self.progress_dialog.show()
        
        self.status_bar.showMessage(f'Mengonversi {len(valid_paths)} dokumen...')
    
    # Event handlers
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event for file drops."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop event for file drops."""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self._on_files_dropped(files)
    
    # Slot methods
    def _on_open_files(self) -> None:
        """Handle open files action."""
        file_filter = (
            'Legal Documents (*.pdf *.docx *.doc *.rtf *.txt);;'
            'PDF Files (*.pdf);;'
            'Word Documents (*.docx *.doc);;'
            'Rich Text Format (*.rtf);;'
            'Text Files (*.txt);;'
            'All Files (*)'
        )
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            'Open Legal Documents',
            str(Path.home()),
            file_filter
        )
        
        if files:
            self._on_files_dropped(files)
    
    def _on_open_folder(self) -> None:
        """Handle open folder action."""
        folder = QFileDialog.getExistingDirectory(
            self,
            'Select Folder with Legal Documents',
            str(Path.home())
        )
        
        if folder:
            folder_path = Path(folder)
            # Find all supported files in the folder
            supported_extensions = {'.pdf', '.docx', '.doc', '.rtf', '.txt'}
            files = [
                str(f) for f in folder_path.rglob('*')
                if f.suffix.lower() in supported_extensions and f.is_file()
            ]
            
            if files:
                self._on_files_dropped(files)
            else:
                self.status_bar.showMessage('No supported documents found in selected folder')
    
    def _on_export(self) -> None:
        """Handle export action."""
        files = self.file_drop.get_files()
        
        if not files:
            QMessageBox.information(
                self,
                'No Files',
                'Tidak ada dokumen untuk diekspor.'
            )
            return
        
        # Show export dialog
        source_file = files[0] if len(files) == 1 else ""
        export_dialog = ExportDialog(source_file, self)
        
        if export_dialog.exec() == export_dialog.DialogCode.Accepted:
            format_key = export_dialog.get_format()
            template_key = export_dialog.get_template()
            output_path = export_dialog.get_output_path()
            options = export_dialog.get_options()
            
            # Perform export
            try:
                for file_path in files:
                    doc_info = self.document_service.get_document(file_path)
                    if doc_info and doc_info.content:
                        success = self.document_service.export_file(
                            file_path,
                            output_path,
                            template_key
                        )
                        if success:
                            self.status_bar.showMessage(f'Diekspor ke: {output_path}')
                        else:
                            QMessageBox.warning(
                                self,
                                'Ekspor Gagal',
                                f'Gagal mengekspor {Path(file_path).name}'
                            )
            except Exception as e:
                logger.error(f'Export error: {e}', exc_info=True)
                QMessageBox.critical(
                    self,
                    'Error',
                    f'Terjadi kesalahan saat ekspor:\n{e}'
                )
    
    def _on_clear(self) -> None:
        """Handle clear action."""
        self.file_drop.clear_files()
        self.document_preview.clear_preview()
        self.document_service.clear_all()
        self.status_bar.showMessage('Cleared all documents')
    
    def _on_convert(self) -> None:
        """Handle convert action."""
        files = self.file_drop.get_files()
        
        if not files:
            QMessageBox.information(
                self,
                'No Files',
                'Harap tambahkan dokumen hukum untuk dikonversi terlebih dahulu.'
            )
            return
        
        # Start parsing
        self._start_parsing(files)
    
    def _on_about(self) -> None:
        """Handle about action — custom dialog with logo and links."""
        dlg = QDialog(self)
        dlg.setWindowTitle('Tentang Lentera MD')
        dlg.setFixedWidth(460)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 20)

        # Logo
        logo_label = QLabel()
        icon_path = Path(__file__).parent.parent.parent.parent / 'assets' / 'icons' / 'app_icon.png'
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path)).scaled(
                120, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # App name & version
        name_label = QLabel('<h2 style="margin:0">Lentera MD</h2>')
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        version_label = QLabel('<p style="color:#666;margin:0">Versi 1.0.0</p>')
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Description
        desc = QLabel(
            '<p style="text-align:center;color:#444">'
            'Aplikasi desktop <i>cross-platform</i> untuk mengonversi<br>'
            'dokumen hukum Indonesia ke format Markdown.<br>'
            'Dilengkapi pemeriksaan ejaan KBBI.</p>'
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        # Separator line
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet('background:#e0e0e0;')
        layout.addWidget(sep)

        # Links
        links_label = QLabel(
            '<p style="text-align:center">'
            '<b>Tautan</b><br>'
            '<a href="https://github.com/ziffan/Lentera-MD-Converter">GitHub — Lentera MD Converter</a><br><br>'
            '<b>Dukung pengembangan:</b><br>'
            '<a href="https://saweria.co/kampusmerahdeveloper">Saweria — Kampus Merah Developer</a><br>'
            '<a href="https://ko-fi.com/kampusmerahdev">Ko-fi — Kampus Merah Dev</a>'
            '</p>'
        )
        links_label.setOpenExternalLinks(True)
        links_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        links_label.setTextFormat(Qt.TextFormat.RichText)
        links_label.setStyleSheet('QLabel { font-size: 13px; }')
        layout.addWidget(links_label)

        # Separator line 2
        sep2 = QLabel()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet('background:#e0e0e0;')
        layout.addWidget(sep2)

        # Disclaimer
        disclaimer_label = QLabel(
            '<p style="text-align:center;color:#795548;font-size:11px">'
            '<b>&#9888; Peringatan</b><br>'
            'Mohon periksa kembali hasil olah kata/kalimat sebelum digunakan.<br>'
            'Jika dokumen bersumber dari hasil OCR, kemungkinan akan banyak tipo<br>'
            'dan pemenggalan kata/kalimat yang tidak sesuai.<br>'
            'Hasil di luar tanggung jawab pengembang. Terima kasih.'
            '</p>'
        )
        disclaimer_label.setWordWrap(True)
        disclaimer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(disclaimer_label)

        # Built with
        tech_label = QLabel(
            '<p style="text-align:center;color:#888;font-size:11px">'
            'Dibangun dengan PySide6, Docling, dan KBBI SQLite</p>'
        )
        tech_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tech_label)

        # Close button
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(dlg.accept)
        layout.addWidget(btn_box)

        dlg.exec()
    
    def _on_check_dependencies(self) -> None:
        """Handle check dependencies action."""
        checks = DependencyChecker.check_all()
        report = DependencyChecker.generate_report(checks)
        
        if checks['is_ready']:
            QMessageBox.information(
                self,
                'Dependensi',
                f'✓ Semua dependensi tersedia\n\n{report}'
            )
        else:
            QMessageBox.warning(
                self,
                'Dependensi Hilang',
                f'Beberapa dependensi hilang:\n\n{report}'
            )
    
    def _on_toggle_spellcheck(self) -> None:
        """Handle toggle spellcheck panel visibility."""
        visible = self.spellcheck_dock.isVisible()
        self.spellcheck_dock.setVisible(not visible)
        self.action_toggle_spellcheck.setChecked(not visible)
    
    def _on_toggle_settings(self) -> None:
        """Handle toggle settings panel visibility."""
        visible = self.settings_dock.isVisible()
        self.settings_dock.setVisible(not visible)
        self.action_toggle_settings.setChecked(not visible)
    
    def _on_spellcheck(self) -> None:
        """Handle spellcheck action."""
        files = self.file_drop.get_files()

        if not files:
            QMessageBox.information(
                self,
                'No Files',
                'Tidak ada dokumen untuk diperiksa ejaannya.'
            )
            return

        # Check first document
        file_path = files[0]
        doc_info = self.document_service.get_document(file_path)

        if not doc_info or not doc_info.is_converted:
            QMessageBox.warning(
                self,
                'Dokumen Belum Dikonversi',
                'Harap konversi dokumen terlebih dahulu sebelum memeriksa ejaan.'
            )
            return

        # Trigger spellcheck using worker
        self._on_document_loaded(file_path)
    
    def _on_spellcheck_progress(self, current: int, total: int) -> None:
        """Handle spellcheck progress update."""
        self.spellcheck_panel.set_progress(current, total)
    
    def _on_spellcheck_complete(self, result: SpellCheckResult) -> None:
        """Handle spellcheck completion."""
        # Update panel with results
        self.spellcheck_panel.set_complete(result.total_words, result.typos)
        
        # Highlight typos in preview
        if result.typos:
            self.document_preview.highlight_typos(result.typos)
        
        self.status_bar.showMessage(result.summary())
        logger.info(f'Spellcheck complete: {result.summary()}')
    
    def _on_spellcheck_error(self, error_message: str) -> None:
        """Handle spellcheck error."""
        self.spellcheck_panel.set_message(f'Error: {error_message}')
        QMessageBox.warning(
            self,
            'Pemeriksaan Ejaan Gagal',
            f'Terjadi kesalahan saat memeriksa ejaan:\n\n{error_message}'
        )
        logger.error(f'Spellcheck error: {error_message}')
    
    def _on_files_dropped(self, files: list[str]) -> None:
        """Handle files being dropped or added."""
        if files:
            self.file_drop.add_files(files)
            self.status_bar.showMessage(f'Ditambahkan {len(files)} dokumen')
    
    # Worker signal handlers
    def _on_parse_progress(self, current: int, total: int) -> None:
        """Handle parsing progress update."""
        if self.progress_dialog:
            self.progress_dialog.set_progress(current, total)
            self.progress_dialog.set_message(f'Mengonversi {current} dari {total} dokumen...')
    
    def _on_page_progress(self, current_page: int, total_pages: int, file_name: str) -> None:
        """Handle page-level progress for large files."""
        if self.progress_dialog:
            self.progress_dialog.add_detail(
                f'{file_name}: Halaman {current_page}/{total_pages}'
            )
    
    def _on_document_parsed(self, file_path: str, content) -> None:
        """Handle single document parsed."""
        if self.progress_dialog:
            self.progress_dialog.add_detail(f'✓ {Path(file_path).name}')
        
        # Update document service
        if content:
            self.document_service.load_file(file_path)
            doc_info = self.document_service.get_document(file_path)
            if doc_info:
                doc_info.content = content
                doc_info.status = 'parsed'
    
    def _on_parsing_complete(self, results: dict) -> None:
        """Handle parsing completion."""
        parsed_count = sum(1 for v in results.values() if v is not None)
        failed_count = len(results) - parsed_count

        if self.progress_dialog:
            if parsed_count == 0 and failed_count > 0:
                self.progress_dialog.fail()
            else:
                self.progress_dialog.complete()

        self.status_bar.showMessage(
            f'Selesai: {parsed_count} berhasil, {failed_count} gagal'
        )

        # Update preview with first parsed document (use proper converted markdown)
        first_parsed_file = None
        for file_path, content in results.items():
            if content:
                try:
                    doc_info = self.document_service.convert_to_markdown(file_path)
                    markdown = doc_info.markdown or content.raw_text
                except Exception:
                    markdown = content.raw_text
                self.document_preview.set_content(markdown, Path(file_path).name)
                first_parsed_file = file_path
                break

        if failed_count > 0:
            QMessageBox.warning(
                self,
                'Parsing Selesai dengan Peringatan',
                f'{parsed_count} dokumen berhasil diproses.\n'
                f'{failed_count} dokumen gagal diproses.'
            )

        # Auto-trigger spellcheck if enabled
        if first_parsed_file and self.auto_spellcheck.isChecked():
            self._on_document_loaded(first_parsed_file)

        logger.info(f'Parsing complete: {parsed_count} succeeded, {failed_count} failed')

    def _on_document_loaded(self, file_path: str) -> None:
        """Trigger spellcheck after document load."""
        if not self.document_service.is_spell_checker_ready():
            logger.debug('Spell checker not ready, skipping auto-check')
            return

        # Show spellcheck panel
        self.spellcheck_dock.setVisible(True)
        self.spellcheck_panel.clear()
        self.spellcheck_panel.set_progress(0, 100)

        # Start spellcheck worker
        doc_info = self.document_service.get_document(file_path)
        if not doc_info or not doc_info.is_converted:
            return

        text = doc_info.markdown or (doc_info.content.raw_text if doc_info.content else '')
        if not text:
            return

        self.spellcheck_worker = SpellCheckWorker(
            self.document_service._spell_checker._searcher,
            text
        )
        self.spellcheck_worker.progress.connect(self._on_spellcheck_progress)
        self.spellcheck_worker.result_ready.connect(self._on_spellcheck_complete)
        self.spellcheck_worker.error_occurred.connect(self._on_spellcheck_error)
        self.spellcheck_worker.start()

        self.status_bar.showMessage('Memeriksa ejaan...')
    
    def _on_parse_log(self, message: str) -> None:
        """Forward worker log messages to the progress dialog detail log."""
        if self.progress_dialog:
            self.progress_dialog.add_detail(message)

    def _on_parse_error(self, error_message: str) -> None:
        """Handle parsing error."""
        if self.progress_dialog:
            self.progress_dialog.set_message(f'Error: {error_message}')
        
        QMessageBox.critical(
            self,
            'Parsing Error',
            f'Terjadi kesalahan saat memproses dokumen:\n\n{error_message}'
        )
        
        self.status_bar.showMessage('Parsing gagal')
    
    def _on_navigate_to_error(self, start: int, end: int) -> None:
        """Handle navigation to spelling error in document preview."""
        self.document_preview.navigate_to_position(start, end)

    def _on_replace_word(self, start: int, end: int, new_word: str) -> None:
        """Handle word replacement in document preview."""
        self.document_preview.replace_text_at(start, end, new_word)
        logger.info(f'Replaced word at {start}-{end} with "{new_word}"')
    
    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Cancel any running workers
        if self.parser_worker and self.parser_worker.isRunning():
            self.parser_worker.cancel()
            self.parser_worker.wait(3000)
        
        if self.spellcheck_worker and self.spellcheck_worker.isRunning():
            self.spellcheck_worker.cancel()
            self.spellcheck_worker.wait(3000)

        # Clean up services
        self.document_service.close()

        logger.info('MainWindow closing')
        event.accept()
