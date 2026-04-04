"""
Document parser engine for Legal-MD-Converter.

Handles parsing of various legal document formats (PDF, DOCX, RTF, TXT)
and conversion to Markdown format using Docling.
"""

import logging
from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions


logger = logging.getLogger(__name__)


class DocumentParser:
    """Parser for converting legal documents to Markdown."""

    # Docling-supported formats
    SUPPORTED_FORMATS = {
        '.pdf', '.docx', '.doc', '.pptx', '.xlsx', 
        '.html', '.htm', '.md', '.txt', '.rtf',
    }

    def __init__(self) -> None:
        """Initialize the document parser with Docling converter."""
        self._setup_converter()

    def _setup_converter(self) -> None:
        """Set up the Docling converter with appropriate options."""
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
            }
        )
        
        logger.info('Document converter initialized')
    
    def parse_file(self, file_path: str) -> Optional[str]:
        """
        Parse a single file and return Markdown content.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Optional[str]: Markdown content or None if parsing fails
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f'File not found: {file_path}')
            return None
        
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            logger.error(f'Unsupported file format: {path.suffix}')
            return None
        
        try:
            logger.info(f'Parsing file: {file_path}')
            result = self.converter.convert(file_path)
            markdown = result.document.export_to_markdown()
            
            logger.info(f'Successfully parsed: {file_path}')
            return markdown
            
        except Exception as e:
            logger.error(f'Error parsing {file_path}: {e}', exc_info=True)
            return None
    
    def parse_files(self, file_paths: list[str]) -> dict[str, Optional[str]]:
        """
        Parse multiple files and return a dictionary of results.
        
        Args:
            file_paths: List of file paths to parse
            
        Returns:
            dict[str, Optional[str]]: Dictionary mapping file paths to markdown content
        """
        results = {}
        
        for file_path in file_paths:
            markdown = self.parse_file(file_path)
            results[file_path] = markdown
        
        logger.info(f'Parsed {len(results)} files')
        return results
    
    def get_supported_formats(self) -> list[str]:
        """
        Get list of supported file formats.
        
        Returns:
            list[str]: List of supported file extensions
        """
        return list(self.SUPPORTED_FORMATS.keys())
    
    def is_supported(self, file_path: str) -> bool:
        """
        Check if a file format is supported.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if the file format is supported
        """
        return Path(file_path).suffix.lower() in self.SUPPORTED_FORMATS
