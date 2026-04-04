"""
Asset Manager for Legal-MD-Converter.

Manages application assets (databases, icons, models) across platforms
and handles both development and frozen (PyInstaller) modes.
"""

import logging
import shutil
from pathlib import Path
from typing import Optional

import platform
import sys

from legal_md_converter.platform.windows_adapter import WindowsAdapter
from legal_md_converter.platform.macos_adapter import MacOSAdapter
from legal_md_converter.platform.linux_adapter import LinuxAdapter
from legal_md_converter.platform.base_adapter import BasePlatformAdapter


logger = logging.getLogger(__name__)


def is_frozen() -> bool:
    """Check if running as compiled executable (PyInstaller)."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_platform_adapter() -> BasePlatformAdapter:
    """
    Get the appropriate platform adapter for the current OS.
    
    Returns:
        BasePlatformAdapter: Platform-specific adapter instance
    """
    system = platform.system()
    
    if system == "Windows":
        return WindowsAdapter()
    elif system == "Darwin":  # macOS
        return MacOSAdapter()
    else:  # Linux
        return LinuxAdapter()


class AssetManager:
    """
    Manages application assets across platforms and deployment modes.
    
    Handles:
    - Resource bundling in development and frozen modes
    - Cross-platform path resolution
    - Asset extraction and caching
    - Database file management
    - Icon and image resources
    """
    
    # Asset directory names
    ASSET_DIR_NAME = "assets"
    KBBI_DIR_NAME = "kbbi"
    ICONS_DIR_NAME = "icons"
    DOCLING_DIR_NAME = "docling"
    
    KBBI_DB_FILENAME = "kbbi.db"
    APP_ICON_FILENAME = "app_icon.png"
    
    def __init__(self) -> None:
        """Initialize the asset manager."""
        self._platform = get_platform_adapter()
        self._asset_base = self._resolve_asset_base()
        self._initialized = False
        
        logger.info(f"AssetManager initialized on {self._platform.platform_name}")
        logger.info(f"Asset base: {self._asset_base}")
    
    def _resolve_asset_base(self) -> Path:
        """
        Resolve the base asset directory based on deployment mode.
        
        Returns:
            Path: Base directory containing application assets
        """
        if is_frozen():
            # PyInstaller extracts bundled data to _MEIPASS
            return Path(sys._MEIPASS) / self.ASSET_DIR_NAME
        else:
            # Development mode - assets are at project root, not src
            # __file__ -> src/legal_md_converter/data/asset_manager.py
            # .parent.parent.parent.parent -> project root
            return Path(__file__).parent.parent.parent.parent / self.ASSET_DIR_NAME
    
    def get_asset_dir(self) -> Path:
        """
        Get the assets directory.
        
        Returns:
            Path: Path to assets directory
        """
        return self._asset_base
    
    def get_kbbi_db_path(self) -> Path:
        """
        Get path to KBBI SQLite database.
        
        Returns:
            Path: Path to kbbi.db file
        """
        return self._asset_base / self.KBBI_DIR_NAME / self.KBBI_DB_FILENAME
    
    def get_icon_path(self, icon_name: str = APP_ICON_FILENAME) -> Path:
        """
        Get path to an icon file.
        
        Args:
            icon_name: Name of the icon file
            
        Returns:
            Path: Path to icon file
        """
        return self._asset_base / self.ICONS_DIR_NAME / icon_name
    
    def get_docling_model_path(self) -> Path:
        """
        Get path to Docling models cache directory.
        
        Models are stored in platform-specific cache directories,
        not in the bundled assets.
        
        Returns:
            Path: Path to Docling model cache directory
        """
        cache_dir = self._platform.get_cache_dir()
        model_path = cache_dir / self.DOCLING_DIR_NAME / "models"
        model_path.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"Docling model path: {model_path}")
        return model_path
    
    def get_kbbi_db_runtime_path(self) -> Path:
        """
        Get the runtime path for KBBI database.
        
        In frozen mode, copies the database to a writable location
        since PyInstaller bundle is read-only.
        
        Returns:
            Path: Writable path to KBBI database
        """
        if is_frozen():
            # Copy to writable app data directory
            runtime_dir = self._platform.get_app_data_dir() / "data"
            runtime_dir.mkdir(parents=True, exist_ok=True)
            
            runtime_path = runtime_dir / self.KBBI_DB_FILENAME
            source_path = self.get_kbbi_db_path()
            
            # Only copy if source exists and runtime doesn't or is outdated
            if source_path.exists():
                if not runtime_path.exists() or \
                   runtime_path.stat().st_mtime < source_path.stat().st_mtime:
                    shutil.copy2(source_path, runtime_path)
                    logger.info(f"Copied KBBI database to runtime: {runtime_path}")
            
            return runtime_path
        else:
            return self.get_kbbi_db_path()
    
    def ensure_assets_available(self) -> bool:
        """
        Ensure all required assets are available.
        
        Returns:
            bool: True if all assets are available
        """
        try:
            # Check asset base exists
            if not self._asset_base.exists():
                logger.warning(f"Asset directory not found: {self._asset_base}")
                return False
            
            # Create platform-specific directories
            self._platform.ensure_directories()
            
            self._initialized = True
            logger.info("Assets verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure assets: {e}", exc_info=True)
            return False
    
    def get_app_icon_path(self) -> Optional[Path]:
        """
        Get the application icon path.
        
        Returns:
            Optional[Path]: Path to app icon or None
        """
        system = platform.system()
        
        if system == "Windows":
            icon_path = self.get_icon_path("app_icon.ico")
        elif system == "Darwin":
            icon_path = self.get_icon_path("app_icon.icns")
        else:
            icon_path = self.get_icon_path(self.APP_ICON_FILENAME)
        
        return icon_path if icon_path.exists() else None
    
    def list_assets(self, directory: str = "") -> list[Path]:
        """
        List all assets in a directory.
        
        Args:
            directory: Subdirectory within assets to list
            
        Returns:
            list[Path]: List of asset files
        """
        target_dir = self._asset_base / directory if directory else self._asset_base
        
        if not target_dir.exists():
            return []
        
        return [f for f in target_dir.rglob("*") if f.is_file()]
    
    def is_initialized(self) -> bool:
        """
        Check if asset manager is initialized.
        
        Returns:
            bool: True if initialized
        """
        return self._initialized
    
    def get_platform_info(self) -> dict:
        """
        Get platform information.
        
        Returns:
            dict: Platform details
        """
        return {
            'system': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'frozen': is_frozen(),
            'platform': self._platform.platform_name,
        }
