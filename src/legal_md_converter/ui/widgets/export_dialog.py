"""
Export Dialog for Legal-MD-Converter.

Provides file format selection, template choice, and output configuration
for exporting converted documents.
"""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QTextEdit,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


logger = logging.getLogger(__name__)


class ExportDialog(QDialog):
    """
    Dialog for configuring document export settings.
    
    Features:
    - File format selection (Markdown, HTML, Plain Text)
    - Template selection (Legal, Academic, Basic)
    - Output path selection with file browser
    - Export options (metadata, formatting, headings)
    - Preview of export filename
    """
    
    # Signals
    export_requested = Signal(str, str, str, dict)  # format, template, output_path, options
    
    # Supported formats
    FORMATS = {
        'markdown': {
            'label': 'Markdown (.md)',
            'extension': '.md',
            'filter': 'Markdown Files (*.md);;All Files (*)'
        },
        'html': {
            'label': 'HTML (.html)',
            'extension': '.html',
            'filter': 'HTML Files (*.html);;All Files (*)'
        },
        'plaintext': {
            'label': 'Plain Text (.txt)',
            'extension': '.txt',
            'filter': 'Text Files (*.txt);;All Files (*)'
        }
    }
    
    # Available templates
    TEMPLATES = {
        'legal': 'Dokumen Hukum (Legal)',
        'academic': 'Dokumen Akademik (Academic)',
        'basic': 'Dasar (Basic)',
    }
    
    def __init__(
        self,
        source_filename: str = "",
        parent: Optional[QDialog] = None
    ) -> None:
        super().__init__(parent)
        
        self._source_filename = source_filename
        self._suggested_path = self._generate_suggested_path()
        
        self._setup_ui()
        self._connect_signals()
        
        # Set modal properties
        self.setModal(True)
        self.setWindowTitle('Ekspor Dokumen')
        self.setMinimumWidth(550)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Format selection
        format_group = QGroupBox('Format Output')
        format_layout = QVBoxLayout(format_group)
        
        self.format_combo = QComboBox()
        self.format_combo.setMinimumHeight(35)
        for key, fmt in self.FORMATS.items():
            self.format_combo.addItem(fmt['label'], key)
        self.format_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 1px solid #2196F3;
            }
        """)
        format_layout.addWidget(self.format_combo)
        
        layout.addWidget(format_group)
        
        # Template selection
        template_group = QGroupBox('Template Dokumen')
        template_layout = QVBoxLayout(template_group)
        
        self.template_combo = QComboBox()
        self.template_combo.setMinimumHeight(35)
        for key, label in self.TEMPLATES.items():
            self.template_combo.addItem(label, key)
        self.template_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 1px solid #2196F3;
            }
        """)
        template_layout.addWidget(self.template_combo)
        
        layout.addWidget(template_group)
        
        # Output path
        output_group = QGroupBox('Lokasi Output')
        output_layout = QVBoxLayout(output_group)
        
        path_layout = QHBoxLayout()
        
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setText(str(self._suggested_path))
        self.output_path_edit.setReadOnly(True)
        self.output_path_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f5f5f5;
                font-size: 13px;
            }
        """)
        path_layout.addWidget(self.output_path_edit)
        
        browse_button = QPushButton('Jelajahi...')
        browse_button.setToolTip('Pilih lokasi penyimpanan')
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        browse_button.clicked.connect(self._on_browse)
        path_layout.addWidget(browse_button)
        
        output_layout.addLayout(path_layout)
        
        layout.addWidget(output_group)
        
        # Export options
        options_group = QGroupBox('Opsi Ekspor')
        options_layout = QVBoxLayout(options_group)
        
        self.include_metadata = QCheckBox('Sertakan metadata dokumen')
        self.include_metadata.setChecked(True)
        self.include_metadata.setStyleSheet("QCheckBox { padding: 5px; font-size: 13px; }")
        options_layout.addWidget(self.include_metadata)
        
        self.preserve_formatting = QCheckBox('Pertahankan format asli')
        self.preserve_formatting.setChecked(True)
        self.preserve_formatting.setStyleSheet("QCheckBox { padding: 5px; font-size: 13px; }")
        options_layout.addWidget(self.preserve_formatting)
        
        self.numbered_headings = QCheckBox('Gunakan heading bernomor')
        self.numbered_headings.setChecked(False)
        self.numbered_headings.setStyleSheet("QCheckBox { padding: 5px; font-size: 13px; }")
        options_layout.addWidget(self.numbered_headings)
        
        self.include_toc = QCheckBox('Sertakan daftar isi (untuk dokumen panjang)')
        self.include_toc.setChecked(False)
        self.include_toc.setStyleSheet("QCheckBox { padding: 5px; font-size: 13px; }")
        options_layout.addWidget(self.include_toc)
        
        layout.addWidget(options_group)
        
        # Preview
        preview_group = QGroupBox('Pratinjau Nama File')
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 13px;
                padding: 8px;
                background-color: #f5f5f5;
                border-radius: 4px;
                font-family: monospace;
            }
        """)
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton('Batal')
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        button_layout.addWidget(cancel_button)
        
        export_button = QPushButton('Ekspor')
        export_button.setDefault(True)
        export_button.clicked.connect(self._on_export)
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        button_layout.addWidget(export_button)
        
        layout.addLayout(button_layout)
        
        # Update preview
        self._update_preview()
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.format_combo.currentIndexChanged.connect(self._update_preview)
    
    def _generate_suggested_path(self) -> Path:
        """Generate a suggested output file path."""
        if self._source_filename:
            base_name = Path(self._source_filename).stem
        else:
            base_name = 'converted_document'
        
        # Default to home directory
        output_dir = Path.home()
        
        return output_dir / f"{base_name}.md"
    
    def _update_preview(self) -> None:
        """Update the filename preview."""
        current_path = Path(self.output_path_edit.text())
        
        # Update extension based on format
        format_key = self.format_combo.currentData()
        if format_key:
            extension = self.FORMATS[format_key]['extension']
            new_path = current_path.with_suffix(extension)
            self.output_path_edit.setText(str(new_path))
        
        # Display formatted preview
        template_key = self.template_combo.currentData()
        template_name = self.TEMPLATES.get(template_key, 'Basic')
        format_name = self.FORMATS.get(format_key, {}).get('label', 'Markdown')
        
        preview_text = (
            f"Format: {format_name}\n"
            f"Template: {template_name}\n"
            f"Output: {self.output_path_edit.text()}"
        )
        self.preview_label.setText(preview_text)
    
    def _on_browse(self) -> None:
        """Handle browse button click."""
        format_key = self.format_combo.currentData()
        file_filter = self.FORMATS.get(format_key, {}).get('filter', 'All Files (*)')
        
        current_path = Path(self.output_path_edit.text())
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Simpan Dokumen',
            str(current_path),
            file_filter
        )
        
        if file_path:
            self.output_path_edit.setText(file_path)
            self._update_preview()
    
    def _on_export(self) -> None:
        """Handle export button click."""
        format_key = self.format_combo.currentData()
        template_key = self.template_combo.currentData()
        output_path = self.output_path_edit.text()
        
        if not output_path:
            QMessageBox.warning(
                self,
                'Peringatan',
                'Silakan pilih lokasi penyimpanan terlebih dahulu.'
            )
            return
        
        # Validate output path
        path = Path(output_path)
        if path.exists():
            reply = QMessageBox.question(
                self,
                'File Sudah Ada',
                f'File "{path.name}" sudah ada. Apakah Anda ingin menimpanya?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Collect options
        options = {
            'include_metadata': self.include_metadata.isChecked(),
            'preserve_formatting': self.preserve_formatting.isChecked(),
            'numbered_headings': self.numbered_headings.isChecked(),
            'include_toc': self.include_toc.isChecked(),
        }
        
        # Emit export signal
        self.export_requested.emit(format_key, template_key, output_path, options)
        
        logger.info(f'Export requested: {format_key} -> {output_path}')
        self.accept()
    
    def set_source_filename(self, filename: str) -> None:
        """
        Set the source filename for export.
        
        Args:
            filename: Source document filename
        """
        self._source_filename = filename
        self._suggested_path = self._generate_suggested_path()
        self.output_path_edit.setText(str(self._suggested_path))
        self._update_preview()
    
    def get_format(self) -> str:
        """Get selected export format."""
        return self.format_combo.currentData() or 'markdown'
    
    def get_template(self) -> str:
        """Get selected template."""
        return self.template_combo.currentData() or 'basic'
    
    def get_output_path(self) -> str:
        """Get output path."""
        return self.output_path_edit.text()
    
    def get_options(self) -> dict:
        """Get export options."""
        return {
            'include_metadata': self.include_metadata.isChecked(),
            'preserve_formatting': self.preserve_formatting.isChecked(),
            'numbered_headings': self.numbered_headings.isChecked(),
            'include_toc': self.include_toc.isChecked(),
        }
