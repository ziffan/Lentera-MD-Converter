"""
Path utilities for Legal-MD-Converter.

Provides pathlib wrappers and cross-platform path handling utilities.
"""

import os
import logging
from pathlib import Path
from typing import Optional

import platform


logger = logging.getLogger(__name__)


def get_home_directory() -> Path:
    """
    Get the user's home directory.
    
    Returns:
        Path: User home directory path
    """
    return Path.home()


def get_desktop_directory() -> Optional[Path]:
    """
    Get the user's desktop directory.
    
    Returns:
        Optional[Path]: Desktop directory or None if not found
    """
    system = platform.system()
    
    if system == "Windows":
        return Path.home() / "Desktop"
    elif system == "Darwin":
        return Path.home() / "Desktop"
    else:  # Linux
        # Check XDG user-dirs
        xdg_config = Path.home() / ".config" / "user-dirs.dirs"
        if xdg_config.exists():
            try:
                with open(xdg_config, 'r') as f:
                    for line in f:
                        if line.startswith("XDG_DEKTOP_DIR"):
                            path_str = line.split("=")[1].strip().strip('"')
                            path_str = path_str.replace("$HOME/", "")
                            return Path.home() / path_str
            except Exception:
                pass
        
        return Path.home() / "Desktop"


def validate_file_path(file_path: str) -> Optional[Path]:
    """
    Validate and normalize a file path.
    
    Args:
        file_path: File path string to validate
        
    Returns:
        Optional[Path]: Normalized Path or None if invalid
    """
    try:
        path = Path(file_path).resolve()
        
        if not path.exists():
            logger.warning(f"Path does not exist: {file_path}")
            return None
        
        if not path.is_file():
            logger.warning(f"Path is not a file: {file_path}")
            return None
        
        return path
        
    except (OSError, ValueError) as e:
        logger.error(f"Invalid file path: {file_path} - {e}")
        return None


def validate_directory_path(dir_path: str) -> Optional[Path]:
    """
    Validate and normalize a directory path.
    
    Args:
        dir_path: Directory path string to validate
        
    Returns:
        Optional[Path]: Normalized Path or None if invalid
    """
    try:
        path = Path(dir_path).resolve()
        
        if not path.exists():
            logger.warning(f"Directory does not exist: {dir_path}")
            return None
        
        if not path.is_dir():
            logger.warning(f"Path is not a directory: {dir_path}")
            return None
        
        return path
        
    except (OSError, ValueError) as e:
        logger.error(f"Invalid directory path: {dir_path} - {e}")
        return None


def create_safe_filename(base_name: str, extension: str = ".md") -> str:
    """
    Create a safe filename by removing invalid characters.
    
    Args:
        base_name: Base filename without extension
        extension: File extension (default: .md)
        
    Returns:
        str: Safe filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    safe_name = base_name
    
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Trim length
    max_length = 200
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length]
    
    return f"{safe_name}{extension}"


def get_unique_filepath(directory: Path, base_name: str, extension: str = ".md") -> Path:
    """
    Get a unique file path by appending a number if file exists.
    
    Args:
        directory: Target directory
        base_name: Base filename
        extension: File extension
        
    Returns:
        Path: Unique file path that doesn't exist
    """
    safe_name = create_safe_filename(base_name, extension)
    target_path = directory / safe_name
    
    if not target_path.exists():
        return target_path
    
    # Add numeric suffix
    counter = 1
    name_without_ext = Path(safe_name).stem
    
    while True:
        new_name = f"{name_without_ext}_{counter}{extension}"
        target_path = directory / new_name
        
        if not target_path.exists():
            return target_path
        
        counter += 1


def get_file_size_human_readable(file_path: Path) -> str:
    """
    Get human-readable file size.
    
    Args:
        file_path: Path to file
        
    Returns:
        str: Human-readable size (e.g., "1.5 MB")
    """
    if not file_path.exists():
        return "0 B"
    
    size_bytes = file_path.stat().st_size
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.1f} GB"


def normalize_line_endings(text: str, platform: Optional[str] = None) -> str:
    """
    Normalize line endings based on platform.
    
    Args:
        text: Text to normalize
        platform: Target platform ('windows', 'unix', 'mac'). 
                  Defaults to current platform.
    
    Returns:
        str: Text with normalized line endings
    """
    if platform is None:
        platform = platform.system().lower()
    
    # First normalize all to \n
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Then convert to target platform
    if platform == 'windows':
        return text.replace('\n', '\r\n')
    else:  # Unix/macOS
        return text


def safe_path_join(*parts: str) -> Path:
    """
    Safely join path parts and normalize.
    
    Args:
        *parts: Path components to join
        
    Returns:
        Path: Normalized path
    """
    return Path(*parts).resolve()


def is_path_safe(file_path: Path, base_directory: Path) -> bool:
    """
    Check if a path is safely within a base directory (prevents path traversal).
    
    Args:
        file_path: Path to check
        base_directory: Base directory that should contain the path
        
    Returns:
        bool: True if path is safely within base directory
    """
    try:
        file_path.resolve().relative_to(base_directory.resolve())
        return True
    except ValueError:
        return False


def get_temp_directory() -> Path:
    """
    Get the system temporary directory.
    
    Returns:
        Path: Temporary directory path
    """
    return Path(os.environ.get('TEMP', os.environ.get('TMP', '/tmp')))


def get_supported_file_extensions() -> list[str]:
    """
    Get list of supported file extensions.
    
    Returns:
        list[str]: Supported file extensions
    """
    return ['.pdf', '.docx', '.doc', '.rtf', '.txt']


def is_supported_file(file_path: Path) -> bool:
    """
    Check if a file has a supported extension.
    
    Args:
        file_path: Path to check
        
    Returns:
        bool: True if file type is supported
    """
    return file_path.suffix.lower() in get_supported_file_extensions()
