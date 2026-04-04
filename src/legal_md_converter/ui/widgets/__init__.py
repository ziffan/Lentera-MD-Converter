"""UI widgets module."""

from legal_md_converter.ui.widgets.file_drop_widget import FileDropWidget
from legal_md_converter.ui.widgets.document_preview import DocumentPreview
from legal_md_converter.ui.widgets.preview_widget import PreviewWidget
from legal_md_converter.ui.widgets.progress_dialog import ProgressDialog
from legal_md_converter.ui.widgets.spellcheck_panel import SpellCheckPanel, TypoMatch
from legal_md_converter.ui.widgets.export_dialog import ExportDialog
from legal_md_converter.ui.widgets.markdown_preview import MarkdownPreview

__all__ = [
    'FileDropWidget',
    'DocumentPreview',
    'PreviewWidget',
    'ProgressDialog',
    'SpellCheckPanel',
    'TypoMatch',
    'ExportDialog',
    'MarkdownPreview',
]
