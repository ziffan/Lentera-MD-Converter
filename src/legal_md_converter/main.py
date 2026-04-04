"""
Main entry point for Legal-MD-Converter.

Handles both development and frozen (PyInstaller) modes.
Sets up QApplication with proper high-DPI support.
Initializes logging, platform adapter, and asset manager.
"""

import sys
import logging
from pathlib import Path

from legal_md_converter.data.asset_manager import AssetManager, is_frozen
from legal_md_converter.platform.base_adapter import BasePlatformAdapter
from legal_md_converter.platform.windows_adapter import WindowsAdapter
from legal_md_converter.platform.macos_adapter import MacOSAdapter
from legal_md_converter.platform.linux_adapter import LinuxAdapter


def get_platform_adapter() -> BasePlatformAdapter:
    """Get the appropriate platform adapter."""
    import platform
    
    system = platform.system()
    if system == "Windows":
        return WindowsAdapter()
    elif system == "Darwin":
        return MacOSAdapter()
    else:
        return LinuxAdapter()


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and frozen mode."""
    if is_frozen():
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    
    return base_path / relative_path


def setup_logging() -> None:
    """Initialize logging configuration for debugging."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Use platform adapter for log directory
    platform_adapter = get_platform_adapter()
    log_dir = platform_adapter.get_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'legal-md-converter.log'
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info('Lentera MD starting up...')
    logger.info(f'Platform: {platform_adapter.platform_name}')
    logger.info(f'Log file: {log_file}')
    
    # Initialize asset manager
    try:
        asset_manager = AssetManager()
        asset_manager.ensure_assets_available()
        logger.info('Asset manager initialized')
    except Exception as e:
        logger.warning(f'Asset manager initialization failed: {e}')


def main() -> int:
    """
    Main entry point for the application.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Import PySide6
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        
        # High-DPI support (must be set before creating QApplication)
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName('Lentera-MD')
        app.setApplicationVersion('1.0.0')
        app.setOrganizationName('Lentera-MD-Team')
        
        # Set application-wide font
        font = QFont('Segoe UI', 10)
        app.setFont(font)
        
        # Import main window after QApplication is created
        from legal_md_converter.ui.main_window import MainWindow
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        logger.info('Main window created and shown')
        
        # Execute application
        exit_code = app.exec()
        logger.info(f'Application exited with code: {exit_code}')
        return exit_code
        
    except Exception as e:
        logger.critical(f'Fatal error: {e}', exc_info=True)
        print(f'Fatal error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
