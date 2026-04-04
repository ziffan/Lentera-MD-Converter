"""
Document preview widget for Legal-MD-Converter.

Displays the converted Markdown content with preview capabilities.
Supports search within document (Ctrl+F).
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
    QTabWidget,
    QSplitter,
    QLineEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor


logger = logging.getLogger(__name__)


class DocumentPreview(QWidget):
    """Widget for previewing converted Markdown documents."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self._search_visible = False
        self._search_term = ""
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel('Document Preview')
        self.title_label.setStyleSheet('''
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                padding: 5px;
            }
        ''')
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Copy button
        self.copy_button = QPushButton('Copy to Clipboard')
        self.copy_button.setToolTip('Copy markdown to clipboard')
        header_layout.addWidget(self.copy_button)
        
        # Save button
        self.save_button = QPushButton('Save Markdown')
        self.save_button.setToolTip('Save markdown to file')
        header_layout.addWidget(self.save_button)
        
        layout.addLayout(header_layout)
        
        # Search bar (hidden by default)
        self.search_widget = QWidget()
        self.search_widget.setVisible(False)
        self.search_widget.setStyleSheet('''
            QWidget {
                background-color: #f5f5f5;
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
            }
        ''')
        
        search_layout = QHBoxLayout(self.search_widget)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in document... (Ctrl+F)")
        self.search_input.setStyleSheet('''
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        ''')
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)
        
        self.search_prev_btn = QPushButton("▲")
        self.search_prev_btn.setToolTip("Previous match")
        self.search_prev_btn.setFixedWidth(30)
        self.search_prev_btn.clicked.connect(self._search_previous)
        search_layout.addWidget(self.search_prev_btn)
        
        self.search_next_btn = QPushButton("▼")
        self.search_next_btn.setToolTip("Next match")
        self.search_next_btn.setFixedWidth(30)
        self.search_next_btn.clicked.connect(self._search_next)
        search_layout.addWidget(self.search_next_btn)
        
        self.search_close_btn = QPushButton("✕")
        self.search_close_btn.setToolTip("Close search")
        self.search_close_btn.setFixedWidth(30)
        self.search_close_btn.clicked.connect(self._hide_search)
        search_layout.addWidget(self.search_close_btn)
        
        layout.addWidget(self.search_widget)
        
        # Tab widget for multiple documents
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        layout.addWidget(self.tab_widget)
        
        # Empty state label
        self.empty_label = QLabel('No documents loaded.\n\nAdd legal documents to see the preview.')
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet('''
            QLabel {
                color: #999999;
                font-size: 14px;
                padding: 40px;
            }
        ''')
        layout.addWidget(self.empty_label)
        
        # Markdown preview area
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont('Consolas', 11))
        self.preview_text.setPlaceholderText('Converted markdown will appear here...')
        layout.addWidget(self.preview_text)
        
        # Hide preview initially
        self.preview_text.hide()
        self.tab_widget.hide()
        
        # Connect signals
        self.copy_button.clicked.connect(self._on_copy_to_clipboard)
        self.save_button.clicked.connect(self._on_save_markdown)
        self.tab_widget.tabCloseRequested.connect(self._on_close_tab)
    
    def set_content(self, markdown: str, filename: str = 'Document') -> None:
        """
        Set the markdown content to display.
        
        Args:
            markdown: The markdown content to display
            filename: The document filename for the tab
        """
        # Show preview, hide empty state
        self.preview_text.show()
        self.empty_label.hide()
        
        # Set content
        self.preview_text.setPlainText(markdown)
        self.title_label.setText(f'Document Preview - {filename}')
        
        logger.info(f'Set content for document: {filename}')
    
    def add_tab(self, filename: str, markdown: str) -> None:
        """
        Add a new tab with markdown content.
        
        Args:
            filename: The document filename for the tab
            markdown: The markdown content to display
        """
        # Create new text edit for this tab
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont('Consolas', 11))
        text_edit.setPlainText(markdown)
        
        # Add tab
        tab_name = Path(filename).stem if '.' in filename else filename
        self.tab_widget.addTab(text_edit, tab_name)
        
        # Show tab widget, hide single preview
        self.tab_widget.show()
        self.preview_text.hide()
        self.empty_label.hide()
        
        logger.info(f'Added tab for document: {filename}')
    
    def clear_preview(self) -> None:
        """Clear all preview content."""
        self.preview_text.clear()
        self.tab_widget.clear()
        
        # Show empty state, hide previews
        self.empty_label.show()
        self.preview_text.hide()
        self.tab_widget.hide()
        
        self._hide_search()
        self.title_label.setText('Document Preview')
        
        logger.info('Cleared preview')
    
    def get_current_markdown(self) -> str:
        """Get the current markdown content."""
        if self.tab_widget.isVisible():
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, QTextEdit):
                return current_widget.toPlainText()
        return self.preview_text.toPlainText()
    
    # Search functionality
    def toggle_search(self) -> None:
        """Toggle search bar visibility."""
        if self._search_visible:
            self._hide_search()
        else:
            self._show_search()
    
    def _show_search(self) -> None:
        """Show search bar and focus input."""
        self._search_visible = True
        self.search_widget.setVisible(True)
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def _hide_search(self) -> None:
        """Hide search bar and clear highlights."""
        self._search_visible = False
        self.search_widget.setVisible(False)
        self.search_input.clear()
        self._clear_search_highlights()
    
    def _on_search_changed(self, text: str) -> None:
        """Handle search text change."""
        self._search_term = text
        if text:
            self._highlight_search_matches(text)
        else:
            self._clear_search_highlights()
    
    def _highlight_search_matches(self, search_term: str) -> None:
        """Highlight all matches of search term."""
        self._clear_search_highlights()
        
        text = self.preview_text.toPlainText()
        if not text or not search_term:
            return
        
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor('#FFEB3B'))
        highlight_format.setForeground(QColor('#000000'))
        
        cursor = self.preview_text.textCursor()
        cursor.beginEditBlock()
        
        text_lower = text.lower()
        search_lower = search_term.lower()
        
        start = 0
        match_count = 0
        
        while True:
            pos = text_lower.find(search_lower, start)
            if pos == -1:
                break
            
            cursor.setPosition(pos)
            cursor.setPosition(pos + len(search_term), QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(highlight_format)
            
            start = pos + 1
            match_count += 1
        
        cursor.endEditBlock()
        
        if match_count > 0:
            self.title_label.setText(
                f'Document Preview - {match_count} match{"es" if match_count > 1 else ""} found'
            )
        else:
            self.title_label.setText('Document Preview - No matches')
    
    def _clear_search_highlights(self) -> None:
        """Clear search highlight formatting."""
        cursor = self.preview_text.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        
        clear_format = QTextCharFormat()
        clear_format.setBackground(QColor('#FFFFFF'))
        clear_format.setForeground(QColor('#000000'))
        cursor.mergeCharFormat(clear_format)
    
    def _search_next(self) -> None:
        """Search for next match."""
        if self._search_term:
            self.preview_text.find(self._search_term)
    
    def _search_previous(self) -> None:
        """Search for previous match."""
        if self._search_term:
            self.preview_text.find(
                self._search_term,
                QTextDocument.FindFlag.FindBackward
            )
    
    def keyPressEvent(self, event) -> None:
        """Handle key press events for Ctrl+F."""
        if event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.toggle_search()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            if self._search_visible:
                self._hide_search()
                event.accept()
        else:
            super().keyPressEvent(event)
    
    def _on_copy_to_clipboard(self) -> None:
        """Handle copy to clipboard button click."""
        from PySide6.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        markdown = self.get_current_markdown()
        
        if markdown:
            clipboard.setText(markdown)
            logger.info('Copied markdown to clipboard')
        else:
            logger.warning('No markdown to copy')
    
    def _on_save_markdown(self) -> None:
        """Handle save markdown button click."""
        from PySide6.QtWidgets import QFileDialog
        from pathlib import Path
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Save Markdown',
            str(Path.home() / 'document.md'),
            'Markdown Files (*.md);;All Files (*)'
        )
        
        if file_path:
            markdown = self.get_current_markdown()
            if markdown:
                Path(file_path).write_text(markdown, encoding='utf-8')
                logger.info(f'Saved markdown to: {file_path}')
    
    def _on_close_tab(self, index: int) -> None:
        """Handle close tab request."""
        self.tab_widget.removeTab(index)
        
        # If no tabs left, show empty state
        if self.tab_widget.count() == 0:
            self.clear_preview()
        
        logger.info(f'Closed tab at index: {index}')


# Import Path locally to avoid circular import
from pathlib import Path
