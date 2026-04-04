"""
Document Parser Worker for Legal-MD-Converter.

QThread wrapper for non-blocking document parsing using Docling.
"""

import logging
from pathlib import Path
from typing import Optional, List

from PySide6.QtCore import QThread, Signal

from legal_md_converter.engine.docling_parser import DocumentParser, DocumentContent


logger = logging.getLogger(__name__)


class DocumentParserWorker(QThread):
    """
    QThread worker for non-blocking document parsing.
    
    Features:
    - Background parsing without blocking UI
    - Progress updates per page/document
    - Memory-efficient processing
    - Cancel support
    - Error handling with signal propagation
    
    Usage:
        worker = DocumentParserWorker(file_paths)
        worker.progress.connect(on_progress)
        worker.document_parsed.connect(on_document_parsed)
        worker.parsing_complete.connect(on_complete)
        worker.error_occurred.connect(on_error)
        worker.start()
    """
    
    # Signals
    progress = Signal(int, int)  # current, total
    document_parsed = Signal(str, object)  # file_path, DocumentContent
    parsing_complete = Signal(object)  # dict[file_path, DocumentContent]
    error_occurred = Signal(str)  # error message
    page_progress = Signal(int, int, str)  # current_page, total_pages, file_name
    
    def __init__(
        self,
        file_paths: List[str],
        parent: Optional[QThread] = None
    ) -> None:
        super().__init__(parent)
        
        self._file_paths = file_paths
        self._parser = DocumentParser()
        self._cancelled = False
        self._results = {}
    
    def run(self) -> None:
        """Execute parsing in background thread."""
        try:
            total = len(self._file_paths)
            self._results = {}
            
            logger.info(f'Starting document parsing: {total} files')
            self.progress.emit(0, total)
            
            # Initialize parser (async init done synchronously in worker thread)
            import asyncio
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(self._parser.initialize())
            finally:
                loop.close()
            
            for i, file_path in enumerate(self._file_paths):
                if self._cancelled:
                    logger.info('Parsing cancelled by user')
                    break
                
                path = Path(file_path)
                self.progress.emit(i + 1, total)
                
                logger.info(f'Parsing file {i + 1}/{total}: {path.name}')
                
                # Parse document
                content = self._parser.parse(path)
                
                if content:
                    self._results[file_path] = content
                    self.document_parsed.emit(file_path, content)
                    
                    # Estimate page count for PDFs
                    page_count = content.metadata.get('pages', 1)
                    self.page_progress.emit(
                        page_count,
                        page_count,
                        path.name
                    )
                else:
                    logger.warning(f'Failed to parse: {file_path}')
                    self._results[file_path] = None
            
            if not self._cancelled:
                self.parsing_complete.emit(self._results)
                logger.info(f'Parsing complete: {len(self._results)} documents')
        
        except Exception as e:
            logger.error(f'Parser worker error: {e}', exc_info=True)
            self.error_occurred.emit(str(e))
    
    def cancel(self) -> None:
        """Request parsing cancellation."""
        self._cancelled = True
        logger.info('Cancel requested for DocumentParserWorker')
    
    def is_cancelled(self) -> bool:
        """Check if worker was cancelled."""
        return self._cancelled
    
    def get_results(self) -> dict:
        """
        Get parsing results.
        
        Returns:
            dict: Mapping of file paths to DocumentContent objects
        """
        return self._results.copy()
    
    def get_parsed_count(self) -> int:
        """Get number of successfully parsed documents."""
        return sum(1 for v in self._results.values() if v is not None)
    
    def get_failed_count(self) -> int:
        """Get number of failed documents."""
        return sum(1 for v in self._results.values() if v is None)


class SingleDocumentWorker(QThread):
    """
    QThread worker for parsing a single document.
    
    Usage:
        worker = SingleDocumentWorker(file_path)
        worker.document_ready.connect(on_ready)
        worker.error_occurred.connect(on_error)
        worker.start()
    """
    
    # Signals
    document_ready = Signal(object)  # DocumentContent
    progress_update = Signal(int, int, str)  # current, total, message
    error_occurred = Signal(str)
    
    def __init__(
        self,
        file_path: str,
        parent: Optional[QThread] = None
    ) -> None:
        super().__init__(parent)
        
        self._file_path = file_path
        self._parser = DocumentParser()
        self._cancelled = False
    
    def run(self) -> None:
        """Execute single document parsing."""
        try:
            path = Path(self._file_path)
            self.progress_update.emit(0, 100, f'Membaca {path.name}...')
            
            # Initialize parser
            import asyncio
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(self._parser.initialize())
            finally:
                loop.close()
            
            self.progress_update.emit(25, 100, 'Mempersiapkan parser...')
            
            # Parse
            content = self._parser.parse(path)
            
            if content:
                self.progress_update.emit(100, 100, 'Selesai!')
                self.document_ready.emit(content)
                logger.info(f'Single document parsed: {path.name}')
            else:
                self.error_occurred.emit(f'Gagal memparse dokumen: {path.name}')
        
        except Exception as e:
            logger.error(f'Single document worker error: {e}', exc_info=True)
            self.error_occurred.emit(str(e))
    
    def cancel(self) -> None:
        """Request cancellation."""
        self._cancelled = True
