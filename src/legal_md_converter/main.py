"""
Main entry point for Legal-MD-Converter.

Handles both development and frozen (PyInstaller) modes.
Sets up QApplication with proper high-DPI support.
Initializes logging, platform adapter, and asset manager.
"""

import sys
import os

# When run as a script, Python inserts this file's directory into sys.path[0],
# which causes the local 'platform/' subpackage to shadow the stdlib 'platform' module.
# Remove it so all stdlib imports resolve correctly. The package itself is accessible
# via the installed editable install (pip install -e .).
_this_dir = os.path.dirname(os.path.abspath(__file__))
if sys.path and os.path.normcase(sys.path[0]) == os.path.normcase(_this_dir):
    sys.path.pop(0)

import logging
import shutil
from pathlib import Path

from legal_md_converter.data.asset_manager import AssetManager, is_frozen


def _fix_hf_symlinks() -> None:
    """
    Di Windows, PyInstaller frozen binary tidak bisa mengikuti symlink relatif
    yang dibuat oleh huggingface_hub di cache. Fungsi ini mengganti semua symlink
    di HuggingFace hub cache dengan salinan file nyata, sehingga docling dapat
    membaca model tanpa error.

    Hanya berjalan di frozen app (PyInstaller), tidak di development mode.
    """
    if not is_frozen():
        return
    import platform as _plat
    if _plat.system() != 'Windows':
        return

    log = logging.getLogger(__name__)

    # Lokasi HuggingFace hub cache
    hf_home = os.environ.get('HF_HOME', '')
    if hf_home:
        hf_hub_cache = Path(hf_home) / 'hub'
    else:
        hf_hub_cache = Path.home() / '.cache' / 'huggingface' / 'hub'

    if not hf_hub_cache.exists():
        return

    fixed = 0
    for model_dir in hf_hub_cache.iterdir():
        if not model_dir.is_dir():
            continue
        snapshots_dir = model_dir / 'snapshots'
        if not snapshots_dir.exists():
            continue
        for snapshot in snapshots_dir.iterdir():
            if not snapshot.is_dir():
                continue
            for link in snapshot.iterdir():
                if not link.is_symlink():
                    continue
                # Jika symlink tidak bisa diakses sebagai file, ganti dengan salinan
                if link.is_file():
                    continue  # sudah bisa diakses, lewati
                try:
                    raw_target = os.readlink(str(link))
                    target = Path(raw_target)
                    if not target.is_absolute():
                        target = (link.parent / target).resolve()
                    if target.is_file():
                        link.unlink()
                        shutil.copy2(str(target), str(link))
                        fixed += 1
                        log.debug(f'HF symlink fixed: {link.name}')
                except Exception as exc:
                    log.debug(f'HF symlink fix skipped ({link.name}): {exc}')

    if fixed:
        log.info(f'Fixed {fixed} HuggingFace cache symlink(s) for frozen app compatibility')
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

    # Perbaiki symlink HuggingFace cache agar model dapat dibaca di frozen app
    _fix_hf_symlinks()

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
    # Pesan konsol untuk pengguna
    print("=" * 60)
    print("  Lentera MD — Konverter Dokumen Hukum Indonesia")
    print("=" * 60)
    print()
    print("  Jendela terminal ini berjalan bersamaan dengan aplikasi.")
    print("  Ini adalah hal NORMAL — jangan ditutup selama aplikasi")
    print("  masih digunakan.")
    print()
    print("  Jika terjadi error atau aplikasi tidak merespons:")
    print("    1. Tutup aplikasi")
    print("    2. Buka kembali aplikasi")
    print("    3. Jika masalah berlanjut, hubungi pengembang:")
    print("       https://github.com/ziffan/Lentera-MD-Converter/issues")
    print()
    print("  Terminal ini akan otomatis tertutup saat aplikasi ditutup.")
    print("=" * 60)
    print()

    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Import PySide6
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont, QIcon

        # High-DPI support (must be set before creating QApplication)
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName('Lentera-MD')
        app.setApplicationVersion('1.0.0')
        app.setOrganizationName('Lentera-MD-Team')

        # Set application icon (shows in taskbar / title bar)
        import platform as _plat
        _icon_dir = Path(__file__).parent.parent.parent / 'assets' / 'icons'
        if _plat.system() == 'Darwin':
            _icon_path = _icon_dir / 'app_icon.icns'
        elif _plat.system() == 'Windows':
            _icon_path = _icon_dir / 'app_icon.ico'
        else:
            _icon_path = _icon_dir / 'app_icon.png'
        if _icon_path.exists():
            app.setWindowIcon(QIcon(str(_icon_path)))

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
