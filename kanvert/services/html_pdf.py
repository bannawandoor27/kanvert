"""
Professional HTML to PDF conversion service using Chrome browser engine.
High-quality PDF generation from HTML content with full CSS support.
"""

import asyncio
import io
import logging
import base64
import json
from datetime import datetime
from typing import Any, Dict, Optional, List
from pathlib import Path
import tempfile
import urllib.parse

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

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


class HtmlToPdfConverter(BaseConverter):
    """
    Professional HTML to PDF conversion service using Chrome browser engine.
    
    Features:
    - Chrome browser engine for accurate rendering
    - Full CSS support including print styles
    - Custom page settings and margins
    - Header and footer support
    - JavaScript execution
    - High-resolution output
    - Batch processing
    - URL and HTML content support
    """
    
    def __init__(self):
        super().__init__(
            name="html_to_pdf",
            supported_formats=[ConversionFormat.PDF]
        )
        
        # Check available engines
        self.engines = []
        if PLAYWRIGHT_AVAILABLE:
            self.engines.append("playwright")
        if SELENIUM_AVAILABLE:
            self.engines.append("selenium")
        
        if not self.engines:
            logger.warning("No HTML to PDF engines available. Install playwright or selenium.")
        
        self.default_engine = self.engines[0] if self.engines else None
    
    def validate_request(self, request: ConversionRequest) -> bool:
        """Validate HTML to PDF conversion request."""
        if not request.content or not request.content.strip():
            return False
        
        if request.output_format != ConversionFormat.PDF:
            return False
        
        return True
    
    async def convert(self, request: ConversionRequest) -> ConversionResult:
        """
        Convert HTML content to PDF.
        
        Args:
            request: Conversion request with HTML content or URL
            
        Returns:
            ConversionResult with PDF data
        """
        job_id = f"html2pdf_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(request)}"
        
        try:
            logger.info(f"Starting HTML to PDF conversion: {job_id}")
            
            # Validate request
            if not self.validate_request(request):
                raise ValidationError("Invalid HTML to PDF conversion request", job_id)
            
            # Extract options
            options = request.options or {}
            engine = options.get('engine', self.default_engine)
            
            if engine not in self.engines:
                raise ProcessingError(f"Engine '{engine}' not available")
            
            # Convert HTML to PDF
            pdf_data = await self._convert_html_to_pdf(request.content, options, engine)
            
            # Create result
            result = ConversionResult(
                job_id=job_id,
                status=ConversionStatus.COMPLETED,
                output_data=pdf_data,
                output_filename=f"{job_id}.pdf",
                metadata={
                    "original_size": len(request.content),
                    "pdf_size": len(pdf_data),
                    "engine_used": engine,
                    "options_used": options
                },
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            
            logger.info(f"HTML to PDF conversion completed: {job_id}")
            return result
            
        except Exception as e:
            logger.error(f"HTML to PDF conversion failed: {job_id} - {str(e)}")
            return ConversionResult(
                job_id=job_id,
                status=ConversionStatus.FAILED,
                error_message=str(e),
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
    
    async def _convert_html_to_pdf(self, content: str, options: Dict[str, Any], engine: str) -> bytes:
        """Convert HTML content to PDF using specified engine."""
        
        if engine == "playwright":
            return await self._convert_with_playwright(content, options)
        elif engine == "selenium":
            return await self._convert_with_selenium(content, options)
        else:
            raise ProcessingError(f"Unknown engine: {engine}")
    
    async def _convert_with_playwright(self, content: str, options: Dict) -> bytes:
        """Convert HTML to PDF using Playwright."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
            )
            
            try:
                page = await browser.new_page()
                
                # Set viewport if specified
                if options.get('viewport'):
                    viewport = options['viewport']
                    await page.set_viewport_size(
                        width=viewport.get('width', 1920),
                        height=viewport.get('height', 1080)
                    )
                
                # Load content
                if self._is_url(content):
                    await page.goto(content, wait_until='networkidle')
                else:
                    await page.set_content(content, wait_until='networkidle')
                
                # Wait for any additional loading
                wait_time = options.get('wait_time', 1000)
                await page.wait_for_timeout(wait_time)
                
                # Execute custom JavaScript if provided
                if options.get('javascript'):
                    await page.evaluate(options['javascript'])
                
                # Configure PDF options
                pdf_options = self._build_playwright_pdf_options(options)
                
                # Generate PDF
                pdf_data = await page.pdf(**pdf_options)
                
                return pdf_data
                
            finally:
                await browser.close()
    
    async def _convert_with_selenium(self, content: str, options: Dict) -> bytes:
        """Convert HTML to PDF using Selenium Chrome."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--remote-debugging-port=9222')
        
        # Configure window size
        viewport = options.get('viewport', {})
        width = viewport.get('width', 1920)
        height = viewport.get('height', 1080)
        chrome_options.add_argument(f'--window-size={width},{height}')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Load content
            if self._is_url(content):
                driver.get(content)
            else:
                # Create temporary HTML file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                    f.write(content)
                    temp_path = f.name
                
                driver.get(f"file://{Path(temp_path).absolute()}")
            
            # Wait for page load
            wait_time = options.get('wait_time', 3)
            await asyncio.sleep(wait_time)
            
            # Execute custom JavaScript if provided
            if options.get('javascript'):
                driver.execute_script(options['javascript'])
            
            # Configure PDF print options
            print_options = self._build_selenium_pdf_options(options)
            
            # Generate PDF using Chrome DevTools Protocol
            pdf_data = driver.execute_cdp_cmd('Page.printToPDF', print_options)
            pdf_bytes = base64.b64decode(pdf_data['data'])
            
            return pdf_bytes
            
        finally:
            driver.quit()
            # Clean up temporary file if created
            if not self._is_url(content) and 'temp_path' in locals():
                Path(temp_path).unlink(missing_ok=True)
    
    def _is_url(self, content: str) -> bool:
        """Check if content is a URL."""
        return content.startswith(('http://', 'https://', 'file://'))
    
    def _build_playwright_pdf_options(self, options: Dict) -> Dict[str, Any]:
        """Build PDF options for Playwright."""
        pdf_options = {
            'format': options.get('page_size', 'A4'),
            'print_background': options.get('print_background', True),
            'prefer_css_page_size': options.get('prefer_css_page_size', False),
        }
        
        # Page margins
        if options.get('margins'):
            margins = options['margins']
            pdf_options['margin'] = {
                'top': margins.get('top', '1cm'),
                'bottom': margins.get('bottom', '1cm'),
                'left': margins.get('left', '1cm'),
                'right': margins.get('right', '1cm')
            }
        
        # Custom page size
        if options.get('page_width') and options.get('page_height'):
            pdf_options['width'] = options['page_width']
            pdf_options['height'] = options['page_height']
        
        # Header and footer
        if options.get('header_template'):
            pdf_options['display_header_footer'] = True
            pdf_options['header_template'] = options['header_template']
        
        if options.get('footer_template'):
            pdf_options['display_header_footer'] = True
            pdf_options['footer_template'] = options['footer_template']
        
        # Scale
        if options.get('scale'):
            pdf_options['scale'] = options['scale']
        
        # Landscape orientation
        if options.get('landscape'):
            pdf_options['landscape'] = True
        
        return pdf_options
    
    def _build_selenium_pdf_options(self, options: Dict) -> Dict[str, Any]:
        """Build PDF options for Selenium Chrome DevTools."""
        print_options = {
            'printBackground': options.get('print_background', True),
            'landscape': options.get('landscape', False),
            'preferCSSPageSize': options.get('prefer_css_page_size', False),
        }
        
        # Page size
        page_size = options.get('page_size', 'A4')
        if page_size == 'A4':
            print_options['paperWidth'] = 8.27
            print_options['paperHeight'] = 11.7
        elif page_size == 'Letter':
            print_options['paperWidth'] = 8.5
            print_options['paperHeight'] = 11
        elif options.get('page_width') and options.get('page_height'):
            print_options['paperWidth'] = options['page_width']
            print_options['paperHeight'] = options['page_height']
        
        # Margins
        if options.get('margins'):
            margins = options['margins']
            print_options['marginTop'] = self._parse_margin(margins.get('top', '1cm'))
            print_options['marginBottom'] = self._parse_margin(margins.get('bottom', '1cm'))
            print_options['marginLeft'] = self._parse_margin(margins.get('left', '1cm'))
            print_options['marginRight'] = self._parse_margin(margins.get('right', '1cm'))
        
        # Scale
        if options.get('scale'):
            print_options['scale'] = options['scale']
        
        # Header and footer
        if options.get('header_template'):
            print_options['displayHeaderFooter'] = True
            print_options['headerTemplate'] = options['header_template']
        
        if options.get('footer_template'):
            print_options['displayHeaderFooter'] = True
            print_options['footerTemplate'] = options['footer_template']
        
        return print_options
    
    def _parse_margin(self, margin_str: str) -> float:
        """Parse margin string to inches."""
        if margin_str.endswith('cm'):
            return float(margin_str[:-2]) / 2.54
        elif margin_str.endswith('mm'):
            return float(margin_str[:-2]) / 25.4
        elif margin_str.endswith('in'):
            return float(margin_str[:-2])
        elif margin_str.endswith('px'):
            return float(margin_str[:-2]) / 96  # 96 DPI
        else:
            # Assume inches
            return float(margin_str)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get converter capabilities."""
        return {
            "name": self.name,
            "description": "Professional HTML to PDF conversion using Chrome browser engine",
            "supported_formats": [fmt.value for fmt in self.supported_formats],
            "available_engines": self.engines,
            "features": [
                "Chrome browser engine for accurate rendering",
                "Full CSS support including print styles",
                "Custom page settings and margins",
                "Header and footer support",
                "JavaScript execution",
                "High-resolution output",
                "URL and HTML content support",
                "Batch processing"
            ],
            "supported_options": [
                "engine",
                "page_size",
                "page_width",
                "page_height",
                "margins",
                "scale",
                "landscape",
                "print_background",
                "header_template",
                "footer_template",
                "javascript",
                "wait_time",
                "viewport"
            ],
            "example_request": {
                "content": "<html><body><h1>Hello World</h1></body></html>",
                "output_format": "pdf",
                "options": {
                    "engine": "playwright",
                    "page_size": "A4",
                    "margins": {
                        "top": "1cm",
                        "bottom": "1cm",
                        "left": "1cm",
                        "right": "1cm"
                    },
                    "print_background": True,
                    "scale": 1.0
                }
            }
        }