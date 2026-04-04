#!/usr/bin/env python3
"""
Cross-platform build script for Lentera MD.

Usage:
    python build_app.py           # Build for current platform
    python build_app.py --onedir  # Build directory bundle
    python build_app.py --help    # Show help
"""

import sys
import platform
import argparse
from pathlib import Path

try:
    from PyInstaller.__main__ import run as pyinstaller_run
except ImportError:
    print("PyInstaller not installed. Install with: pip install pyinstaller")
    sys.exit(1)


def get_build_args(onedir: bool = False) -> list[str]:
    """Get platform-specific PyInstaller arguments."""
    system = platform.system()

    base_args = [
        '--name=LenteraMD',
        '--clean',
        f'--distpath=dist/{system.lower()}',
        f'--workpath=build/{system.lower()}/temp',
        '--specpath=.',
    ]

    if onedir:
        base_args.append('--onedir')
    else:
        base_args.append('--onefile')
        base_args.append('--windowed')  # GUI app, no console

    # Add icon based on platform
    icon_path = Path('assets/icons')
    if system == 'Windows':
        icon_file = icon_path / 'app_icon.ico'
        if icon_file.exists():
            base_args.extend(['--icon', str(icon_file)])
    elif system == 'Darwin':
        icon_file = icon_path / 'app_icon.icns'
        if icon_file.exists():
            base_args.extend(['--icon', str(icon_file)])
        base_args.append('--osx-bundle-identifier=com.lenteramd.app')
    else:
        icon_file = icon_path / 'app_icon.png'
        if icon_file.exists():
            base_args.extend(['--icon', str(icon_file)])

    return base_args


def get_data_files() -> list[tuple[str, str]]:
    """Get data files to include in the package."""
    data = []
    
    assets_dir = Path('assets')
    if assets_dir.exists():
        data.append(('assets', 'assets'))
    
    return data


def get_hidden_imports() -> list[str]:
    """Get all required hidden imports."""
    return [
        # PySide6 core
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtPrintSupport',
        # Docling
        'docling',
        'docling.document_converter',
        'docling.datamodel.base_models',
        'docling.datamodel.pipeline_options',
        # Database
        'sqlite3',
    ]


def check_dependencies() -> None:
    """Check if required build dependencies are installed."""
    missing = []
    
    try:
        import PySide6
    except ImportError:
        missing.append('PySide6')
    
    try:
        import docling
    except ImportError:
        missing.append('docling')
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        sys.exit(1)
    
    print("✓ All build dependencies available")


def build(onedir: bool = False) -> None:
    """Run the build process."""
    check_dependencies()
    
    args = get_build_args(onedir=onedir)
    
    # Add data files
    for src, dest in get_data_files():
        separator = ';' if platform.system() == 'Windows' else ':'
        args.extend(['--add-data', f'{src}{separator}{dest}'])
    
    # Add hidden imports
    for imp in get_hidden_imports():
        args.extend(['--hidden-import', imp])
    
    # Add main script
    args.append('src/legal_md_converter/main.py')
    
    system = platform.system()
    print(f"\n{'='*60}")
    print(f"Building Lentera MD for {system}")
    print(f"Mode: {'OneDir' if onedir else 'OneFile'}")
    print(f"{'='*60}\n")
    
    pyinstaller_run(args)
    
    print(f"\n{'='*60}")
    print(f"Build complete! Output in: dist/{system.lower()}/")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Build Lentera MD executable')
    parser.add_argument('--onedir', action='store_true', help='Build directory bundle instead of single file')
    args = parser.parse_args()
    
    build(onedir=args.onedir)


if __name__ == '__main__':
    main()
