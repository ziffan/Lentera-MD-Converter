"""
Document Service for Legal-MD-Converter.

Business logic layer bridging UI and Engine components.
Handles document lifecycle, parsing, conversion, and export orchestration.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from legal_md_converter.engine.docling_parser import DocumentParser, DocumentContent
from legal_md_converter.engine.markdown_converter import MarkdownExporter
from legal_md_converter.engine.spell_checker import SpellCheckEngine
from legal_md_converter.data.asset_manager import AssetManager
from legal_md_converter.utils.path_utils import get_unique_filepath, create_safe_filename


logger = logging.getLogger(__name__)


class DocumentInfo:
    """Metadata wrapper for loaded documents."""
    
    def __init__(
        self,
        file_path: str,
        content: Optional[DocumentContent] = None,
        markdown: Optional[str] = None,
        status: str = 'loaded'  # loaded, parsed, converted, error
    ) -> None:
        self.file_path = file_path
        self.filename = Path(file_path).name
        self.content = content
        self.markdown = markdown
        self.status = status
        self.loaded_at = datetime.now()
        self.error_message: Optional[str] = None
    
    @property
    def is_parsed(self) -> bool:
        return self.content is not None
    
    @property
    def is_converted(self) -> bool:
        return self.markdown is not None
    
    @property
    def word_count(self) -> int:
        if self.content:
            return self.content.word_count
        elif self.markdown:
            return len(self.markdown.split())
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'file_path': self.file_path,
            'filename': self.filename,
            'status': self.status,
            'word_count': self.word_count,
            'loaded_at': self.loaded_at.isoformat(),
            'error_message': self.error_message,
        }


class DocumentService:
    """
    Central service for document operations.
    
    Responsibilities:
    - Document lifecycle management
    - Coordinating parsing and conversion
    - Managing document cache
    - Export orchestration
    - Spell checking integration
    
    This is the primary interface the UI layer should interact with.
    """
    
    def __init__(self) -> None:
        """Initialize the document service."""
        self._parser = DocumentParser()
        self._exporter = MarkdownExporter()
        self._spell_checker: Optional[SpellCheckEngine] = None
        self._documents: Dict[str, DocumentInfo] = {}
        
        # Try to initialize spell checker
        self._init_spell_checker()
        
        logger.info('DocumentService initialized')
    
    def _init_spell_checker(self) -> None:
        """Initialize the spell checker with KBBI database."""
        try:
            asset_manager = AssetManager()
            db_path = asset_manager.get_kbbi_db_runtime_path()
            
            if db_path.exists():
                self._spell_checker = SpellCheckEngine(db_path)
                logger.info('Spell checker initialized')
            else:
                logger.warning(f'KBBI database not found at: {db_path}')
        except Exception as e:
            logger.warning(f'Failed to initialize spell checker: {e}')
    
    def load_file(self, file_path: str) -> DocumentInfo:
        """
        Load a file into the service (without parsing).
        
        Args:
            file_path: Path to the file
            
        Returns:
            DocumentInfo: Document information object
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f'File not found: {file_path}')
        
        info = DocumentInfo(file_path=str(path))
        self._documents[file_path] = info
        
        logger.info(f'File loaded: {path.name}')
        return info
    
    async def parse_file(self, file_path: str) -> DocumentInfo:
        """
        Parse a single file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            DocumentInfo: Updated document info with parsed content
        """
        if file_path not in self._documents:
            self.load_file(file_path)
        
        info = self._documents[file_path]
        
        try:
            # Initialize parser if needed
            if not self._parser.is_initialized():
                import asyncio
                await self._parser.initialize()
            
            # Parse document
            content = self._parser.parse(Path(file_path))
            
            if content:
                info.content = content
                info.status = 'parsed'
                logger.info(f'File parsed: {info.filename} ({content.word_count} words)')
            else:
                info.status = 'error'
                info.error_message = 'Parsing returned empty content'
        
        except Exception as e:
            info.status = 'error'
            info.error_message = str(e)
            logger.error(f'Failed to parse {file_path}: {e}', exc_info=True)
        
        return info
    
    def convert_to_markdown(self, file_path: str, template: Optional[str] = None) -> DocumentInfo:
        """
        Convert a parsed document to Markdown.
        
        Args:
            file_path: Path to the original file
            template: Optional template name ('legal', 'academic', 'basic')
            
        Returns:
            DocumentInfo: Updated document info with markdown content
        """
        if file_path not in self._documents:
            raise ValueError(f'Document not loaded: {file_path}')
        
        info = self._documents[file_path]
        
        if not info.content:
            raise ValueError(f'Document not parsed: {file_path}')
        
        try:
            if template:
                # Apply template formatting via our exporter
                markdown = self._exporter.to_markdown(info.content, template)
            else:
                # Use Docling's native markdown output — it preserves numbering,
                # tables, and structure better than our secondary re-conversion.
                markdown = info.content.raw_text or self._exporter.to_markdown(info.content)
            info.markdown = markdown
            info.status = 'converted'

            logger.info(f'Converted to markdown: {info.filename} ({len(markdown)} chars)')
        
        except Exception as e:
            info.status = 'error'
            info.error_message = f'Conversion error: {str(e)}'
            logger.error(f'Failed to convert {file_path}: {e}', exc_info=True)
        
        return info
    
    def export_file(
        self,
        file_path: str,
        output_path: str,
        template: Optional[str] = None
    ) -> bool:
        """
        Export a document to a Markdown file.
        
        Args:
            file_path: Original file path
            output_path: Output file path
            template: Optional template name
            
        Returns:
            bool: True if export was successful
        """
        if file_path not in self._documents:
            raise ValueError(f'Document not loaded: {file_path}')
        
        info = self._documents[file_path]
        
        if not info.content:
            raise ValueError(f'Document not parsed: {file_path}')
        
        try:
            output = Path(output_path)
            success = self._exporter.save_file(info.content, output, template)
            
            if success:
                logger.info(f'Exported: {output_path}')
            
            return success
        
        except Exception as e:
            logger.error(f'Failed to export {file_path}: {e}', exc_info=True)
            return False
    
    def check_spelling(self, file_path: str) -> Optional[List]:
        """
        Check spelling in a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Optional[List]: List of (word, is_correct, suggestions) or None
        """
        if not self._spell_checker:
            logger.warning('Spell checker not available')
            return None
        
        if file_path not in self._documents:
            return None
        
        info = self._documents[file_path]
        
        text_to_check = info.markdown or (info.content.raw_text if info.content else '')
        
        if not text_to_check:
            return None
        
        try:
            results = self._spell_checker.check_text(text_to_check)
            logger.info(f'Spell check complete for {info.filename}')
            return results
        except Exception as e:
            logger.error(f'Spell check error: {e}', exc_info=True)
            return None
    
    def get_error_positions(self, file_path: str) -> List[tuple]:
        """
        Get character positions of spelling errors.
        
        Args:
            file_path: Path to the document
            
        Returns:
            List[tuple]: List of (start, end) positions
        """
        if not self._spell_checker or file_path not in self._documents:
            return []
        
        info = self._documents[file_path]
        text = info.markdown or (info.content.raw_text if info.content else '')
        
        return self._spell_checker.get_error_positions(text)
    
    def get_document(self, file_path: str) -> Optional[DocumentInfo]:
        """
        Get document info for a loaded file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Optional[DocumentInfo]: Document info or None
        """
        return self._documents.get(file_path)
    
    def get_all_documents(self) -> Dict[str, DocumentInfo]:
        """
        Get all loaded documents.
        
        Returns:
            Dict[str, DocumentInfo]: Dictionary of file paths to document info
        """
        return self._documents.copy()
    
    def remove_document(self, file_path: str) -> None:
        """
        Remove a document from the service.
        
        Args:
            file_path: Path to the document to remove
        """
        if file_path in self._documents:
            del self._documents[file_path]
            logger.info(f'Removed document: {Path(file_path).name}')
    
    def clear_all(self) -> None:
        """Clear all loaded documents."""
        self._documents.clear()
        logger.info('Cleared all documents')
    
    def get_document_count(self) -> int:
        """Get number of loaded documents."""
        return len(self._documents)
    
    def get_parsed_count(self) -> int:
        """Get number of parsed documents."""
        return sum(1 for doc in self._documents.values() if doc.is_parsed)
    
    def get_total_word_count(self) -> int:
        """Get total word count across all documents."""
        return sum(doc.word_count for doc in self._documents.values())
    
    def is_spell_checker_ready(self) -> bool:
        """Check if spell checker is available."""
        return self._spell_checker is not None and self._spell_checker.is_ready()
    
    def close(self) -> None:
        """Clean up resources."""
        if self._spell_checker:
            self._spell_checker.close()
        logger.info('DocumentService closed')
