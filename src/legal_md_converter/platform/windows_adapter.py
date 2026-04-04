"""
Windows platform adapter.

Handles Windows-specific paths, permissions, and behaviors.
"""

import os
import stat
from pathlib import Path
from typing import Optional

from legal_md_converter.platform.base_adapter import BasePlatformAdapter


class WindowsAdapter(BasePlatformAdapter):
    """Platform adapter for Windows."""
    
    @property
    def platform_name(self) -> str:
        return "Windows"
    
    def get_app_data_dir(self) -> Path:
        """Get Windows application data directory (%LOCALAPPDATA%)."""
        local_app_data = os.environ.get('LOCALAPPDATA')
        if not local_app_data:
            # Fallback if environment variable is missing
            local_app_data = str(Path.home() / 'AppData' / 'Local')
        
        return Path(local_app_data) / self._organization / self._app_name
    
    def get_cache_dir(self) -> Path:
        """Get Windows cache directory."""
        return self.get_app_data_dir() / 'Cache'
    
    def get_config_dir(self) -> Path:
        """Get Windows configuration directory."""
        # Windows typically stores configs in AppData\Roaming
        roaming_app_data = os.environ.get('APPDATA')
        if not roaming_app_data:
            roaming_app_data = str(Path.home() / 'AppData' / 'Roaming')
        
        return Path(roaming_app_data) / self._organization / self._app_name
    
    def get_log_dir(self) -> Path:
        """Get Windows log directory."""
        return self.get_app_data_dir() / 'Logs'
    
    def check_file_permissions(self, file_path: Path, permission: str) -> bool:
        """Check Windows file permissions."""
        if not file_path.exists():
            return False
        
        permission_map = {
            'read': os.R_OK,
            'write': os.W_OK,
            'execute': os.X_OK,
        }
        
        return os.access(str(file_path), permission_map.get(permission, os.R_OK))
    
    def set_file_permissions(self, file_path: Path, permission: str) -> bool:
        """Set Windows file permissions."""
        if not file_path.exists():
            return False
        
        try:
            current_mode = file_path.stat().st_mode
            
            permission_map = {
                'read': stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH,
                'write': stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH,
                'execute': stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
            }
            
            if permission == 'read':
                new_mode = current_mode | permission_map[permission]
            elif permission == 'write':
                new_mode = current_mode | permission_map[permission]
            elif permission == 'execute':
                new_mode = current_mode | permission_map[permission]
            else:
                return False
            
            file_path.chmod(new_mode)
            return True
            
        except OSError:
            return False
    
    def get_system_theme(self) -> str:
        """Detect Windows system theme."""
        try:
            import winreg
            
            registry_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            
            value, _ = winreg.QueryValueEx(registry_key, "AppsUseLightTheme")
            winreg.CloseKey(registry_key)
            
            return 'light' if value == 1 else 'dark'
            
        except (ImportError, OSError):
            return 'light'  # Default to light if detection fails
    
    def get_open_file_filter(self) -> str:
        """Get Windows file dialog filter."""
        return (
            "Legal Documents (*.pdf *.docx *.doc *.rtf *.txt);;"
            "PDF Files (*.pdf);;"
            "Word Documents (*.docx *.doc);;"
            "Rich Text Format (*.rtf);;"
            "Text Files (*.txt);;"
            "All Files (*.*)"
        )
