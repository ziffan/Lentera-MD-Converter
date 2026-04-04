"""
Base platform adapter - Abstract interface for cross-platform operations.

Defines the contract that all platform-specific adapters must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any


class BasePlatformAdapter(ABC):
    """
    Abstract base class for platform-specific operations.
    
    Provides a unified interface for:
    - Application data paths
    - Cache directories
    - Permission handling
    - OS-specific behaviors
    """
    
    def __init__(self) -> None:
        """Initialize the platform adapter."""
        self._app_name = "LegalMDConverter"
        self._organization = "Legal-MD-Team"
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform name."""
        pass
    
    @abstractmethod
    def get_app_data_dir(self) -> Path:
        """
        Get the application data directory.
        
        Returns:
            Path: Platform-specific application data directory
        """
        pass
    
    @abstractmethod
    def get_cache_dir(self) -> Path:
        """
        Get the application cache directory.
        
        Returns:
            Path: Platform-specific cache directory
        """
        pass
    
    @abstractmethod
    def get_config_dir(self) -> Path:
        """
        Get the application configuration directory.
        
        Returns:
            Path: Platform-specific config directory
        """
        pass
    
    @abstractmethod
    def get_log_dir(self) -> Path:
        """
        Get the application log directory.
        
        Returns:
            Path: Platform-specific log directory
        """
        pass
    
    def ensure_directories(self) -> Dict[str, Path]:
        """
        Create and return all required application directories.
        
        Returns:
            Dict[str, Path]: Dictionary of directory names to paths
        """
        dirs = {
            'data': self.get_app_data_dir(),
            'cache': self.get_cache_dir(),
            'config': self.get_config_dir(),
            'logs': self.get_log_dir(),
        }
        
        for path in dirs.values():
            path.mkdir(parents=True, exist_ok=True)
        
        return dirs
    
    @abstractmethod
    def check_file_permissions(self, file_path: Path, permission: str) -> bool:
        """
        Check file permissions for a given file.
        
        Args:
            file_path: Path to the file
            permission: Permission to check ('read', 'write', 'execute')
            
        Returns:
            bool: True if the permission is granted
        """
        pass
    
    @abstractmethod
    def set_file_permissions(self, file_path: Path, permission: str) -> bool:
        """
        Set file permissions for a given file.
        
        Args:
            file_path: Path to the file
            permission: Permission to set ('read', 'write', 'execute')
            
        Returns:
            bool: True if the permission was successfully set
        """
        pass
    
    @abstractmethod
    def get_system_theme(self) -> str:
        """
        Detect the system theme (light/dark).
        
        Returns:
            str: 'light' or 'dark'
        """
        pass
    
    @abstractmethod
    def get_open_file_filter(self) -> str:
        """
        Get the platform-specific file dialog filter string.
        
        Returns:
            str: File filter string for QFileDialog
        """
        pass
    
    def get_app_info(self) -> Dict[str, Any]:
        """
        Get application information.
        
        Returns:
            Dict[str, Any]: Dictionary with app info
        """
        return {
            'app_name': self._app_name,
            'organization': self._organization,
            'platform': self.platform_name,
        }
    
    def validate_environment(self) -> bool:
        """
        Validate that the platform environment is suitable.
        
        Returns:
            bool: True if environment is valid
        """
        try:
            self.ensure_directories()
            return True
        except Exception:
            return False
