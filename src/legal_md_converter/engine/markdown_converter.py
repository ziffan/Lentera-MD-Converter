"""
Markdown Converter for Legal-MD-Converter.

Converts parsed document content to properly formatted Markdown
with legal document templates and styling.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from string import Template

from legal_md_converter.engine.docling_parser import DocumentContent, Paragraph, Table
from legal_md_converter.data.asset_manager import AssetManager


logger = logging.getLogger(__name__)


class TemplateLoader:
    """Loads and processes markdown templates."""
    
    def __init__(self) -> None:
        """Initialize template loader."""
        self._templates: Dict[str, str] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all available templates from assets directory."""
        template_dir = AssetManager().get_asset_dir() / 'templates'
        
        if not template_dir.exists():
            logger.warning(f'Template directory not found: {template_dir}')
            return
        
        for template_file in template_dir.glob('*.md'):
            try:
                content = template_file.read_text(encoding='utf-8')
                template_name = template_file.stem
                self._templates[template_name] = content
                logger.info(f'Loaded template: {template_name}')
            except Exception as e:
                logger.error(f'Failed to load template {template_file}: {e}')
    
    def get_template(self, name: str) -> Optional[str]:
        """
        Get a template by name.
        
        Args:
            name: Template name (e.g., 'legal', 'academic', 'basic')
            
        Returns:
            Optional[str]: Template content or None
        """
        return self._templates.get(name)
    
    def get_available_templates(self) -> List[str]:
        """
        Get list of available template names.
        
        Returns:
            List[str]: Available template names
        """
        return list(self._templates.keys())
    
    def render_template(self, name: str, **kwargs) -> Optional[str]:
        """
        Render a template with variables.
        
        Args:
            name: Template name
            **kwargs: Template variables
            
        Returns:
            Optional[str]: Rendered template or None
        """
        template = self.get_template(name)
        if not template:
            return None
        
        try:
            # Use simple string replacement with {{ variable }} syntax
            result = template
            for key, value in kwargs.items():
                result = result.replace('{{ ' + key + ' }}', str(value))
                result = result.replace('{{' + key + '}}', str(value))
            return result
        except Exception as e:
            logger.error(f'Template rendering error: {e}')
            return None


