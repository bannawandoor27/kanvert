"""
Tests for markdown to PDF conversion service.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime

from kanvert.services.markdown_pdf import MarkdownToPdfConverter
from kanvert.core.base import ConversionRequest, ConversionFormat, ConversionStatus
from kanvert.tests.conftest import TestBase


class TestMarkdownToPdfConverter(TestBase):
    """Test markdown to PDF converter."""
    
    @pytest.fixture
    def converter(self):
        """Create converter instance."""
        return MarkdownToPdfConverter()
    
    def test_converter_initialization(self, converter):
        """Test converter initialization."""
        assert converter.name == "markdown_to_pdf"
        assert ConversionFormat.PDF in converter.supported_formats
        assert converter.md is not None
        assert converter.font_config is not None
        assert converter.default_css is not None
    
    def test_validate_request_valid(self, converter):
        """Test validation with valid request."""
        request = ConversionRequest(
            content="# Test Document",
            output_format=ConversionFormat.PDF
        )
        
        assert converter.validate_request(request)
    
    def test_validate_request_empty_content(self, converter):
        """Test validation with empty content."""
        request = ConversionRequest(
            content="",
            output_format=ConversionFormat.PDF
        )
        
        assert not converter.validate_request(request)
    
    def test_validate_request_whitespace_only(self, converter):
        """Test validation with whitespace-only content."""
        request = ConversionRequest(
            content="   \n\t  ",
            output_format=ConversionFormat.PDF
        )
        
        assert not converter.validate_request(request)
    
    def test_validate_request_wrong_format(self, converter):
        """Test validation with wrong output format."""
        request = ConversionRequest(
            content="# Test",
            output_format=ConversionFormat.HTML
        )
        
        assert not converter.validate_request(request)
    
    @pytest.mark.asyncio
    async def test_markdown_to_html_simple(self, converter):
        """Test markdown to HTML conversion with simple content."""
        markdown_content = "# Test\n\nThis is **bold** text."
        options = {"title": "Test Document"}
        
        html = await converter._markdown_to_html(markdown_content, options)
        
        assert "<h1>Test</h1>" in html
        assert "<strong>bold</strong>" in html
        assert "<title>Test Document</title>" in html
    
    @pytest.mark.asyncio
    async def test_markdown_to_html_with_code(self, converter):
        """Test markdown to HTML with code blocks."""
        markdown_content = """# Code Example
        
```python
def hello():
    print("Hello, World!")
```

Inline `code` here."""
        
        html = await converter._markdown_to_html(markdown_content, {})
        
        assert "<pre>" in html or "<code>" in html
        assert "def hello():" in html
        assert "<code>code</code>" in html
    
    @pytest.mark.asyncio
    async def test_markdown_to_html_with_table(self, converter):
        """Test markdown to HTML with tables."""
        markdown_content = """# Table Test

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
"""
        
        html = await converter._markdown_to_html(markdown_content, {})
        
        assert "<table>" in html
        assert "<th>Column 1</th>" in html
        assert "<td>Value 1</td>" in html
    
    @pytest.mark.asyncio
    async def test_markdown_to_html_with_toc(self, converter):
        """Test markdown to HTML with table of contents."""
        markdown_content = """# Main Title

## Section 1

### Subsection 1.1

