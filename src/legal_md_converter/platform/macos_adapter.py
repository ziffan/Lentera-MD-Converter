"""
macOS platform adapter.

Handles macOS-specific paths, sandboxing, and behaviors.
"""

import os
import stat
from pathlib import Path
from typing import Optional

from legal_md_converter.platform.base_adapter import BasePlatformAdapter


class MacOSAdapter(BasePlatformAdapter):
    """Platform adapter for macOS."""
    
    @property
    def platform_name(self) -> str:
        return "macOS"
    
    def get_app_data_dir(self) -> Path:
        """Get macOS application data directory (Application Support)."""
        return Path.home() / 'Library' / 'Application Support' / self._app_name
    
    def get_cache_dir(self) -> Path:
        """Get macOS cache directory."""
        return Path.home() / 'Library' / 'Caches' / self._app_name
    
    def get_config_dir(self) -> Path:
        """Get macOS configuration directory."""
        # macOS apps typically store configs in Application Support or ~/.config
        return Path.home() / 'Library' / 'Preferences' / self._app_name
    
    def get_log_dir(self) -> Path:
        """Get macOS log directory."""
        return Path.home() / 'Library' / 'Logs' / self._app_name
    
    def check_file_permissions(self, file_path: Path, permission: str) -> bool:
        """Check macOS file permissions."""
        if not file_path.exists():
            return False
        
        permission_map = {
            'read': os.R_OK,
            'write': os.W_OK,
            'execute': os.X_OK,
        }
        
        return os.access(str(file_path), permission_map.get(permission, os.R_OK))
    
    def set_file_permissions(self, file_path: Path, permission: str) -> bool:
        """Set macOS file permissions."""
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
        """Detect macOS system theme (Dark Mode)."""
        try:
            import subprocess
            
            # Check macOS dark mode setting
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Returns 'Dark' if dark mode is enabled
            return 'dark' if result.stdout.strip() == 'Dark' else 'light'
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return 'light'  # Default to light if detection fails
    
    def get_open_file_filter(self) -> str:
        """Get macOS file dialog filter."""
        return (
            "Legal Documents (*.pdf *.docx *.doc *.rtf *.txt);;"
            "PDF Files (*.pdf);;"
            "Word Documents (*.docx *.doc);;"
            "Rich Text Format (*.rtf);;"
            "Text Files (*.txt);;"
            "All Files (*)"
        )
    
    def check_sandbox_permissions(self) -> bool:
        """
        Check if app is running in macOS sandbox with proper permissions.
        
        Returns:
            bool: True if sandbox permissions are valid
        """
        try:
            # Check if running as sandboxed app
            sandbox_dir = Path.home() / 'Library' / 'Containers'
            app_bundle = f'com.legalmd.{self._app_name}'.lower()
            
            return (sandbox_dir / app_bundle).exists()
            
        except Exception:
            return False