class MarkdownExporter:
    """
    Exports parsed documents to Markdown format.
    
    Features:
    - Standard Markdown output
    - Legal document templates
    - Table formatting
    - Metadata headers
    - Template loading from assets
    """
    
    def __init__(self) -> None:
        """Initialize the markdown exporter."""
        self._template_loader = TemplateLoader()
    
    def to_markdown(self, content: DocumentContent, template: Optional[str] = None) -> str:
        """
        Convert document content to Markdown.
        
        Args:
            content: Parsed document content
            template: Optional template name ('legal', 'basic', 'academic')
            
        Returns:
            str: Formatted Markdown string
        """
        if template and self._template_loader.get_template(template):
            return self._apply_template(content, template)
        
        return self._generate_basic_markdown(content)
    
    def _generate_basic_markdown(self, content: DocumentContent) -> str:
        """
        Generate basic Markdown from document content.
        
        Args:
            content: Parsed document content
            
        Returns:
            str: Markdown string
        """
        parts = []
        
        # Title
        parts.append(f"# {content.title}\n")
        
        # Metadata
        parts.append(self._generate_metadata(content))
        
        # Paragraphs
        for para in content.paragraphs:
            parts.append(self._format_paragraph(para))
        
        # Tables
        if content.tables:
            parts.append("\n## Tables\n")
            for i, table in enumerate(content.tables, 1):
                parts.append(self._format_table(table, i))
        
        markdown = '\n'.join(parts)
        
        logger.info(f'Generated markdown: {len(markdown)} characters')
        return markdown
    
    def _generate_metadata(self, content: DocumentContent) -> str:
        """
        Generate metadata section.
        
        Args:
            content: Document content
            
        Returns:
            str: Markdown metadata block
        """
        metadata = content.metadata
        
        if not metadata:
            return ""
        
        parts = ["---"]
        
        if 'filename' in metadata:
            parts.append(f"source: {metadata['filename']}")
        
        if 'format' in metadata:
            parts.append(f"format: {metadata['format']}")
        
        if 'pages' in metadata and metadata['pages']:
            parts.append(f"pages: {metadata['pages']}")
        
        parts.append(f"converted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        parts.append("---\n")
        
        return '\n'.join(parts)
    
    def _format_paragraph(self, para: Paragraph) -> str:
        """
        Format a paragraph as Markdown.
        
        Args:
            para: Paragraph object
            
        Returns:
            str: Markdown paragraph
        """
        if para.style == 'heading':
            # Markdown heading (# Heading)
            prefix = '#' * min(para.level, 6)  # Max 6 levels
            return f"\n{prefix} {para.text}\n"
        
        elif para.style == 'list_item':
            # List item
            return f"- {para.text}"
        
        else:
            # Normal paragraph
            return f"{para.text}\n"
    
    def _format_table(self, table: Table, index: int = 1) -> str:
        """
        Format a table as Markdown table.

        Args:
            table: Table object
            index: Table number for caption

        Returns:
            str: Markdown table
        """
        if not table.headers and not table.rows:
            return ""

        parts = []

        # Caption
        if table.caption:
            parts.append(f"\n**Table {index}:** {table.caption}\n")

        # Helper to convert any cell value to string
        def cell_str(val):
            if isinstance(val, list):
                return ', '.join(str(v) for v in val)
            return str(val) if val is not None else ''

        # Normalize headers to strings
        headers = [cell_str(h) for h in table.headers] if table.headers else []

        # Header row
        if headers:
            parts.append('| ' + ' | '.join(headers) + ' |')
            parts.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')

            # Data rows
            for row in table.rows:
                cells = [cell_str(c) for c in row]
                # Pad row to match headers
                padded_row = cells + [''] * (len(headers) - len(cells))
                parts.append('| ' + ' | '.join(padded_row) + ' |')

        return '\n'.join(parts) + '\n'
    
    def _apply_template(self, content: DocumentContent, template: str) -> str:
        """
        Apply a template to the document.
        
        Args:
            content: Document content
            template: Template name
            
        Returns:
            str: Templated Markdown
        """
        # Generate content parts
        paragraphs_md = '\n\n'.join(
            self._format_paragraph(para) for para in content.paragraphs
        )
        
        tables_md = ""
        if content.tables:
            tables_parts = []
            for i, table in enumerate(content.tables, 1):
                tables_parts.append(self._format_table(table, i))
            tables_md = '\n\n'.join(tables_parts)
        
        # Prepare template variables
        metadata = content.metadata or {}
        variables = {
            'title': content.title,
            'source': metadata.get('filename', 'Unknown'),
            'source_file': metadata.get('source', 'Unknown'),
            'date': datetime.now().strftime('%d %B %Y'),
            'word_count': str(content.word_count),
            'page_count': str(metadata.get('pages', 'N/A')),
            'content': paragraphs_md,
            'tables': tables_md,
            'abstract': content.paragraphs[0].text if content.paragraphs else '',
        }
        
        # Render template
        rendered = self._template_loader.render_template(template, **variables)
        
        if rendered:
            return rendered
        
        # Fallback to basic if template rendering fails
        logger.warning(f'Template rendering failed for {template}, using basic')
        return self._generate_basic_markdown(content)
    
    def _legal_template(self, content: DocumentContent) -> str:
        """
        Generate Markdown with legal document template.
        
        Args:
            content: Document content
            
        Returns:
            str: Legal-styled Markdown
        """
        parts = []
        
        # Legal document header
        parts.append(f"# {content.title}")
        parts.append("")
        parts.append("---")
        parts.append(f"**Document Source:** {content.metadata.get('filename', 'Unknown')}")
        parts.append(f"**Document Type:** {content.metadata.get('format', 'Unknown')}")
        parts.append(f"**Conversion Date:** {datetime.now().strftime('%d %B %Y')}")
        parts.append(f"**Word Count:** {content.word_count}")
        parts.append("---")
        parts.append("")
        
        # Content
        for para in content.paragraphs:
            parts.append(self._format_paragraph(para))
        
        # Tables
        if content.tables:
            parts.append("\n---\n")
            parts.append("## Lampiran (Tables)\n")
            for i, table in enumerate(content.tables, 1):
                parts.append(self._format_table(table, i))
        
        return '\n'.join(parts)
    
    def _academic_template(self, content: DocumentContent) -> str:
        """
        Generate Markdown with academic document template.
        
        Args:
            content: Document content
            
        Returns:
            str: Academic-styled Markdown
        """
        parts = []
        
        # Academic header
        parts.append(f"# {content.title}")
        parts.append("")
        
        # Abstract section
        parts.append("## Abstract")
        parts.append("")
        if content.paragraphs:
            # Use first paragraph as abstract
            parts.append(content.paragraphs[0].text)
            parts.append("")
        
        # Main content
        parts.append("## Document Content")
        parts.append("")
        
        for para in content.paragraphs[1:]:
            parts.append(self._format_paragraph(para))
        
        # Tables
        if content.tables:
            parts.append("\n## Data Tables\n")
            for i, table in enumerate(content.tables, 1):
                parts.append(self._format_table(table, i))
        
        return '\n'.join(parts)
    
    def save_file(
        self,
        content: DocumentContent,
        output_path: Path,
        template: Optional[str] = None
    ) -> bool:
        """
        Convert and save document to Markdown file.
        
        Args:
            content: Document content
            output_path: Output file path
            template: Optional template name
            
        Returns:
            bool: True if successfully saved
        """
        try:
            markdown = self.to_markdown(content, template)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown, encoding='utf-8')
            
            logger.info(f'Saved markdown to: {output_path}')
            return True
            
        except Exception as e:
            logger.error(f'Failed to save markdown: {e}', exc_info=True)
            return False
