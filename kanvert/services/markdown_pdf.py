"""
Markdown to PDF conversion service using WeasyPrint.
"""

import asyncio
import io
import logging
from datetime import datetime
from typing import Any, Dict, Optional, List
from pathlib import Path

import markdown
# Try to import WeasyPrint - make it optional
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    # Create placeholder classes for type hints
    class HTML:
        pass
    class CSS:
        pass
    class FontConfiguration:
        pass
from bs4 import BeautifulSoup

from ..core.base import (
    BaseConverter, 
    ConversionFormat, 
    ConversionRequest, 
    ConversionResult,
    ConversionStatus,
    ProcessingError,
    ValidationError
)

logger = logging.getLogger(__name__)


class MarkdownToPdfConverter(BaseConverter):
    """
    Professional markdown to PDF converter with advanced features.
    
    Features:
    - Custom CSS styling
    - Math equation support
    - Code syntax highlighting
    - Table support
    - Custom fonts
    - Header/footer support
    - Page numbering
    - Table of contents generation
    """
    
    def __init__(self):
        super().__init__(
            name="markdown_to_pdf",
            supported_formats=[ConversionFormat.PDF]
        )
    
    def _perform_initialization(self) -> None:
        """Initialize markdown converter with required dependencies."""
        if not WEASYPRINT_AVAILABLE:
            raise ImportError(
                "WeasyPrint is not available. Please install system dependencies: "
                "brew install cairo pango gdk-pixbuf libffi"
            )
        
        # Initialize markdown parser with extensions
        self.md = markdown.Markdown(extensions=[
            'extra',           # Tables, footnotes, etc.
            'codehilite',      # Code highlighting
            'toc',             # Table of contents
            'pymdownx.arithmatex',  # Math support
            'pymdownx.superfences',  # Advanced code blocks
            'pymdownx.tasklist',     # Task lists
            'pymdownx.emoji',        # Emoji support
        ])
        
        # Font configuration for WeasyPrint
        self.font_config = FontConfiguration()
        
        # Default CSS for professional styling
        self.default_css = self._get_default_css()
    
    def validate_request(self, request: ConversionRequest) -> bool:
        """Validate markdown to PDF conversion request."""
        if not request.content or not request.content.strip():
            return False
        
        if request.output_format != ConversionFormat.PDF:
            return False
        
        return True
    
    async def convert(self, request: ConversionRequest) -> ConversionResult:
        """
        Convert markdown content to PDF.
        
        Args:
            request: Conversion request with markdown content
            
        Returns:
            ConversionResult with PDF data
        """
        job_id = self._generate_job_id("md2pdf")
        
        try:
            logger.info(f"Starting markdown to PDF conversion: {job_id}")
            
            # Validate request
            if not self.validate_request(request):
                raise ValidationError("Invalid markdown to PDF conversion request", job_id)
            
            # Extract options
            options = request.options or {}
            
            # Convert markdown to HTML
            html_content = await self._markdown_to_html(request.content, options)
            
            # Generate PDF from HTML
            pdf_data = await self._html_to_pdf(html_content, options)
            
            # Create successful result
            return self._create_result_success(
                job_id=job_id,
                output_data=pdf_data,
                filename=f"{job_id}.pdf",
                metadata={
                    "original_size": len(request.content),
                    "pdf_size": len(pdf_data),
                    "options_used": options
                }
            )
            
        except Exception as e:
            logger.error(f"Conversion failed: {job_id} - {str(e)}")
            return self._create_result_failure(job_id, str(e))
    
    async def _markdown_to_html(self, markdown_content: str, options: Dict[str, Any]) -> str:
        """Convert markdown content to HTML."""
        try:
            # Reset the markdown processor
            self.md.reset()
            
            # Convert to HTML
            html_body = self.md.convert(markdown_content)
            
            # Get table of contents if generated
            toc = getattr(self.md, 'toc', '')
            
            # Build complete HTML document
            html_template = self._get_html_template(options)
            
            # Replace placeholders
            html_content = html_template.format(
                title=options.get('title', 'Document'),
                body=html_body,
                toc=toc if options.get('include_toc', False) else '',
                custom_css=options.get('custom_css', '')
            )
            
            # Clean up HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            return str(soup)
            
        except Exception as e:
            raise ProcessingError(f"Failed to convert markdown to HTML: {str(e)}")
    
    async def _html_to_pdf(self, html_content: str, options: Dict[str, Any]) -> bytes:
        """Convert HTML content to PDF using WeasyPrint."""
        try:
            # Run WeasyPrint in a thread to avoid blocking
            pdf_data = await self._run_in_executor(
                self._generate_pdf, 
                html_content, 
                options
            )
            return pdf_data
            
        except Exception as e:
            raise ProcessingError(f"Failed to convert HTML to PDF: {str(e)}")
    
    def _generate_pdf(self, html_content: str, options: Dict[str, Any]) -> bytes:
        """Generate PDF using WeasyPrint (blocking operation)."""
        # Create CSS list
        css_list = [CSS(string=self.default_css, font_config=self.font_config)]
        
        # Add custom CSS if provided
        if 'custom_css' in options:
            css_list.append(CSS(string=options['custom_css'], font_config=self.font_config))
        
        # Create HTML object
        html_obj = HTML(string=html_content)
        
        # Generate PDF
        pdf_bytes = html_obj.write_pdf(
            stylesheets=css_list,
            font_config=self.font_config
        )
        
        return pdf_bytes
    
    def _get_html_template(self, options: Dict[str, Any]) -> str:
        """Get HTML template with proper structure."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{custom_css}</style>
</head>
<body>
    {toc}
    <div class="content">
        {body}
    </div>
</body>
</html>'''
    
    def _get_default_css(self) -> str:
        """Get default CSS for professional PDF styling."""
        return '''
/* Professional PDF Styling */
@page {
    size: A4;
    margin: 2cm;
    @top-center {
        content: string(doc-title);
        font-size: 10pt;
        color: #666;
    }
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 10pt;
        color: #666;
    }
}

body {
    font-family: 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 0;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Arial', sans-serif;
    color: #2c3e50;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}

h1 {
    font-size: 24pt;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.3em;
    string-set: doc-title content();
}

h2 {
    font-size: 20pt;
    color: #34495e;
}

h3 {
    font-size: 16pt;
    color: #7f8c8d;
}

/* Paragraphs */
p {
    margin-bottom: 1em;
    text-align: justify;
}

/* Lists */
ul, ol {
    margin-left: 1.5em;
    margin-bottom: 1em;
}

li {
    margin-bottom: 0.3em;
}

/* Code blocks */
pre {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 1em;
    font-family: 'Courier New', monospace;
    font-size: 9pt;
    overflow-x: auto;
    page-break-inside: avoid;
}

code {
    background-color: #f8f9fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 9pt;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #ddd;
    padding: 0.5em;
    text-align: left;
}

th {
    background-color: #f8f9fa;
    font-weight: bold;
}

/* Blockquotes */
blockquote {
    margin: 1em 0;
    padding-left: 1em;
    border-left: 4px solid #3498db;
    background-color: #f8f9fa;
    font-style: italic;
}

/* Links */
a {
    color: #3498db;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* Images */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
}

/* Table of Contents */
#toc {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 1em;
    margin-bottom: 2em;
    page-break-after: always;
}

#toc h2 {
    margin-top: 0;
    color: #2c3e50;
}

#toc ul {
    list-style-type: none;
    margin-left: 0;
}

#toc a {
    text-decoration: none;
    color: #34495e;
}

/* Math equations */
.math {
    text-align: center;
    margin: 1em 0;
}

/* Task lists */
.task-list-item {
    list-style-type: none;
}

.task-list-item input[type="checkbox"] {
    margin-right: 0.5em;
}

/* Page breaks */
.page-break {
    page-break-before: always;
}

/* Print-specific styles */
@media print {
    * {
        -webkit-print-color-adjust: exact !important;
        color-adjust: exact !important;
    }
}
'''
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get converter capabilities with detailed options."""
        base_caps = super().get_capabilities()
        base_caps.update({
            "description": "Convert Markdown to high-quality PDF with professional styling",
            "features": [
                "Professional typography",
                "Code syntax highlighting", 
                "Math equation support",
                "Table of contents generation",
                "Custom CSS styling",
                "Page numbering",
                "Header/footer support",
                "Table and list formatting"
            ],
            "supported_options": {
                "title": "Document title for header",
                "include_toc": "Include table of contents",
                "custom_css": "Additional CSS styling",
                "page_size": "Page size (A4, Letter, etc.)",
                "margins": "Page margins"
            },
            "example_request": {
                "content": "# My Document\n\nThis is **markdown** content.",
                "output_format": "pdf",
                "options": {
                    "title": "My Document",
                    "include_toc": True
                }
            }
        })
        return base_caps