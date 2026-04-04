"""
Briefcase entry point for Lentera MD.

This module is used by Briefcase for cross-platform packaging.
"""

import sys
from pathlib import Path

# Add src to path for development mode
src_path = Path(__file__).parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


def main(args=None):
    """
    Main entry point for Briefcase packaging.
    
    Args:
        args: Command line arguments (defaults to sys.argv)
        
    Returns:
        int: Exit code
    """
    app = QApplication(args or sys.argv)
    
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app.setApplicationName('Lentera MD')
    app.setApplicationVersion('1.0.0')
    app.setOrganizationName('Lentera-MD-Team')
    
    # Application font
    font = QFont('Segoe UI', 10)
    app.setFont(font)
    
    from legal_md_converter.ui.main_window import MainWindow
    
    window = MainWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
