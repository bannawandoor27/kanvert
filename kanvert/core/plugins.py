"""
Centralized plugin implementations for all converters.
"""

from typing import Any, Dict, List
from .factory import ConverterPlugin
from .base import BaseConverter


class MarkdownToPdfPlugin(ConverterPlugin):
    """Plugin for markdown to PDF conversion."""
    
    def get_name(self) -> str:
        return "markdown_to_pdf"
    
    def get_dependencies(self) -> List[str]:
        return [
            "weasyprint>=61.2",
            "markdown>=3.5.1", 
            "pymdown-extensions>=10.5",
            "beautifulsoup4>=4.12.2"
        ]
    
    def is_available(self) -> bool:
        try:
            from ..services.markdown_pdf import WEASYPRINT_AVAILABLE
            return WEASYPRINT_AVAILABLE
        except ImportError:
            return False
    
    def create_converter(self) -> BaseConverter:
        from ..services.markdown_pdf import MarkdownToPdfConverter
        return MarkdownToPdfConverter()
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.get_name(),
            "description": "Convert Markdown to high-quality PDF with professional styling",
            "version": "1.0.0",
            "author": "Kanvert Team",
            "supported_formats": ["pdf"],
            "features": [
                "Professional typography",
                "Code syntax highlighting",
                "Math equation support", 
                "Table of contents generation",
                "Custom CSS styling",
                "Page numbering",
                "Header/footer support"
            ],
            "dependencies": self.get_dependencies(),
            "available": self.is_available()
        }


class DocxToPdfPlugin(ConverterPlugin):
    """Plugin for DOCX to PDF conversion."""
    
    def get_name(self) -> str:
        return "docx_to_pdf"
    
    def get_dependencies(self) -> List[str]:
        return [
            "python-docx>=1.1.0",
            "docx2pdf>=0.1.8"
        ]
    
    def is_available(self) -> bool:
        try:
            import docx
            return True
        except ImportError:
            return False
    
    def create_converter(self) -> BaseConverter:
        from ..services.docx_pdf import DocxToPdfConverter
        return DocxToPdfConverter()
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.get_name(),
            "description": "Convert DOCX documents to PDF with formatting preservation",
            "version": "1.0.0",
            "author": "Kanvert Team",
            "supported_formats": ["pdf"],
            "features": [
                "Format preservation",
                "Multiple conversion engines",
                "Batch processing",
                "Password protection"
            ],
            "dependencies": self.get_dependencies(),
            "available": self.is_available()
        }


class HtmlToPdfPlugin(ConverterPlugin):
    """Plugin for HTML to PDF conversion."""
    
    def get_name(self) -> str:
        return "html_to_pdf"
    
    def get_dependencies(self) -> List[str]:
        return [
            "playwright>=1.40.0",
            "beautifulsoup4>=4.12.2"
        ]
    
    def is_available(self) -> bool:
        try:
            import playwright
            return True
        except ImportError:
            return False
    
    def create_converter(self) -> BaseConverter:
        from ..services.html_pdf import HtmlToPdfConverter
        return HtmlToPdfConverter()
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.get_name(),
            "description": "Convert HTML to PDF with modern browser rendering",
            "version": "1.0.0",
            "author": "Kanvert Team",
            "supported_formats": ["pdf"],
            "features": [
                "Modern CSS support",
                "JavaScript execution",
                "High-quality rendering",
                "Custom page settings"
            ],
            "dependencies": self.get_dependencies(),
            "available": self.is_available()
        }


class OfficeToPdfPlugin(ConverterPlugin):
    """Plugin for Office documents to PDF conversion."""
    
    def get_name(self) -> str:
        return "office_to_pdf"
    
    def get_dependencies(self) -> List[str]:
        return [
            "python-docx>=1.1.0",
            "openpyxl>=3.1.2",
            "python-pptx>=0.6.23"
        ]
    
    def is_available(self) -> bool:
        try:
            import docx
            import openpyxl
            import pptx
            return True
        except ImportError:
            return False
    
    def create_converter(self) -> BaseConverter:
        from ..services.office_pdf import OfficeToPdfConverter
        return OfficeToPdfConverter()
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.get_name(),
            "description": "Convert Office documents (DOCX, XLSX, PPTX) to PDF",
            "version": "1.0.0",
            "author": "Kanvert Team",
            "supported_formats": ["pdf"],
            "features": [
                "Multi-format support",
                "Batch processing",
                "Format preservation",
                "Cross-platform compatibility"
            ],
            "dependencies": self.get_dependencies(),
            "available": self.is_available()
        }


class DocxComparePlugin(ConverterPlugin):
    """Plugin for DOCX document comparison."""
    
    def get_name(self) -> str:
        return "docx_compare"
    
    def get_dependencies(self) -> List[str]:
        return [
            "python-docx>=1.1.0",
            "fuzzywuzzy>=0.18.0",
            "python-Levenshtein>=0.25.0"
        ]
    
    def is_available(self) -> bool:
        try:
            import docx
            import fuzzywuzzy
            return True
        except ImportError:
            return False
    
    def create_converter(self) -> BaseConverter:
        from ..services.docx_compare import DocxCompareService
        return DocxCompareService()
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.get_name(),
            "description": "Compare DOCX documents for content and formatting differences",
            "version": "1.0.0",
            "author": "Kanvert Team",
            "supported_formats": ["comparison"],
            "features": [
                "Content analysis",
                "Formatting comparison",
                "Similarity scoring",
                "Detailed reporting",
                "Track changes visualization"
            ],
            "dependencies": self.get_dependencies(),
            "available": self.is_available()
        }


# Plugin registry for easy discovery
AVAILABLE_PLUGINS = [
    MarkdownToPdfPlugin,
    DocxToPdfPlugin, 
    HtmlToPdfPlugin,
    OfficeToPdfPlugin,
    DocxComparePlugin
]


def get_all_plugins() -> List[ConverterPlugin]:
    """Get instances of all available plugins."""
    return [plugin_class() for plugin_class in AVAILABLE_PLUGINS]


def get_plugin_by_name(name: str) -> ConverterPlugin:
    """Get a plugin instance by name."""
    for plugin_class in AVAILABLE_PLUGINS:
        plugin = plugin_class()
        if plugin.get_name() == name:
            return plugin
    raise ValueError(f"Plugin '{name}' not found")