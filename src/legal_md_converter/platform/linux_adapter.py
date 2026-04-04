"""
Linux platform adapter.

Handles Linux-specific paths, permissions, and behaviors.
"""

import os
import stat
from pathlib import Path
from typing import Optional

from legal_md_converter.platform.base_adapter import BasePlatformAdapter


class LinuxAdapter(BasePlatformAdapter):
    """Platform adapter for Linux."""
    
    @property
    def platform_name(self) -> str:
        return "Linux"
    
    def get_app_data_dir(self) -> Path:
        """Get Linux application data directory (~/.local/share)."""
        return Path.home() / '.local' / 'share' / self._app_name
    
    def get_cache_dir(self) -> Path:
        """Get Linux cache directory (~/.cache)."""
        return Path.home() / '.cache' / self._app_name
    
    def get_config_dir(self) -> Path:
        """Get Linux configuration directory (~/.config)."""
        return Path.home() / '.config' / self._app_name
    
    def get_log_dir(self) -> Path:
        """Get Linux log directory."""
        return Path.home() / '.local' / 'share' / self._app_name / 'Logs'
    
    def check_file_permissions(self, file_path: Path, permission: str) -> bool:
        """Check Linux file permissions."""
        if not file_path.exists():
            return False
        
        permission_map = {
            'read': os.R_OK,
            'write': os.W_OK,
            'execute': os.X_OK,
        }
        
        return os.access(str(file_path), permission_map.get(permission, os.R_OK))
    
    def set_file_permissions(self, file_path: Path, permission: str) -> bool:
        """Set Linux file permissions."""
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
        """
        Detect Linux system theme.
        
        Tries to detect GTK theme preference.
        """
        try:
            # Try to detect GTK theme preference
            import subprocess
            
            # Check GNOME theme
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                theme_name = result.stdout.strip().lower().strip("'\"")
                
                # Common dark theme names
                dark_themes = ['adwaita-dark', 'yaru-dark', 'arc-dark', 'breeze-dark', 
                              ' Materia-dark', 'numix-dark']
                
                for dark_theme in dark_themes:
                    if dark_theme in theme_name:
                        return 'dark'
                
                # Check if theme name contains 'dark'
                if 'dark' in theme_name:
                    return 'dark'
            
            return 'light'
            
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            return 'light'  # Default to light if detection fails
    
    def get_open_file_filter(self) -> str:
        """Get Linux file dialog filter."""
        return (
            "Legal Documents (*.pdf *.docx *.doc *.rtf *.txt);;"
            "PDF Files (*.pdf);;"
            "Word Documents (*.docx *.doc);;"
            "Rich Text Format (*.rtf);;"
            "Text Files (*.txt);;"
            "All Files (*)"
        )
