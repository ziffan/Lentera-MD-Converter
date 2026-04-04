"""
Progress Dialog for Legal-MD-Converter.

Non-blocking, thread-safe progress dialog for long-running operations.
"""

import logging
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from PySide6.QtGui import QFont


logger = logging.getLogger(__name__)


class ProgressDialog(QDialog):
    """
    Non-blocking progress dialog for background operations.
    
    Features:
    - Progress bar with percentage
    - Status message display
    - Cancel button with signal
    - Optional detailed log view
    - Thread-safe updates via signals/slots
    """
    
    # Signals for thread-safe updates
    update_progress = Signal(int, int)  # current, total
    update_message = Signal(str)
    update_detail = Signal(str)
    operation_complete = Signal()
    
    def __init__(
        self,
        title: str = "Processing...",
        cancelable: bool = True,
        show_details: bool = False,
        parent: Optional[QDialog] = None
    ) -> None:
        super().__init__(parent)
        
        self._cancelable = cancelable
        self._show_details = show_details
        self._cancelled = False
        self._current = 0
        self._total = 0
        
        self._setup_ui(title)
        self._connect_signals()
        
        # Set modal properties
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setMinimumWidth(500)
    
    def _setup_ui(self, title: str) -> None:
        """Set up the dialog UI."""
        self.setWindowTitle(title)
        
        layout = QVBoxLayout(self)
        
        # Status message
        self.message_label = QLabel("Starting...")
        self.message_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                padding: 5px;
                color: #333333;
            }
        """)
        layout.addWidget(self.message_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                height: 25px;
                background-color: #f5f5f5;
            }
            
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Progress text
        self.progress_text = QLabel("0 / 0")
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_text.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.progress_text)
        
        # Detail log (optional)
        if self._show_details:
            self.detail_log = QTextEdit()
            self.detail_log.setReadOnly(True)
            self.detail_log.setFont(QFont('Consolas', 10))
            self.detail_log.setMaximumHeight(150)
            self.detail_log.setPlaceholderText("Detailed operation log...")
            layout.addWidget(self.detail_log)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if self._cancelable:
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.clicked.connect(self._on_cancel)
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            button_layout.addWidget(self.cancel_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.close_button.setEnabled(False)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """Connect internal signals to slots."""
        self.update_progress.connect(self._on_update_progress)
        self.update_message.connect(self._on_update_message)
        self.update_detail.connect(self._on_update_detail)
        self.operation_complete.connect(self._on_complete)
    
    @Slot(int, int)
    def _on_update_progress(self, current: int, total: int) -> None:
        """Update progress bar (slot for signal)."""
        self._current = current
        self._total = total
        
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_text.setText(f"{current} / {total}")
        else:
            # Indeterminate mode
            self.progress_bar.setValue(0)
            self.progress_text.setText("Processing...")
    
    @Slot(str)
    def _on_update_message(self, message: str) -> None:
        """Update status message (slot for signal)."""
        self.message_label.setText(message)
    
    @Slot(str)
    def _on_update_detail(self, detail: str) -> None:
        """Update detail log (slot for signal)."""
        if self._show_details and hasattr(self, 'detail_log'):
            self.detail_log.append(detail)
            # Auto-scroll to bottom
            scrollbar = self.detail_log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    @Slot()
    def _on_complete(self) -> None:
        """Handle operation completion."""
        self.progress_bar.setValue(100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                height: 25px;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        self.message_label.setText("Operation completed successfully!")
        
        # Enable close button, disable cancel
        self.close_button.setEnabled(True)
        
        if self._cancelable and hasattr(self, 'cancel_button'):
            self.cancel_button.setEnabled(False)
        
        logger.info("Progress dialog: operation complete")
    
    def set_progress(self, current: int, total: int) -> None:
        """
        Set progress value (thread-safe via signal).
        
        Args:
            current: Current progress value
            total: Total expected value
        """
        self.update_progress.emit(current, total)
    
    def set_message(self, message: str) -> None:
        """
        Set status message (thread-safe via signal).
        
        Args:
            message: Status message to display
        """
        self.update_message.emit(message)
    
    def add_detail(self, detail: str) -> None:
        """
        Add detail log entry (thread-safe via signal).
        
        Args:
            detail: Detail message to append
        """
        self.update_detail.emit(detail)
    
    def complete(self) -> None:
        """Mark operation as complete (thread-safe via signal)."""
        self.operation_complete.emit()
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self._cancelled = True
        self.message_label.setText("Cancelling...")
        
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setEnabled(False)
        
        logger.info("Progress dialog: cancel requested")
    
    def is_cancelled(self) -> bool:
        """
        Check if operation was cancelled.
        
        Returns:
            bool: True if cancelled
        """
        return self._cancelled
    
    def reset(self) -> None:
        """Reset dialog to initial state."""
        self._cancelled = False
        self._current = 0
        self._total = 0
        
        self.progress_bar.setValue(0)
        self.progress_text.setText("0 / 0")
        self.message_label.setText("Starting...")
        
        if self._show_details and hasattr(self, 'detail_log'):
            self.detail_log.clear()
        
        self.close_button.setEnabled(False)
        
        if self._cancelable and hasattr(self, 'cancel_button'):
            self.cancel_button.setEnabled(True)
