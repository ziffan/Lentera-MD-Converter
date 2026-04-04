"""Document parsing engine module."""

from legal_md_converter.engine.docling_parser import (
    DocumentParser,
    DocumentContent,
    Paragraph,
    Table,
    DocumentParseError,
    CorruptDocumentError,
    EncryptedDocumentError,
)
from legal_md_converter.engine.document_parser import DocumentParser as LegacyDocumentParser
from legal_md_converter.engine.markdown_converter import MarkdownExporter
from legal_md_converter.engine.spell_checker import SpellCheckEngine
from legal_md_converter.engine.document_parser_worker import DocumentParserWorker, SingleDocumentWorker
from legal_md_converter.engine.document_service import DocumentService, DocumentInfo
from legal_md_converter.engine.docling_config import DoclingConfig
from legal_md_converter.engine.large_file_processor import LargeFileProcessor
from legal_md_converter.engine.spell_check_result import SpellCheckResult, TypoMatch
from legal_md_converter.engine.spell_check_worker import SpellCheckWorker
from legal_md_converter.engine.indonesian_text_processor import IndonesianTextProcessor

__all__ = [
    'DocumentParser',
    'DocumentContent',
    'Paragraph',
    'Table',
    'DocumentParseError',
    'CorruptDocumentError',
    'EncryptedDocumentError',
    'LegacyDocumentParser',
    'MarkdownExporter',
    'SpellCheckEngine',
    'DocumentParserWorker',
    'SingleDocumentWorker',
    'DocumentService',
    'DocumentInfo',
    'DoclingConfig',
    'LargeFileProcessor',
    'SpellCheckResult',
    'TypoMatch',
    'SpellCheckWorker',
    'IndonesianTextProcessor',
]
