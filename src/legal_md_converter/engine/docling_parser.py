"""
Docling Parser - Document parsing engine for Legal-MD-Converter.

Handles PDF/TXT/DOCX parsing using IBM Docling engine with non-blocking processing.
Includes error handling for corrupt/encrypted files and memory management.
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

from legal_md_converter.data.asset_manager import AssetManager
from legal_md_converter.engine.docling_config import DoclingConfig
from legal_md_converter.engine.large_file_processor import LargeFileProcessor


logger = logging.getLogger(__name__)


class DocumentParseError(Exception):
    """Base exception for document parsing errors."""
    pass


class CorruptDocumentError(DocumentParseError):
    """Exception for corrupt or unreadable documents."""
    pass


class EncryptedDocumentError(DocumentParseError):
    """Exception for password-protected documents."""
    pass


class LargeDocumentWarning(UserWarning):
    """Warning for large files that may take longer to process."""
    pass



@dataclass
class Paragraph:
    """Single paragraph with styling info."""
    text: str
    style: str  # 'heading', 'normal', 'list_item', etc.
    level: int = 0  # For headings (H1=1, H2=2, etc.)
    page_number: int = 0


@dataclass
class Table:
    """Table extracted from document."""
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    page_number: int = 0
    caption: str = ""


@dataclass
class DocumentContent:
    """Structured representation of parsed document."""
    source_path: Path
    title: str
    paragraphs: List[Paragraph]
    tables: List[Table]
    metadata: Dict[str, Any]
    raw_text: str
    word_count: int
    
    def __post_init__(self):
        """Calculate word count if not provided."""
        if self.word_count == 0 and self.raw_text:
            self.word_count = len(self.raw_text.split())


class DocumentParser:
    """
    Handles PDF and TXT parsing using Docling.
    
    Features:
    - Async initialization to not block UI
    - Model caching for performance
    - Cross-platform model storage
    - Support for PDF and TXT formats
    """
    
    SUPPORTED_FORMATS = ['.pdf', '.txt']
    
    def __init__(self) -> None:
        """Initialize the document parser."""
        self._converter: Optional[DocumentConverter] = None
        self._initialized = False
        self._config = DoclingConfig()
        
        logger.info('DocumentParser created')
    
    async def initialize(self) -> None:
        """
        Initialize Docling models (async to not block UI).
        
        Loads document understanding models and caches them
        in OS-specific storage paths.
        """
        if self._initialized:
            return
        
        try:
            logger.info('Initializing Docling models...')

            # Configure pipeline
            pipeline_options = self._config.get_pipeline_options()

            # Create converter with options
            self._converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
                }
            )

            self._initialized = True
            logger.info('Docling models initialized successfully')
            
        except Exception as e:
            logger.error(f'Failed to initialize Docling: {e}', exc_info=True)
            raise
    
    def parse(self, file_path: Path) -> Optional[DocumentContent]:
        """
        Parse document and return structured content.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Optional[DocumentContent]: Parsed content or None if failed
        """
        if not self._initialized:
            logger.warning('Parser not initialized. Initializing synchronously...')
            # Run async initialization synchronously
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(self.initialize())
            finally:
                loop.close()
        
        suffix = file_path.suffix.lower()

        if suffix == '.pdf':
            return self.parse_pdf(file_path)
        elif suffix in ['.txt', '.rtf', '.text', '.log']:
            return self.parse_txt(file_path)
        elif suffix in ['.docx', '.doc', '.pptx', '.xlsx', '.html', '.htm', '.md']:
            return self.parse_generic(file_path)
        else:
            logger.error(f'Unsupported format: {suffix}')
            return None
    
    def parse_pdf(self, file_path: Path) -> Optional[DocumentContent]:
        """
        Extract text and structure from PDF.
        
        Handles:
        - Normal PDF files
        - Large files (>50MB) with chunked processing
        - Encrypted files
        - Corrupt files
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Optional[DocumentContent]: Parsed PDF content
            
        Raises:
            CorruptDocumentError: If file is corrupt
            EncryptedDocumentError: If file is password-protected
        """
        if not self._converter:
            logger.error('Converter not initialized')
            return None
        
        # Validate file exists and is readable
        if not file_path.exists():
            logger.error(f'File not found: {file_path}')
            raise CorruptDocumentError(f'File tidak ditemukan: {file_path.name}')
        
        if file_path.stat().st_size == 0:
            logger.error(f'Empty file: {file_path}')
            raise CorruptDocumentError(f'File kosong: {file_path.name}')
        
        # Check if file is too large
        is_large_file = DoclingConfig.is_file_too_large(file_path)
        
        if is_large_file:
            logger.info(f'Large file detected ({file_path.stat().st_size / 1024 / 1024:.1f} MB), using chunked processing')
            return self._parse_large_pdf(file_path)
        
        try:
            logger.info(f'Parsing PDF: {file_path}')
            
            # Convert document
            result = self._converter.convert(str(file_path))
            
            # Extract markdown
            markdown = result.document.export_to_markdown()
            
            # Extract structured content
            paragraphs = self._extract_paragraphs(result.document)
            tables = self._extract_tables(result.document)
            
            # Get metadata
            metadata = {
                'source': str(file_path),
                'filename': file_path.name,
                'format': 'PDF',
                'pages': len(result.document.pages) if hasattr(result.document, 'pages') else 0,
                'file_size': file_path.stat().st_size,
            }
            
            content = DocumentContent(
                source_path=file_path,
                title=file_path.stem,
                paragraphs=paragraphs,
                tables=tables,
                metadata=metadata,
                raw_text=markdown,
                word_count=len(markdown.split()),
            )
            
            logger.info(f'Successfully parsed PDF: {file_path} ({content.word_count} words)')
            return content
            
        except EncryptedDocumentError:
            logger.error(f'Encrypted PDF: {file_path}')
            raise
        
        except CorruptDocumentError:
            logger.error(f'Corrupt PDF: {file_path}')
            raise
        
        except Exception as e:
            error_str = str(e).lower()
            
            # Detect specific error types
            if 'encrypted' in error_str or 'password' in error_str:
                raise EncryptedDocumentError(f'File terproteksi kata sandi: {file_path.name}')
            
            if 'corrupt' in error_str or 'invalid' in error_str or 'damaged' in error_str:
                raise CorruptDocumentError(f'File rusak atau tidak valid: {file_path.name}')
            
            logger.error(f'Error parsing PDF {file_path}: {e}', exc_info=True)
            return None
    
    def _parse_large_pdf(self, file_path: Path) -> Optional[DocumentContent]:
        """
        Parse large PDF file using chunked processing.
        
        Args:
            file_path: Path to large PDF file
            
        Returns:
            Optional[DocumentContent]: Parsed content or None
        """
        try:
            processor = LargeFileProcessor(
                chunk_size=DoclingConfig.get_chunk_size(),
                progress_callback=lambda current, total, msg: logger.info(f'Large file: {msg}')
            )
            
            result = processor.process(file_path)
            
            if not result:
                logger.error('Large file processing returned None')
                return None
            
            # Convert result to DocumentContent
            paragraphs = []
            for para_data in result.get('paragraphs', []):
                paragraphs.append(Paragraph(
                    text=para_data.get('text', ''),
                    style=para_data.get('style', 'normal'),
                    level=para_data.get('level', 0),
                    page_number=para_data.get('page_number', 0),
                ))
            
            tables = []
            for table_data in result.get('tables', []):
                tables.append(Table(
                    headers=table_data.get('headers', []),
                    rows=table_data.get('rows', []),
                    page_number=table_data.get('page_number', 0),
                ))
            
            metadata = {
                'source': str(file_path),
                'filename': file_path.name,
                'format': 'PDF',
                'pages': result.get('total_pages', 0),
                'file_size': file_path.stat().st_size,
                'large_file': True,
                'chunked_processing': True,
            }
            
            content = DocumentContent(
                source_path=file_path,
                title=file_path.stem,
                paragraphs=paragraphs,
                tables=tables,
                metadata=metadata,
                raw_text=result.get('markdown', ''),
                word_count=len(result.get('markdown', '').split()),
            )
            
            logger.info(f'Successfully parsed large PDF: {file_path} ({content.word_count} words)')
            return content
        
        except Exception as e:
            logger.error(f'Error parsing large PDF {file_path}: {e}', exc_info=True)
            return None
    
    def parse_txt(self, file_path: Path) -> Optional[DocumentContent]:
        """
        Parse plain text with basic structure detection.
        
        Detects headings, paragraphs, and list items from raw text.
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Optional[DocumentContent]: Parsed text content
        """
        try:
            logger.info(f'Parsing TXT: {file_path}')
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            
            # Parse structure
            paragraphs = self._parse_text_structure(raw_text)
            
            # Metadata
            metadata = {
                'source': str(file_path),
                'filename': file_path.name,
                'format': 'TXT',
            }
            
            content = DocumentContent(
                source_path=file_path,
                title=file_path.stem,
                paragraphs=paragraphs,
                tables=[],
                metadata=metadata,
                raw_text=raw_text,
                word_count=len(raw_text.split()),
            )
            
            logger.info(f'Successfully parsed TXT: {file_path} ({content.word_count} words)')
            return content
            
        except Exception as e:
            logger.error(f'Error parsing TXT {file_path}: {e}', exc_info=True)
            return None

    def parse_generic(self, file_path: Path) -> Optional[DocumentContent]:
        """
        Parse DOCX, PPTX, XLSX, HTML, MD files using docling.

        Args:
            file_path: Path to the document file

        Returns:
            Optional[DocumentContent]: Parsed content or None
        """
        if not self._converter:
            logger.error('Converter not initialized')
            return None

        if not file_path.exists():
            logger.error(f'File not found: {file_path}')
            raise CorruptDocumentError(f'File tidak ditemukan: {file_path.name}')

        try:
            logger.info(f'Parsing document: {file_path}')
            result = self._converter.convert(str(file_path))
            markdown = result.document.export_to_markdown()

            metadata = {
                'source': str(file_path),
                'filename': file_path.name,
                'format': file_path.suffix.upper().lstrip('.'),
            }

            content = DocumentContent(
                source_path=file_path,
                title=file_path.stem,
                paragraphs=[],
                tables=[],
                metadata=metadata,
                raw_text=markdown,
                word_count=len(markdown.split()),
            )

            logger.info(f'Successfully parsed: {file_path} ({content.word_count} words)')
            return content

        except Exception as e:
            logger.error(f'Error parsing {file_path}: {e}', exc_info=True)
            return None

    def _extract_paragraphs(self, document) -> List[Paragraph]:
        """
        Extract paragraphs from Docling document.
        
        Args:
            document: Docling document object
            
        Returns:
            List[Paragraph]: Extracted paragraphs
        """
        paragraphs = []
        
        try:
            # Access document structure
            if hasattr(document, 'texts'):
                for item in document.texts:
                    para = Paragraph(
                        text=item.text,
                        style=item.label.lower() if hasattr(item, 'label') else 'normal',
                        level=item.level if hasattr(item, 'level') else 0,
                        page_number=item.page if hasattr(item, 'page') else 0,
                    )
                    paragraphs.append(para)
            elif hasattr(document, 'body'):
                # Fallback: extract from body
                paragraphs.append(Paragraph(
                    text=document.body,
                    style='normal',
                ))
        except Exception as e:
            logger.warning(f'Error extracting paragraphs: {e}')
        
        return paragraphs
    
    def _extract_tables(self, document) -> List[Table]:
        """
        Extract tables from Docling document.
        
        Args:
            document: Docling document object
            
        Returns:
            List[Table]: Extracted tables
        """
        tables = []
        
        try:
            if hasattr(document, 'tables'):
                for table in document.tables:
                    headers = []
                    rows = []
                    
                    if hasattr(table, 'headers'):
                        headers = table.headers
                    
                    if hasattr(table, 'data'):
                        rows = table.data
                    
                    tables.append(Table(
                        headers=headers,
                        rows=rows,
                        page_number=table.page if hasattr(table, 'page') else 0,
                    ))
        except Exception as e:
            logger.warning(f'Error extracting tables: {e}')
        
        return tables
    
    def _parse_text_structure(self, text: str) -> List[Paragraph]:
        """
        Parse structure from plain text.
        
        Detects headings (lines ending with :\n or ALL CAPS),
        list items (lines starting with - or *), and paragraphs.
        
        Args:
            text: Raw text content
            
        Returns:
            List[Paragraph]: Structured paragraphs
        """
        paragraphs = []
        lines = text.split('\n')
        current_para = []
        page_number = 1
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Empty line - finalize current paragraph
                if current_para:
                    paragraphs.append(Paragraph(
                        text='\n'.join(current_para),
                        style='normal',
                        page_number=page_number,
                    ))
                    current_para = []
                continue
            
            # Detect heading patterns
            if line.endswith(':') or (line.isupper() and len(line) > 3):
                # Finalize previous paragraph
                if current_para:
                    paragraphs.append(Paragraph(
                        text='\n'.join(current_para),
                        style='normal',
                        page_number=page_number,
                    ))
                    current_para = []
                
                # Add as heading
                paragraphs.append(Paragraph(
                    text=line,
                    style='heading',
                    level=1,
                    page_number=page_number,
                ))
                continue
            
            # Detect list items
            if line.startswith(('- ', '* ', '• ')):
                # Finalize previous paragraph
                if current_para:
                    paragraphs.append(Paragraph(
                        text='\n'.join(current_para),
                        style='normal',
                        page_number=page_number,
                    ))
                    current_para = []
                
                # Add as list item
                paragraphs.append(Paragraph(
                    text=line[2:],  # Remove bullet
                    style='list_item',
                    page_number=page_number,
                ))
                continue
            
            # Regular paragraph line
            current_para.append(line)
        
        # Finalize last paragraph
        if current_para:
            paragraphs.append(Paragraph(
                text='\n'.join(current_para),
                style='normal',
                page_number=page_number,
            ))
        
        return paragraphs
    
    def is_initialized(self) -> bool:
        """
        Check if parser is initialized.
        
        Returns:
            bool: True if ready to parse
        """
        return self._initialized
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List[str]: Supported file extensions
        """
        return self.SUPPORTED_FORMATS.copy()
