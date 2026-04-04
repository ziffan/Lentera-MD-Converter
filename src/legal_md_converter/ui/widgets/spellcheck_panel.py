"""
Spell Check Panel for Legal-MD-Converter.

Displays detected typos with navigation, replacement, and dictionary management.
"""

import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QComboBox,
    QGroupBox,
    QProgressBar,
    QTextEdit,
    QSplitter,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor


logger = logging.getLogger(__name__)


@dataclass
class TypoMatch:
    """Represents a spelling error with context."""
    word: str
    start_pos: int
    end_pos: int
    suggestions: List[str]
    context: str = ""  # Surrounding text for context
    page_number: int = 0


class SpellCheckPanel(QWidget):
    """
    Panel for displaying and managing spelling errors.
    
    Features:
    - List of detected typos with context
    - Click to navigate to error location
    - Suggestion selection and replacement
    - Ignore/Ignore All buttons
    - Add to Dictionary button
    - Statistics display (word count, error count)
    - Progress bar during checking
    """
    
    # Signals
    navigate_to_position = Signal(int, int)  # start, end
    replace_word = Signal(int, int, str)  # start, end, new_word
    ignore_word = Signal(str)
    ignore_all = Signal(str)
    add_to_dictionary = Signal(str)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self._typos: List[TypoMatch] = []
        self._current_index = -1
        self._total_words = 0
        self._checking = False
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header with statistics
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel('Pemeriksaan Ejaan')
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                padding: 5px;
            }
        """)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Statistics label
        self.stats_label = QLabel('0 kata, 0 kesalahan')
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 5px;
            }
        """)
        header_layout.addWidget(self.stats_label)
        
        layout.addLayout(header_layout)
        
        # Progress bar (shown during checking)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                height: 18px;
                text-align: center;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status message
        self.status_label = QLabel('Siap memeriksa ejaan')
        self.status_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Typo list
        self.typo_list = QListWidget()
        self.typo_list.setAlternatingRowColors(True)
        self.typo_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1565C0;
            }
        """)
        layout.addWidget(self.typo_list)
        
        # Current word display
        word_group = QGroupBox('Kata Saat Ini')
        word_layout = QVBoxLayout(word_group)
        
        self.current_word_label = QLabel('')
        self.current_word_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #F44336;
                padding: 10px;
                background-color: #FFEBEE;
                border-radius: 4px;
                text-align: center;
            }
        """)
        self.current_word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        word_layout.addWidget(self.current_word_label)
        
        # Context text
        self.context_label = QLabel('')
        self.context_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                padding: 5px;
                font-style: italic;
            }
        """)
        self.context_label.setWordWrap(True)
        word_layout.addWidget(self.context_label)
        
        layout.addWidget(word_group)
        
        # Suggestions
        suggestions_group = QGroupBox('Saran Perbaikan')
        suggestions_layout = QVBoxLayout(suggestions_group)
        
        self.suggestions_combo = QComboBox()
        self.suggestions_combo.setMinimumHeight(35)
        self.suggestions_combo.setStyleSheet("""
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
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
        """)
        suggestions_layout.addWidget(self.suggestions_combo)
        
        layout.addWidget(suggestions_group)
        
        # Action buttons
        buttons_layout = QVBoxLayout()
        
        # Replace button
        self.replace_button = QPushButton('Ganti')
        self.replace_button.setToolTip('Ganti kata dengan saran yang dipilih')
        self.replace_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        buttons_layout.addWidget(self.replace_button)
        
        # Button row (Ignore, Ignore All, Add to Dict)
        action_row = QHBoxLayout()
        
        self.ignore_button = QPushButton('Abaikan')
        self.ignore_button.setToolTip('Abaikan kata ini')
        self.ignore_button.setStyleSheet(self._button_style('#757575', '#616161'))
        action_row.addWidget(self.ignore_button)
        
        self.ignore_all_button = QPushButton('Abaikan Semua')
        self.ignore_all_button.setToolTip('Abaikan semua kemunculan kata ini')
        self.ignore_all_button.setStyleSheet(self._button_style('#757575', '#616161'))
        action_row.addWidget(self.ignore_all_button)
        
        self.add_dict_button = QPushButton('Tambah ke Kamus')
        self.add_dict_button.setToolTip('Tambah kata ke kamus pengguna')
        self.add_dict_button.setStyleSheet(self._button_style('#4CAF50', '#388E3C'))
        action_row.addWidget(self.add_dict_button)
        
        buttons_layout.addLayout(action_row)
        
        layout.addLayout(buttons_layout)
        
        # Initial state
        self._update_ui_state()
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.typo_list.currentRowChanged.connect(self._on_typo_selected)
        self.replace_button.clicked.connect(self._on_replace)
        self.ignore_button.clicked.connect(self._on_ignore)
        self.ignore_all_button.clicked.connect(self._on_ignore_all)
        self.add_dict_button.clicked.connect(self._on_add_to_dictionary)
    
    def _button_style(self, bg: str, hover_bg: str) -> str:
        """Generate button stylesheet."""
        return f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
        """
    
    def set_progress(self, current: int, total: int) -> None:
        """
        Update progress bar.
        
        Args:
            current: Current progress
            total: Total items to process
        """
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f'Memeriksa... {current}/{total}')
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FF9800;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        self._checking = True
    
    def set_complete(self, total_words: int, typos: List[TypoMatch]) -> None:
        """
        Set spell check results.
        
        Args:
            total_words: Total word count
            typos: List of typo matches
        """
        self._total_words = total_words
        self._typos = typos
        
        # Hide progress
        self.progress_bar.setVisible(False)
        self._checking = False
        
        # Update statistics
        self.stats_label.setText(f'{total_words} kata, {len(typos)} kesalahan')
        
        if len(typos) == 0:
            self.status_label.setText('✓ Tidak ada kesalahan ejaan')
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
        else:
            self.status_label.setText(f'Ditemukan {len(typos)} kesalahan ejaan')
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #F44336;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
        
        # Populate typo list
        self._populate_typo_list()
        
        logger.info(f'Spell check complete: {len(typos)} errors in {total_words} words')
    
    def _populate_typo_list(self) -> None:
        """Populate the typo list widget."""
        self.typo_list.clear()
        
        for i, typo in enumerate(self._typos):
            item_text = f"{typo.word}"
            if typo.suggestions:
                item_text += f" → {typo.suggestions[0]}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            item.setToolTip(f"Posisi: {typo.start_pos}-{typo.end_pos}")
            
            # Red text for errors
            item.setForeground(QColor('#F44336'))
            
            self.typo_list.addItem(item)
        
        # Select first typo if available
        if self._typos:
            self.typo_list.setCurrentRow(0)
    
    def _on_typo_selected(self, row: int) -> None:
        """Handle typo selection."""
        if row < 0 or row >= len(self._typos):
            return
        
        self._current_index = row
        typo = self._typos[row]
        
        # Update current word display
        self.current_word_label.setText(typo.word)
        
        # Update context
        if typo.context:
            self.context_label.setText(f'...{typo.context}...')
        else:
            self.context_label.setText(f'Posisi: {typo.start_pos}-{typo.end_pos}')
        
        # Populate suggestions
        self.suggestions_combo.clear()
        if typo.suggestions:
            self.suggestions_combo.addItems(typo.suggestions)
        else:
            self.suggestions_combo.addItem('(Tidak ada saran)')
        
        # Enable buttons
        self._update_ui_state()
        
        # Emit navigation signal
        self.navigate_to_position.emit(typo.start_pos, typo.end_pos)
    
    def _on_replace(self) -> None:
        """Handle replace button click."""
        if self._current_index < 0:
            return
        
        typo = self._typos[self._current_index]
        new_word = self.suggestions_combo.currentText()
        
        if not new_word or new_word == '(Tidak ada saran)':
            return
        
        self.replace_word.emit(typo.start_pos, typo.end_pos, new_word)
        
        # Remove from list
        self._typos.pop(self._current_index)
        self.typo_list.takeItem(self._current_index)
        
        # Update stats
        self.stats_label.setText(f'{self._total_words} kata, {len(self._typos)} kesalahan')
        
        # Select next typo
        if self._typos:
            next_row = min(self._current_index, len(self._typos) - 1)
            self.typo_list.setCurrentRow(next_row)
        else:
            self.status_label.setText('✓ Tidak ada kesalahan ejaan')
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            self.current_word_label.setText('')
            self.context_label.setText('')
        
        logger.info(f'Replaced "{typo.word}" with "{new_word}"')
    
    def _on_ignore(self) -> None:
        """Handle ignore button click."""
        if self._current_index < 0:
            return
        
        typo = self._typos[self._current_index]
        self.ignore_word.emit(typo.word)
        
        # Remove from list
        self._typos.pop(self._current_index)
        self.typo_list.takeItem(self._current_index)
        
        # Update stats
        self.stats_label.setText(f'{self._total_words} kata, {len(self._typos)} kesalahan')
        
        # Select next typo
        if self._typos:
            next_row = min(self._current_index, len(self._typos) - 1)
            self.typo_list.setCurrentRow(next_row)
        
        logger.info(f'Ignored word: {typo.word}')
    
    def _on_ignore_all(self) -> None:
        """Handle ignore all button click."""
        if self._current_index < 0:
            return
        
        typo = self._typos[self._current_index]
        self.ignore_all.emit(typo.word)
        
        # Remove all instances of this word
        self._typos = [t for t in self._typos if t.word.lower() != typo.word.lower()]
        self._populate_typo_list()
        
        # Update stats
        self.stats_label.setText(f'{self._total_words} kata, {len(self._typos)} kesalahan')
        
        logger.info(f'Ignored all instances of: {typo.word}')
    
    def _on_add_to_dictionary(self) -> None:
        """Handle add to dictionary button click."""
        if self._current_index < 0:
            return
        
        typo = self._typos[self._current_index]
        self.add_to_dictionary.emit(typo.word)
        
        # Remove from list
        self._typos.pop(self._current_index)
        self.typo_list.takeItem(self._current_index)
        
        # Update stats
        self.stats_label.setText(f'{self._total_words} kata, {len(self._typos)} kesalahan')
        
        logger.info(f'Added to dictionary: {typo.word}')
    
    def _update_ui_state(self) -> None:
        """Update UI element enabled states."""
        has_selection = self._current_index >= 0
        has_suggestions = (
            self.suggestions_combo.count() > 0 and
            self.suggestions_combo.currentText() != '(Tidak ada saran)'
        )
        
        self.replace_button.setEnabled(has_selection and has_suggestions)
        self.ignore_button.setEnabled(has_selection)
        self.ignore_all_button.setEnabled(has_selection)
        self.add_dict_button.setEnabled(has_selection)
    
    def clear(self) -> None:
        """Clear all data from the panel."""
        self._typos.clear()
        self._current_index = -1
        self._total_words = 0
        
        self.typo_list.clear()
        self.current_word_label.setText('')
        self.context_label.setText('')
        self.suggestions_combo.clear()
        self.stats_label.setText('0 kata, 0 kesalahan')
        self.status_label.setText('Siap memeriksa ejaan')
        self.progress_bar.setVisible(False)
        self._checking = False
        
        self._update_ui_state()
    
    def is_checking(self) -> bool:
        """Check if spell check is in progress."""
        return self._checking
    
    def get_typo_count(self) -> int:
        """Get number of detected typos."""
        return len(self._typos)
    
    def get_total_words(self) -> int:
        """Get total word count."""
        return self._total_words
