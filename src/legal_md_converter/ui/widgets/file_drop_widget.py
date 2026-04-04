"""
File drop widget for Legal-MD-Converter.

Provides a drag-and-drop area for adding legal documents to the converter.
Uses QTreeWidget for file list display per spec.
"""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QFileDialog,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent


logger = logging.getLogger(__name__)


class FileDropWidget(QWidget):
    """Widget for drag-and-drop file management."""
    
    # Signals
    files_dropped = Signal(list)
    file_removed = Signal(str)
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.rtf', '.txt'}
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self._files: list[str] = []
        
        self._setup_ui()
        self._connect_signals()
        
        self.setAcceptDrops(True)
    
    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        
        # Drop area label
        self.drop_label = QLabel('Drag & Drop Legal Documents Here\n\nSupported: PDF, DOCX, DOC, RTF, TXT')
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setStyleSheet('''
            QLabel {
                background-color: #f5f5f5;
                border: 2px dashed #cccccc;
                border-radius: 8px;
                padding: 40px;
                color: #666666;
                font-size: 14px;
            }
            QLabel:hover {
                background-color: #e8f4fd;
                border-color: #2196F3;
                color: #2196F3;
            }
        ''')
        layout.addWidget(self.drop_label)
        
        # Button layout
        button_layout = QVBoxLayout()
        
        self.add_files_button = QPushButton('Add Files...')
        self.add_files_button.setToolTip('Select files to add')
        button_layout.addWidget(self.add_files_button)
        
        self.clear_button = QPushButton('Clear All')
        self.clear_button.setToolTip('Remove all files from the list')
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # File tree (QTreeWidget per spec)
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(['Nama File', 'Tipe', 'Ukuran'])
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setRootIsDecorated(False)
        layout.addWidget(self.file_tree)
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.add_files_button.clicked.connect(self._on_add_files)
        self.clear_button.clicked.connect(self.clear_files)
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_label.setStyleSheet('''
                QLabel {
                    background-color: #e8f4fd;
                    border: 2px dashed #2196F3;
                    border-radius: 8px;
                    padding: 40px;
                    color: #2196F3;
                    font-size: 14px;
                }
            ''')
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event) -> None:
        """Handle drag leave event."""
        self.drop_label.setStyleSheet('''
            QLabel {
                background-color: #f5f5f5;
                border: 2px dashed #cccccc;
                border-radius: 8px;
                padding: 40px;
                color: #666666;
                font-size: 14px;
            }
        ''')
    
    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop event."""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.add_files(files)
        self.files_dropped.emit(files)
        
        # Reset style
        self.drop_label.setStyleSheet('''
            QLabel {
                background-color: #f5f5f5;
                border: 2px dashed #cccccc;
                border-radius: 8px;
                padding: 40px;
                color: #666666;
                font-size: 14px;
            }
        ''')
    
    def _get_file_size_human(self, file_path: Path) -> str:
        """Get human-readable file size."""
        size = file_path.stat().st_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 ** 2):.1f} MB"
    
    def add_files(self, files: list[str]) -> None:
        """Add files to the list."""
        for file_path in files:
            path = Path(file_path)
            
            # Check if file is supported
            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                logger.warning(f'Unsupported file type: {file_path}')
                continue
            
            # Check for duplicates
            if file_path in self._files:
                continue
            
            if path.is_file():
                self._files.append(file_path)
                
                # Add to tree widget
                item = QTreeWidgetItem([
                    path.name,
                    path.suffix.upper().lstrip('.'),
                    self._get_file_size_human(path),
                ])
                item.setToolTip(0, str(path))
                item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                self.file_tree.addTopLevelItem(item)
        
        logger.info(f'Added {len(files)} files, total: {len(self._files)}')
    
    def clear_files(self) -> None:
        """Clear all files from the widget."""
        self._files.clear()
        self.file_tree.clear()
        logger.info('Cleared all files')
    
    def remove_file(self, index: int) -> None:
        """Remove a file at the specified index."""
        if 0 <= index < len(self._files):
            file_path = self._files.pop(index)
            item = self.file_tree.takeTopLevelItem(index)
            if item:
                del item
            self.file_removed.emit(file_path)
            logger.info(f'Removed file: {file_path}')
    
    def get_files(self) -> list[str]:
        """Get list of current file paths."""
        return self._files.copy()
    
    def file_count(self) -> int:
        """Get the number of files."""
        return len(self._files)
    
    def _on_add_files(self) -> None:
        """Handle add files button click."""
        file_filter = (
            'Legal Documents (*.pdf *.docx *.doc *.rtf *.txt);;'
            'All Files (*)'
        )
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            'Add Legal Documents',
            str(Path.home()),
            file_filter
        )
        
        if files:
            self.add_files(files)
            self.files_dropped.emit(files)
