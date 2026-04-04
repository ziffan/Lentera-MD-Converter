"""
Dependency checker for Legal-MD-Converter.

Validates that all required system dependencies and Python packages
are installed and functional.
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, List, Dict, Any

import platform


logger = logging.getLogger(__name__)


class DependencyChecker:
    """
    Checks and reports on required dependencies.
    
    Features:
    - Python package validation
    - System dependency detection (Tesseract, Poppler)
    - Cross-platform awareness
    - Installation guidance
    """
    
    # Required Python packages
    REQUIRED_PACKAGES = [
        'PySide6',
        'docling',
    ]
    
    # Optional Python packages
    OPTIONAL_PACKAGES = [
        'bloom_filter2',  # For spellcheck optimization
        'pytest',          # For testing
        'pytest-qt',       # For Qt testing
    ]
    
    # System dependencies by platform
    SYSTEM_DEPS = {
        'Linux': {
            'tesseract': {
                'required': False,
                'check_command': 'tesseract --version',
                'install_command': 'sudo apt install tesseract-ocr tesseract-ocr-ind',
                'description': 'OCR engine untuk dokumen scan',
            },
            'pdftotext': {
                'required': False,
                'check_command': 'pdftotext -v',
                'install_command': 'sudo apt install poppler-utils',
                'description': 'PDF text extraction utility',
            },
        },
        'Darwin': {
            'tesseract': {
                'required': False,
                'check_command': 'tesseract --version',
                'install_command': 'brew install tesseract',
                'description': 'OCR engine untuk dokumen scan',
            },
        },
        'Windows': {
            'tesseract': {
                'required': False,
                'check_command': 'tesseract --version',
                'install_command': 'Unduh dari https://github.com/UB-Mannheim/tesseract/wiki',
                'description': 'OCR engine untuk dokumen scan',
            },
        },
    }
    
    @staticmethod
    def check_python_packages() -> Dict[str, Any]:
        """
        Check if required Python packages are installed.
        
        Returns:
            Dict[str, Any]: {
                'installed': List[str],
                'missing': List[str],
                'optional_installed': List[str],
                'optional_missing': List[str],
            }
        """
        import importlib
        
        result = {
            'installed': [],
            'missing': [],
            'optional_installed': [],
            'optional_missing': [],
        }
        
        # Check required packages
        for package in DependencyChecker.REQUIRED_PACKAGES:
            try:
                importlib.import_module(package)
                result['installed'].append(package)
            except ImportError:
                result['missing'].append(package)
        
        # Check optional packages
        for package in DependencyChecker.OPTIONAL_PACKAGES:
            try:
                importlib.import_module(package.replace('-', '_'))
                result['optional_installed'].append(package)
            except ImportError:
                result['optional_missing'].append(package)
        
        return result
    
    @staticmethod
    def check_system_dependencies() -> Dict[str, Any]:
        """
        Check if system dependencies are available.
        
        Returns:
            Dict[str, Any]: {
                'available': List[dict],
                'missing': List[dict],
            }
        """
        system = platform.system()
        deps = DependencyChecker.SYSTEM_DEPS.get(system, {})
        
        result = {
            'available': [],
            'missing': [],
        }
        
        for dep_name, dep_info in deps.items():
            is_available = DependencyChecker._check_command(dep_info['check_command'])
            
            info = {
                'name': dep_name,
                'required': dep_info['required'],
                'description': dep_info['description'],
                'install_command': dep_info['install_command'],
            }
            
            if is_available:
                result['available'].append(info)
            else:
                result['missing'].append(info)
        
        return result
    
    @staticmethod
    def _check_command(command: str) -> bool:
        """
        Check if a command is available in PATH.
        
        Args:
            command: Command to check
            
        Returns:
            bool: True if command is available
        """
        try:
            # Extract the base command
            base_cmd = command.split()[0]
            
            # Check if executable exists
            if shutil.which(base_cmd):
                # Try running the check command
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    timeout=10,
                    shell=False
                )
                return result.returncode == 0
            
            return False
            
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    @staticmethod
    def check_all() -> Dict[str, Any]:
        """
        Run all dependency checks.
        
        Returns:
            Dict[str, Any]: Comprehensive check results
        """
        python_checks = DependencyChecker.check_python_packages()
        system_checks = DependencyChecker.check_system_dependencies()
        
        return {
            'python': python_checks,
            'system': system_checks,
            'is_ready': len(python_checks['missing']) == 0,
            'warnings': [],
            'errors': [],
        }
    
    @staticmethod
    def generate_report(checks: Dict[str, Any]) -> str:
        """
        Generate human-readable report from check results.
        
        Args:
            checks: Results from check_all()
            
        Returns:
            str: Formatted report string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("LAPORAN PEMERIKSAAN DEPENDENSI")
        lines.append("=" * 60)
        lines.append("")
        
        # Python packages
        lines.append("Python Packages:")
        lines.append("-" * 40)
        
        python = checks['python']
        
        for pkg in python['installed']:
            lines.append(f"  ✓ {pkg}")
        
        for pkg in python['missing']:
            lines.append(f"  ✗ {pkg} (REQUIRED)")
            checks['errors'].append(f'Missing required package: {pkg}')
        
        for pkg in python['optional_installed']:
            lines.append(f"  ✓ {pkg} (opsional)")
        
        for pkg in python['optional_missing']:
            lines.append(f"  ○ {pkg} (opsional, tidak ditemukan)")
            checks['warnings'].append(f'Missing optional package: {pkg}')
        
        lines.append("")
        
        # System dependencies
        lines.append("System Dependencies:")
        lines.append("-" * 40)
        
        system = checks['system']
        
        for dep in system['available']:
            lines.append(f"  ✓ {dep['name']} - {dep['description']}")
        
        for dep in system['missing']:
            if dep['required']:
                lines.append(f"  ✗ {dep['name']} (REQUIRED) - {dep['description']}")
                lines.append(f"    Instal: {dep['install_command']}")
                checks['errors'].append(f'Missing required system dependency: {dep["name"]}')
            else:
                lines.append(f"  ○ {dep['name']} (opsional) - {dep['description']}")
                lines.append(f"    Instal: {dep['install_command']}")
                checks['warnings'].append(f'Missing optional system dependency: {dep["name"]}')
        
        lines.append("")
        lines.append("=" * 60)
        
        if checks['is_ready']:
            lines.append("STATUS: ✓ SIAP DIGUNAKAN")
        else:
            lines.append("STATUS: ✗ TIDAK SIAP")
            lines.append("")
            lines.append("Harap instal dependensi yang hilang terlebih dahulu:")
            lines.append("  pip install " + " ".join(python['missing']))
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    @staticmethod
    def get_install_commands(checks: Dict[str, Any]) -> List[str]:
        """
        Get installation commands for missing dependencies.
        
        Args:
            checks: Results from check_all()
            
        Returns:
            List[str]: List of installation commands
        """
        commands = []
        
        # Python packages
        python = checks['python']
        if python['missing']:
            commands.append(f'pip install {" ".join(python["missing"])}')
        
        # System dependencies
        system = checks['system']
        for dep in system['missing']:
            if dep['required']:
                commands.append(dep['install_command'])
        
        return commands
