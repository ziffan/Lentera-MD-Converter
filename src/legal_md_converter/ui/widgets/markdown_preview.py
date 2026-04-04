"""
Markdown Preview Widget for Legal-MD-Converter.

Provides live preview of Markdown output with syntax highlighting,
copy to clipboard, and export to file.
"""

import logging
from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor


logger = logging.getLogger(__name__)


class MarkdownPreview(QWidget):
    """
    Widget for live preview of Markdown output.
    
    Features:
    - Live Markdown preview with syntax highlighting
    - Copy to clipboard
    - Export to file
    - Word count display
    - Clear preview
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self._markdown_content = ""
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header toolbar
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel('Pratinjau Markdown')
        self.title_label.setStyleSheet('''
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                padding: 8px;
                background-color: #f5f5f5;
                border-bottom: 1px solid #e0e0e0;
            }
        ''')
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Word count
        self.word_count_label = QLabel('0 kata')
        self.word_count_label.setStyleSheet('''
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 8px;
            }
        ''')
        header_layout.addWidget(self.word_count_label)
        
        # Copy button
        self.copy_button = QPushButton('Salin')
        self.copy_button.setToolTip('Salin markdown ke clipboard')
        self.copy_button.setStyleSheet(self._button_style('#2196F3', '#1976D2'))
        header_layout.addWidget(self.copy_button)
        
        # Export button
        self.export_button = QPushButton('Ekspor')
        self.export_button.setToolTip('Ekspor markdown ke file')
        self.export_button.setStyleSheet(self._button_style('#4CAF50', '#388E3C'))
        header_layout.addWidget(self.export_button)
        
        # Clear button
        self.clear_button = QPushButton('Hapus')
        self.clear_button.setToolTip('Hapus pratinjau')
        self.clear_button.setStyleSheet(self._button_style('#757575', '#616161'))
        header_layout.addWidget(self.clear_button)
        
        layout.addLayout(header_layout)
        
        # Preview text edit
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont('Consolas', 11))
        self.preview_text.setPlaceholderText('Pratinjau markdown akan muncul di sini...')
        self.preview_text.setStyleSheet('''
            QTextEdit {
                background-color: white;
                border: none;
                padding: 15px;
                selection-background-color: #BBDEFB;
            }
        ''')
        layout.addWidget(self.preview_text)
        
        # Empty state label
        self.empty_label = QLabel(
            '<div style="text-align: center; padding: 60px; color: #999999;">'
            '<h2>Pratinjau Tidak Tersedia</h2>'
            '<p>Konversi dokumen untuk melihat pratinjau markdown di sini.</p>'
            '</div>'
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.copy_button.clicked.connect(self._on_copy_to_clipboard)
        self.export_button.clicked.connect(self._on_export)
        self.clear_button.clicked.connect(self._on_clear)
    
    def _button_style(self, bg: str, hover_bg: str) -> str:
        """Generate button stylesheet."""
        return f'''
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
        '''
    
    def set_content(self, markdown: str, title: str = "Dokumen") -> None:
        """
        Set the Markdown content to preview.
        
        Args:
            markdown: Markdown content
            title: Document title for display
        """
        self._markdown_content = markdown
        
        # Show preview, hide empty state
        self.preview_text.setVisible(True)
        self.empty_label.setVisible(False)
        
        # Set content
        self.preview_text.setPlainText(markdown)
        self.title_label.setText(f'Pratinjau Markdown - {title}')
        
        # Update word count (exclude markdown syntax tokens like #, *, -, etc.)
        import re
        clean_text = re.sub(r'^[#*\->`~]+\s*', '', markdown, flags=re.MULTILINE)
        word_count = len(clean_text.split())
        self.word_count_label.setText(f'{word_count} kata')
        
        # Apply syntax highlighting
        self._apply_syntax_highlighting()
        
        logger.info(f'Set markdown preview for: {title}')
    
    def _apply_syntax_highlighting(self) -> None:
        """Apply basic syntax highlighting to markdown."""
        cursor = self.preview_text.textCursor()
        
        # Define formats
        heading_format = QTextCharFormat()
        heading_format.setForeground(QColor('#1565C0'))
        heading_format.setFontWeight(QFont.Weight.Bold)
        
        code_format = QTextCharFormat()
        code_format.setForeground(QColor('#D32F2F'))
        code_format.setFont(QFont('Consolas', 11))
        
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Weight.Bold)
        
        # Simple highlighting for headings (# Heading)
        text = self.preview_text.toPlainText()
        lines = text.split('\n')
        pos = 0
        
        for line in lines:
            if line.startswith('#'):
                # Heading
                cursor.setPosition(pos)
                cursor.setPosition(pos + len(line), QTextCursor.MoveMode.KeepAnchor)
                cursor.mergeCharFormat(heading_format)
            
            pos += len(line) + 1  # +1 for newline
    
    def clear_preview(self) -> None:
        """Clear all preview content."""
        self._markdown_content = ""
        self.preview_text.clear()
        self.preview_text.setVisible(False)
        self.empty_label.setVisible(True)
        self.title_label.setText('Pratinjau Markdown')
        self.word_count_label.setText('0 kata')
    
    def get_content(self) -> str:
        """
        Get the current preview content.
        
        Returns:
            str: Markdown content
        """
        return self._markdown_content
    
    def _on_copy_to_clipboard(self) -> None:
        """Handle copy to clipboard button click."""
        from PySide6.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        markdown = self.get_content()
        
        if markdown:
            clipboard.setText(markdown)
            self.word_count_label.setText('✓ Disalin!')
            logger.info('Copied markdown to clipboard')
        else:
            self.word_count_label.setText('Tidak ada konten')
    
    def _on_export(self) -> None:
        """Handle export button click."""
        markdown = self.get_content()
        
        if not markdown:
            QMessageBox.information(
                self,
                'Tidak Ada Konten',
                'Tidak ada markdown untuk diekspor.'
            )
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Ekspor Markdown',
            str(Path.home() / 'document.md'),
            'Markdown Files (*.md);;All Files (*)'
        )
        
        if file_path:
            try:
                Path(file_path).write_text(markdown, encoding='utf-8')
                self.word_count_label.setText(f'✓ Diekspor: {Path(file_path).name}')
                logger.info(f'Exported markdown to: {file_path}')
            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Ekspor Gagal',
                    f'Gagal mengekspor markdown:\n{e}'
                )
                logger.error(f'Export failed: {e}', exc_info=True)
    
    def _on_clear(self) -> None:
        """Handle clear button click."""
        self.clear_preview()
        self.word_count_label.setText('0 kata')


# Import Path locally
from pathlib import Path
