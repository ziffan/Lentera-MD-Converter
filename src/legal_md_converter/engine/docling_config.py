"""
Docling Configuration for Legal-MD-Converter.

Cross-platform Docling settings including model storage,
OCR language configuration, and pipeline options.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional

import platform

from docling.document_converter import PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions


logger = logging.getLogger(__name__)


class DoclingConfig:
    """
    Configuration for Docling parser.
    
    Handles:
    - OS-specific model cache directories
    - OCR language settings
    - Pipeline performance options
    - Memory limits
    """
    
    # Default OCR languages for Indonesian legal documents
    DEFAULT_OCR_LANGUAGES = ['ind', 'eng']
    
    # Maximum file size for single-file processing (50MB)
    MAX_SINGLE_FILE_SIZE = 50 * 1024 * 1024
    
    # Chunk size for large file processing (pages per chunk)
    LARGE_FILE_CHUNK_SIZE = 10
    
    # Memory limit for Docling models (MB)
    MODEL_MEMORY_LIMIT_MB = 512
    
    @staticmethod
    def get_model_dir() -> Path:
        """
        Get OS-appropriate model cache directory.
        
        Returns:
            Path: Directory for caching Docling models
        """
        system = platform.system()
        
        if system == "Windows":
            base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
        elif system == "Darwin":  # macOS
            base = Path.home() / 'Library' / 'Application Support'
        else:  # Linux
            base = Path(os.environ.get(
                'XDG_DATA_HOME',
                Path.home() / '.local' / 'share'
            ))
        
        model_dir = base / 'legal_md_converter' / 'docling_models'
        model_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f'Model directory: {model_dir}')
        return model_dir
    
    @staticmethod
    def get_ocr_languages() -> List[str]:
        """
        Get OCR language codes for document recognition.
        
        Indonesian + English for legal documents.
        
        Returns:
            List[str]: List of Tesseract language codes
        """
        return DoclingConfig.DEFAULT_OCR_LANGUAGES.copy()
    
    @staticmethod
    def set_ocr_languages(languages: List[str]) -> None:
        """
        Set custom OCR languages.
        
        Args:
            languages: List of Tesseract language codes
        """
        DoclingConfig.DEFAULT_OCR_LANGUAGES = languages.copy()
        logger.info(f'OCR languages updated: {languages}')
    
    @staticmethod
    def get_pipeline_options() -> PdfPipelineOptions:
        """
        Get configured pipeline options for PDF processing.
        
        Returns:
            PdfPipelineOptions: Configured pipeline options
        """
        options = PdfPipelineOptions()
        
        # Enable OCR for scanned documents
        options.do_ocr = True
        options.ocr_options.lang = DoclingConfig.get_ocr_languages()
        
        # Enable table structure recognition
        options.do_table_structure = True
        
        # Performance tuning
        options.table_structure_options.do_cell_matching = True
        
        logger.debug('Pipeline options configured')
        return options
    
    @staticmethod
    def get_converter_config() -> dict:
        """
        Get converter configuration dict.

        Returns:
            dict: Configuration for DocumentConverter
        """
        return {
            'format_options': {
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=DoclingConfig.get_pipeline_options()
                ),
            },
            'raise_on_error': False,  # Handle errors gracefully
        }
    
    @staticmethod
    def is_file_too_large(file_path: Path) -> bool:
        """
        Check if a file exceeds the single-file processing limit.
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if file is too large for single processing
        """
        if not file_path.exists():
            return False
        
        return file_path.stat().st_size > DoclingConfig.MAX_SINGLE_FILE_SIZE
    
    @staticmethod
    def get_chunk_size() -> int:
        """
        Get the recommended chunk size for large file processing.
        
        Returns:
            int: Number of pages per chunk
        """
        return DoclingConfig.LARGE_FILE_CHUNK_SIZE
    
    @staticmethod
    def estimate_processing_time(page_count: int) -> str:
        """
        Estimate processing time based on page count.
        
        Rough estimates:
        - 10 pages: < 5 seconds
        - 100 pages: < 30 seconds
        - 500+ pages: 2-5 minutes
        
        Args:
            page_count: Number of pages
            
        Returns:
            str: Human-readable time estimate
        """
        if page_count <= 10:
            return "< 5 detik"
        elif page_count <= 50:
            return "5-15 detik"
        elif page_count <= 100:
            return "15-30 detik"
        elif page_count <= 500:
            return "1-3 menit"
        else:
            return "> 3 menit"
    
    @staticmethod
    def validate_tesseract_available() -> tuple[bool, str]:
        """
        Validate that Tesseract OCR is installed.
        
        Returns:
            tuple[bool, str]: (is_available, message)
        """
        import shutil
        
        tesseract_path = shutil.which('tesseract')
        
        if tesseract_path:
            return True, f'Tesseract ditemukan di: {tesseract_path}'
        else:
            return False, (
                'Tesseract OCR tidak ditemukan. '
                'Instal Tesseract untuk mendukung OCR dokumen scan.\n\n'
                'Ubuntu/Debian: sudo apt install tesseract-ocr\n'
                'Fedora: sudo dnf install tesseract\n'
                'macOS: brew install tesseract\n'
                'Windows: Unduh dari https://github.com/UB-Mannheim/tesseract/wiki'
            )
    
    @staticmethod
    def validate_ocr_languages_installed() -> tuple[bool, str]:
        """
        Validate that required OCR language packs are installed.
        
        Returns:
            tuple[bool, str]: (is_available, message)
        """
        import subprocess
        
        missing_langs = []
        
        for lang in DoclingConfig.get_ocr_languages():
            try:
                result = subprocess.run(
                    ['tesseract', '--list-langs'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if lang not in result.stdout:
                    missing_langs.append(lang)
                    
            except (FileNotFoundError, subprocess.TimeoutExpired):
                return False, 'Tesseract tidak terinstal atau tidak dapat diakses'
        
        if missing_langs:
            langs_str = ', '.join(missing_langs)
            return False, (
                f'Bahasa OCR berikut tidak ditemukan: {langs_str}\n\n'
                f'Instal dengan: sudo apt install tesseract-ocr-{"-and-".join(missing_langs)}'
            )
        
        return True, 'Semua bahasa OCR tersedia'
