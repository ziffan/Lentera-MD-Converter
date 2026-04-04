"""
Preview Widget for Legal-MD-Converter.

Provides Markdown preview with syntax highlighting and spellcheck error display.
"""

import re
import logging
from typing import Optional, List, Tuple

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QLineEdit,
    QToolBar,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QFont,
    QTextCharFormat,
    QColor,
    QTextCursor,
    QKeySequence,
    QAction,
)


logger = logging.getLogger(__name__)


class PreviewWidget(QWidget):
    """
    Widget for previewing Markdown documents.
    
    Features:
    - Markdown content display
    - Basic syntax highlighting
    - Spellcheck error highlighting (red underline)
    - Search within document (Ctrl+F)
    - Copy to clipboard
    """
    
    # Signals
    search_occurred = Signal(str)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self._spellcheck_errors: List[Tuple[int, int]] = []
        self._current_search_term = ""
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.title_label = QLabel('Markdown Preview')
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                padding: 8px;
                background-color: #f5f5f5;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        toolbar_layout.addWidget(self.title_label)
        
        toolbar_layout.addStretch()
        
        # Word count label
        self.word_count_label = QLabel('0 words')
        self.word_count_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 8px;
            }
        """)
        toolbar_layout.addWidget(self.word_count_label)
        
        layout.addLayout(toolbar_layout)
        
        # Search bar (hidden by default)
        self.search_widget = QWidget()
        self.search_widget.setVisible(False)
        self.search_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
            }
        """)
        
        search_layout = QHBoxLayout(self.search_widget)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in document...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        search_layout.addWidget(self.search_input)
        
        self.search_prev_button = QPushButton("▲")
        self.search_prev_button.setToolTip("Previous match")
        self.search_prev_button.setFixedWidth(30)
        search_layout.addWidget(self.search_prev_button)
        
        self.search_next_button = QPushButton("▼")
        self.search_next_button.setToolTip("Next match")
        self.search_next_button.setFixedWidth(30)
        search_layout.addWidget(self.search_next_button)
        
        self.search_close_button = QPushButton("✕")
        self.search_close_button.setToolTip("Close search")
        self.search_close_button.setFixedWidth(30)
        search_layout.addWidget(self.search_close_button)
        
        layout.addWidget(self.search_widget)
        
        # Preview text edit
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont('Consolas', 11))
        self.preview_text.setPlaceholderText('Converted markdown will appear here...')
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: none;
                padding: 15px;
                selection-background-color: #BBDEFB;
            }
        """)
        layout.addWidget(self.preview_text)
        
        # Empty state label
        self.empty_label = QLabel(
            '<div style="text-align: center; padding: 60px; color: #999999;">'
            '<h2>No Preview Available</h2>'
            '<p>Add legal documents and convert them to see the preview here.</p>'
            '</div>'
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_prev_button.clicked.connect(self._search_previous)
        self.search_next_button.clicked.connect(self._search_next)
        self.search_close_button.clicked.connect(self.hide_search)
    
    def set_content(self, markdown: str, filename: str = "Document") -> None:
        """
        Set the Markdown content to display.
        
        Args:
            markdown: Markdown content
            filename: Source filename for display
        """
        self.preview_text.setPlainText(markdown)
        self.title_label.setText(f'Markdown Preview - {filename}')
        
        # Update word count
        word_count = len(markdown.split())
        self.word_count_label.setText(f'{word_count} words')
        
        # Show preview, hide empty state
        self.preview_text.setVisible(True)
        self.empty_label.setVisible(False)
        
        # Clear any previous spellcheck errors
        self._spellcheck_errors.clear()
        
        logger.info(f'Set preview content for: {filename}')
    
    def clear_preview(self) -> None:
        """Clear all preview content."""
        self.preview_text.clear()
        self.title_label.setText('Markdown Preview')
        self.word_count_label.setText('0 words')
        
        self._spellcheck_errors.clear()
        self.hide_search()
    
    def toggle_search(self) -> None:
        """Toggle search bar visibility."""
        if self.search_widget.isVisible():
            self.hide_search()
        else:
            self.show_search()
    
    def show_search(self) -> None:
        """Show search bar and focus input."""
        self.search_widget.setVisible(True)
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def hide_search(self) -> None:
        """Hide search bar and clear highlights."""
        self.search_widget.setVisible(False)
        self.search_input.clear()
        self._clear_search_highlights()
    
    def highlight_spellcheck_errors(self, typos: List[Tuple[int, int]]) -> None:
        """
        Highlight spellcheck errors in the preview.
        
        Args:
            typos: List of (start, end) positions for errors
        """
        self._spellcheck_errors = typos
        
        # Create error format (red underline)
        error_format = QTextCharFormat()
        error_format.setUnderlineColor(QColor('#F44336'))
        error_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
        
        # Apply to each error range
        cursor = self.preview_text.textCursor()
        
        for start, end in typos:
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(error_format)
        
        logger.info(f'Highlighted {len(typos)} spellcheck errors')
    
    def highlight_typos(self, typos) -> None:
        """
        Highlight typos from SpellCheckResult with red underline.
        
        Handles overlapping ranges correctly by merging.
        
        Args:
            typos: List of TypoMatch objects
        """
        if not typos:
            self.clear_spellcheck_highlights()
            return
        
        # Create error format
        error_format = QTextCharFormat()
        error_format.setUnderlineColor(QColor('#F44336'))
        error_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
        error_format.setToolTip('Kesalahan ejaan')
        
        # Sort by position and merge overlapping ranges
        sorted_typos = sorted(typos, key=lambda t: t.start_pos)
        merged = []
        
        for typo in sorted_typos:
            if merged and typo.start_pos < merged[-1][1]:
                # Overlapping - extend previous range
                merged[-1] = (merged[-1][0], max(merged[-1][1], typo.end_pos))
            else:
                merged.append((typo.start_pos, typo.end_pos))
        
        # Apply highlights
        cursor = self.preview_text.textCursor()
        cursor.beginEditBlock()
        
        for start, end in merged:
            cursor.setPosition(min(start, len(self.preview_text.toPlainText()) - 1))
            cursor.setPosition(min(end, len(self.preview_text.toPlainText())), QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(error_format)
        
        cursor.endEditBlock()
        
        logger.info(f'Highlighted {len(typos)} typos ({len(merged)} merged ranges)')
    
    def clear_spellcheck_highlights(self) -> None:
        """Clear all spellcheck error highlights."""
        self._spellcheck_errors.clear()
        
        # Reset formatting
        cursor = self.preview_text.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        
        clear_format = QTextCharFormat()
        clear_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.NoUnderline)
        cursor.mergeCharFormat(clear_format)
    
    def _on_search_text_changed(self, text: str) -> None:
        """Handle search text change."""
        self._current_search_term = text
        
        if text:
            self._highlight_search_matches(text)
            self.search_occurred.emit(text)
        else:
            self._clear_search_highlights()
    
    def _highlight_search_matches(self, search_term: str) -> None:
        """Highlight all matches of search term."""
        self._clear_search_highlights()
        
        text = self.preview_text.toPlainText()
        if not text or not search_term:
            return
        
        # Create highlight format
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor('#FFEB3B'))
        highlight_format.setForeground(QColor('#000000'))
        
        # Find and highlight all matches
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
        
        # Update title with match count
        if match_count > 0:
            self.title_label.setText(
                f'Markdown Preview - {match_count} match{"es" if match_count > 1 else ""} found'
            )
        else:
            self.title_label.setText('Markdown Preview - No matches')
    
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
        if self._current_search_term:
            self.preview_text.find(self._current_search_term)
    
    def _search_previous(self) -> None:
        """Search for previous match."""
        if self._current_search_term:
            self.preview_text.find(
                self._current_search_term,
                QTextDocument.FindFlag.FindBackward
            )
    
    def get_content(self) -> str:
        """
        Get the current preview content.
        
        Returns:
            str: Markdown content
        """
        return self.preview_text.toPlainText()
    
    def keyPressEvent(self, event) -> None:
        """Handle key press events."""
        # Ctrl+F to toggle search
        if event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.toggle_search()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            if self.search_widget.isVisible():
                self.hide_search()
                event.accept()
        else:
            super().keyPressEvent(event)
