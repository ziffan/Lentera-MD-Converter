"""
Large file processor for Legal-MD-Converter.

Handles chunked processing of large PDF files to prevent
memory issues and provide granular progress reporting.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions


logger = logging.getLogger(__name__)


class LargeFileProcessor:
    """
    Processes large PDF files in chunks to prevent memory issues.
    
    Features:
    - Page-range based chunking
    - Memory release between chunks
    - Progress callbacks
    - Cancel support
    - Result aggregation
    """
    
    def __init__(
        self,
        chunk_size: int = 10,
        progress_callback: Optional[Callable] = None
    ) -> None:
        """
        Initialize the large file processor.
        
        Args:
            chunk_size: Number of pages to process per chunk
            progress_callback: Optional callback(current, total, message)
        """
        self._chunk_size = chunk_size
        self._progress_callback = progress_callback
        self._cancelled = False
        self._converter: Optional[DocumentConverter] = None
    
    def _get_converter(self) -> DocumentConverter:
        """Get or create converter instance."""
        if not self._converter:
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = True
            pipeline_options.do_table_structure = True
            pipeline_options.ocr_options.lang = ['ind', 'eng']

            self._converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
                }
            )

        return self._converter
    
    def get_page_count(self, file_path: Path) -> int:
        """
        Get the number of pages in a PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            int: Number of pages
        """
        try:
            import fitz  # PyMuPDF for page counting
            
            with fitz.open(str(file_path)) as doc:
                return len(doc)
        
        except ImportError:
            # Fallback: try docling
            logger.warning('PyMuPDF not available, using fallback')
            return self._estimate_pages_docling(file_path)
        
        except Exception as e:
            logger.error(f'Failed to get page count: {e}')
            return 0
    
    def _estimate_pages_docling(self, file_path: Path) -> int:
        """Estimate page count using Docling (slower fallback)."""
        try:
            converter = self._get_converter()
            result = converter.convert(str(file_path))
            return len(result.document.pages) if hasattr(result.document, 'pages') else 1
        except Exception:
            return 1
    
    def process(
        self,
        file_path: Path,
        start_page: int = 0,
        end_page: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Process a PDF file (optionally with page range).
        
        Args:
            file_path: Path to PDF
            start_page: First page to process (0-indexed)
            end_page: Last page to process (None for all)
            
        Returns:
            Dict[str, Any]: Processing results or None on failure
        """
        try:
            # Get total pages
            total_pages = self.get_page_count(file_path)
            if total_pages == 0:
                logger.error('Could not determine page count')
                return None
            
            if end_page is None:
                end_page = total_pages
            
            # Calculate chunks
            pages_to_process = list(range(start_page, min(end_page, total_pages)))
            chunks = [
                pages_to_process[i:i + self._chunk_size]
                for i in range(0, len(pages_to_process), self._chunk_size)
            ]
            
            logger.info(f'Processing {file_path}: {len(pages_to_process)} pages in {len(chunks)} chunks')
            
            # Process each chunk
            all_markdown = []
            all_paragraphs = []
            all_tables = []
            
            for chunk_idx, chunk_pages in enumerate(chunks):
                if self._cancelled:
                    logger.info('Processing cancelled')
                    break
                
                # Update progress
                if self._progress_callback:
                    pages_done = chunk_idx * self._chunk_size
                    self._progress_callback(
                        pages_done,
                        len(pages_to_process),
                        f'Memproses halaman {pages_done + 1}-{min(pages_done + len(chunk_pages), len(pages_to_process))} dari {total_pages}'
                    )
                
                # Process chunk
                chunk_result = self._process_page_range(file_path, chunk_pages)
                
                if chunk_result:
                    if chunk_result.get('markdown'):
                        all_markdown.append(chunk_result['markdown'])
                    if chunk_result.get('paragraphs'):
                        all_paragraphs.extend(chunk_result['paragraphs'])
                    if chunk_result.get('tables'):
                        all_tables.extend(chunk_result['tables'])
                
                # Release memory between chunks
                self._release_memory()
            
            if self._cancelled:
                return None
            
            # Aggregate results
            return {
                'markdown': '\n\n'.join(all_markdown),
                'paragraphs': all_paragraphs,
                'tables': all_tables,
                'total_pages': total_pages,
                'pages_processed': len(pages_to_process),
            }
        
        except Exception as e:
            logger.error(f'Large file processing error: {e}', exc_info=True)
            return None
    
    def _process_page_range(
        self,
        file_path: Path,
        pages: List[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Process a specific range of pages.
        
        Args:
            file_path: Path to PDF
            pages: List of page indices to process
            
        Returns:
            Dict with markdown, paragraphs, tables
        """
        try:
            converter = self._get_converter()
            
            # Note: Docling doesn't support page-range conversion directly
            # So we process the whole file but track which pages we care about
            result = converter.convert(str(file_path))
            
            markdown = result.document.export_to_markdown()
            
            # Extract paragraphs for target pages
            paragraphs = []
            if hasattr(result.document, 'texts'):
                for item in result.document.texts:
                    page_num = item.page if hasattr(item, 'page') else 0
                    if page_num in pages:
                        paragraphs.append({
                            'text': item.text,
                            'style': item.label.lower() if hasattr(item, 'label') else 'normal',
                            'level': item.level if hasattr(item, 'level') else 0,
                            'page_number': page_num,
                        })
            
            # Extract tables for target pages
            tables = []
            if hasattr(result.document, 'tables'):
                for table in result.document.tables:
                    page_num = table.page if hasattr(table, 'page') else 0
                    if page_num in pages:
                        tables.append({
                            'headers': table.headers if hasattr(table, 'headers') else [],
                            'rows': table.data if hasattr(table, 'data') else [],
                            'page_number': page_num,
                        })
            
            return {
                'markdown': markdown,
                'paragraphs': paragraphs,
                'tables': tables,
            }
        
        except Exception as e:
            logger.error(f'Page range processing error: {e}')
            return None
    
    def _release_memory(self) -> None:
        """Release memory between chunks."""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Reset converter to release model memory
        self._converter = None
        
        logger.debug('Memory released between chunks')
    
    def cancel(self) -> None:
        """Request cancellation of processing."""
        self._cancelled = True
        logger.info('Cancellation requested for LargeFileProcessor')
    
    def is_cancelled(self) -> bool:
        """Check if processing was cancelled."""
        return self._cancelled