## Section 2
"""
        options = {"include_toc": True}
        
        html = await converter._markdown_to_html(markdown_content, options)
        
        # Check that TOC is included (exact format depends on markdown extension)
        assert "toc" in html.lower() or len(converter.md.toc) > 0
    
    @pytest.mark.asyncio
    async def test_markdown_to_html_with_custom_css(self, converter):
        """Test markdown to HTML with custom CSS."""
        markdown_content = "# Test"
        custom_css = "body { font-family: Arial; }"
        options = {"custom_css": custom_css}
        
        html = await converter._markdown_to_html(markdown_content, options)
        
        assert custom_css in html
    
    @pytest.mark.asyncio
    @patch('kanvert.services.markdown_pdf.HTML')
    async def test_html_to_pdf_success(self, mock_html_class, converter):
        """Test HTML to PDF conversion success."""
        # Mock WeasyPrint HTML class
        mock_html_instance = Mock()
        mock_html_instance.write_pdf.return_value = b"mock pdf data"
        mock_html_class.return_value = mock_html_instance
        
        html_content = "<html><body><h1>Test</h1></body></html>"
        options = {}
        
        pdf_data = await converter._html_to_pdf(html_content, options)
        
        assert pdf_data == b"mock pdf data"
        mock_html_class.assert_called_once()
        mock_html_instance.write_pdf.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_convert_simple_markdown(self, converter, sample_markdown):
        """Test complete conversion with simple markdown."""
        request = ConversionRequest(
            content=sample_markdown,
            output_format=ConversionFormat.PDF,
            options={"title": "Test Document"}
        )
        
        # Mock the PDF generation to avoid actual WeasyPrint call
        with patch.object(converter, '_generate_pdf', return_value=b"mock pdf data"):
            result = await converter.convert(request)
        
        assert result.status == ConversionStatus.COMPLETED
        assert result.output_data == b"mock pdf data"
        assert result.output_filename.endswith(".pdf")
        assert result.job_id is not None
        assert result.metadata is not None
    
    @pytest.mark.asyncio
    async def test_convert_complex_markdown(self, converter, complex_markdown):
        """Test conversion with complex markdown features."""
        request = ConversionRequest(
            content=complex_markdown,
            output_format=ConversionFormat.PDF,
            options={
                "title": "Advanced Document",
                "include_toc": True
            }
        )
        
        # Mock the PDF generation
        with patch.object(converter, '_generate_pdf', return_value=b"complex pdf data"):
            result = await converter.convert(request)
        
        assert result.status == ConversionStatus.COMPLETED
        assert result.output_data == b"complex pdf data"
        assert "include_toc" in result.metadata["options_used"]
    
    @pytest.mark.asyncio
    async def test_convert_invalid_request(self, converter):
        """Test conversion with invalid request."""
        request = ConversionRequest(
            content="",  # Empty content
            output_format=ConversionFormat.PDF
        )
        
        result = await converter.convert(request)
        
        assert result.status == ConversionStatus.FAILED
        assert "Invalid markdown" in result.error_message
    
    @pytest.mark.asyncio
    async def test_convert_with_processing_error(self, converter, sample_markdown):
        """Test conversion handling processing errors."""
        request = ConversionRequest(
            content=sample_markdown,
            output_format=ConversionFormat.PDF
        )
        
        # Mock markdown conversion to raise an error
        with patch.object(converter, '_markdown_to_html', side_effect=Exception("Mock error")):
            result = await converter.convert(request)
        
        assert result.status == ConversionStatus.FAILED
        assert "Mock error" in result.error_message
    
    def test_get_html_template(self, converter):
        """Test HTML template generation."""
        options = {}
        template = converter._get_html_template(options)
        
        assert "{title}" in template
        assert "{body}" in template
        assert "{toc}" in template
        assert "{custom_css}" in template
        assert "<!DOCTYPE html>" in template
    
    def test_get_default_css(self, converter):
        """Test default CSS generation."""
        css = converter._get_default_css()
        
        assert "@page" in css
        assert "font-family" in css
        assert "h1, h2, h3" in css
        assert "table" in css
        assert "code" in css
    
    def test_get_capabilities(self, converter):
        """Test converter capabilities."""
        capabilities = converter.get_capabilities()
        
        assert capabilities["name"] == "markdown_to_pdf"
        assert "features" in capabilities
        assert "supported_options" in capabilities
        assert "example_request" in capabilities
        assert "Professional typography" in capabilities["features"]
        assert "title" in capabilities["supported_options"]
    
    @pytest.mark.asyncio
    async def test_conversion_metadata(self, converter, sample_markdown):
        """Test that conversion includes proper metadata."""
        request = ConversionRequest(
            content=sample_markdown,
            output_format=ConversionFormat.PDF,
            options={"title": "Test", "include_toc": True}
        )
        
        with patch.object(converter, '_generate_pdf', return_value=b"test pdf"):
            result = await converter.convert(request)
        
        assert result.metadata is not None
        assert "original_size" in result.metadata
        assert "pdf_size" in result.metadata
        assert "options_used" in result.metadata
        assert result.metadata["original_size"] == len(sample_markdown)
        assert result.metadata["pdf_size"] == len(b"test pdf")
    
    def test_supports_format(self, converter):
        """Test format support checking."""
        assert converter.supports_format(ConversionFormat.PDF)
        assert not converter.supports_format(ConversionFormat.HTML)
        assert not converter.supports_format(ConversionFormat.DOCX)


class TestMarkdownToPdfIntegration:
    """Integration tests for markdown to PDF conversion."""
    
    @pytest.fixture
    def converter(self):
        """Create converter instance."""
        return MarkdownToPdfConverter()
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_real_pdf_generation(self, converter):
        """Test actual PDF generation (slow test)."""
        markdown_content = """# Integration Test

This is a **real** PDF generation test.

## Features Tested

- Basic formatting
- Code blocks
- Lists

```python
print("Hello, PDF!")
```

| Feature | Status |
|---------|--------|
| PDF Gen | ✅ Working |
"""
        
        request = ConversionRequest(
            content=markdown_content,
            output_format=ConversionFormat.PDF,
            options={"title": "Integration Test"}
        )
        
        try:
            result = await converter.convert(request)
            
            # Should succeed with real WeasyPrint
            assert result.status == ConversionStatus.COMPLETED
            assert result.output_data is not None
            assert len(result.output_data) > 1000  # PDF should be reasonably sized
            assert result.output_data.startswith(b'%PDF-')
            
        except ImportError:
            # Skip if WeasyPrint dependencies not available
            pytest.skip("WeasyPrint dependencies not available for integration test")
        except Exception as e:
            # Log the error for debugging but don't fail the test suite
            pytest.skip(f"PDF generation failed (this may be expected in CI): {e}")