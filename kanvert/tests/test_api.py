"""
Tests for FastAPI API endpoints.
"""

import pytest
import json
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from kanvert.core.base import ConversionResult, ConversionStatus
from kanvert.core.registry import converter_registry
from kanvert.services.markdown_pdf import MarkdownToPdfConverter
from kanvert.tests.conftest import TestBase


class TestConversionAPI(TestBase):
    """Test conversion API endpoints."""
    
    def setup_method(self):
        """Set up test method with registered converter."""
        # Register a mock converter for testing
        self.mock_converter = Mock()
        self.mock_converter.name = "test_markdown"
        self.mock_converter.supported_formats = ["pdf"]
        self.mock_converter.validate_request.return_value = True
        
        # Create successful result
        self.success_result = ConversionResult(
            job_id="test-123",
            status=ConversionStatus.COMPLETED,
            output_data=b"mock pdf data",
            output_filename="test.pdf",
            created_at=Mock(),
            completed_at=Mock()
        )
        
        self.mock_converter.convert.return_value = self.success_result
        converter_registry._converters["test_markdown"] = self.mock_converter
        converter_registry._format_mapping["pdf"] = ["test_markdown"]
    
    def teardown_method(self):
        """Clean up after test."""
        converter_registry._converters.clear()
        converter_registry._format_mapping.clear()
    
    def test_markdown_to_pdf_success(self, client, sample_markdown):
        """Test successful markdown to PDF conversion."""
        request_data = {
            "content": sample_markdown,
            "output_format": "pdf",
            "options": {"title": "Test Document"}
        }
        
        with patch.object(converter_registry, 'convert', return_value=self.success_result):
            response = client.post("/api/v1/convert/markdown-to-pdf", json=request_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["x-job-id"] == "test-123"
        assert response.content == b"mock pdf data"
    
    def test_markdown_to_pdf_empty_content(self, client):
        """Test markdown to PDF with empty content."""
        request_data = {
            "content": "",
            "output_format": "pdf"
        }
        
        response = client.post("/api/v1/convert/markdown-to-pdf", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_markdown_to_pdf_large_content(self, client):
        """Test markdown to PDF with content exceeding size limit."""
        large_content = "# Large Document\n" + "Large content " * 100000
        request_data = {
            "content": large_content,
            "output_format": "pdf"
        }
        
        response = client.post("/api/v1/convert/markdown-to-pdf", json=request_data)
        
        assert response.status_code == 413  # Request entity too large
    
    def test_markdown_to_pdf_conversion_failure(self, client, sample_markdown):
        """Test markdown to PDF conversion failure."""
        request_data = {
            "content": sample_markdown,
            "output_format": "pdf"
        }
        
        failed_result = ConversionResult(
            job_id="test-456",
            status=ConversionStatus.FAILED,
            error_message="Conversion failed",
            created_at=Mock()
        )
        
        with patch.object(converter_registry, 'convert', return_value=failed_result):
            response = client.post("/api/v1/convert/markdown-to-pdf", json=request_data)
        
        assert response.status_code == 500
        error_data = response.json()
        assert "Conversion failed" in error_data["detail"]
    
    def test_generic_convert_success(self, client, sample_markdown):
        """Test generic conversion endpoint."""
        request_data = {
            "content": sample_markdown,
            "output_format": "pdf",
            "options": {"title": "Generic Test"}
        }
        
        with patch.object(converter_registry, 'convert', return_value=self.success_result):
            response = client.post("/api/v1/convert/", json=request_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content == b"mock pdf data"
    
    def test_generic_convert_html_format(self, client):
        """Test generic conversion with HTML output."""
        request_data = {
            "content": "# Test",
            "output_format": "html"
        }
        
        html_result = ConversionResult(
            job_id="html-123",
            status=ConversionStatus.COMPLETED,
            output_data=b"<html><body><h1>Test</h1></body></html>",
            output_filename="test.html",
            created_at=Mock(),
            completed_at=Mock()
        )
        
        with patch.object(converter_registry, 'convert', return_value=html_result):
            response = client.post("/api/v1/convert/", json=request_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html"
    
    def test_get_supported_formats(self, client):
        """Test getting supported formats."""
        with patch.object(converter_registry, 'get_supported_formats', return_value=["pdf"]):
            with patch.object(converter_registry, 'list_converters', return_value=[{"name": "test"}]):
                response = client.get("/api/v1/convert/formats")
        
        assert response.status_code == 200
        data = response.json()
        assert "supported_formats" in data
        assert "converters" in data
    
    def test_get_converters(self, client):
        """Test getting converter information."""
        with patch.object(converter_registry, 'list_converters', return_value=[{"name": "test"}]):
            response = client.get("/api/v1/convert/converters")
        
        assert response.status_code == 200
        data = response.json()
        assert "converters" in data
        assert "total" in data
    
    def test_conversion_health_check(self, client):
        """Test conversion service health check."""
        health_data = {
            "status": "healthy",
            "total_converters": 1,
            "healthy_converters": 1,
            "converters": {"test": "healthy"}
        }
        
        with patch.object(converter_registry, 'health_check', return_value=health_data):
            response = client.get("/api/v1/convert/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_conversion_health_degraded(self, client):
        """Test conversion health check with degraded status."""
        health_data = {
            "status": "degraded",
            "total_converters": 2,
            "healthy_converters": 1,
            "converters": {"test1": "healthy", "test2": "unhealthy"}
        }
        
        with patch.object(converter_registry, 'health_check', return_value=health_data):
            response = client.get("/api/v1/convert/health")
        
        assert response.status_code == 207  # Multi-status
        data = response.json()
        assert data["status"] == "degraded"


class TestApplicationAPI(TestBase):
    """Test application-level API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Kanvert"
        assert "version" in data
        assert "description" in data
    
    def test_health_check(self, client):
        """Test application health check."""
        health_data = {
            "status": "healthy",
            "total_converters": 1,
            "healthy_converters": 1
        }
        
        with patch.object(converter_registry, 'health_check', return_value=health_data):
            response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data
        assert "status" in data
    
    def test_health_check_service_unavailable(self, client):
        """Test health check when services are unavailable."""
        health_data = {
            "status": "error",
            "total_converters": 1,
            "healthy_converters": 0
        }
        
        with patch.object(converter_registry, 'health_check', return_value=health_data):
            response = client.get("/health")
        
        assert response.status_code == 503  # Service unavailable


class TestMCPAPI(TestBase):
    """Test MCP protocol API endpoints."""
    
    def test_mcp_capabilities(self, client):
        """Test MCP capabilities endpoint."""
        response = client.get("/api/v1/mcp/capabilities")
        
        assert response.status_code == 200
        data = response.json()
        assert "server" in data
        assert "tools" in data
        assert data["server"]["name"] == "kanvert"
    
    def test_mcp_tools_list(self, client):
        """Test MCP tools list endpoint."""
        response = client.get("/api/v1/mcp/tools")
        
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
    
    def test_mcp_call_list_tools(self, client):
        """Test MCP call to list tools."""
        request_data = {
            "method": "tools/list",
            "params": {}
        }
        
        response = client.post("/api/v1/mcp/call", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert data["error"] is None
    
    def test_mcp_call_convert_markdown(self, client):
        """Test MCP call to convert markdown."""
        request_data = {
            "method": "tools/call",
            "params": {
                "name": "convert_markdown_to_pdf",
                "arguments": {
                    "content": "# Test Document",
                    "title": "Test"
                }
            }
        }
        
        # Mock the conversion
        mock_result = ConversionResult(
            job_id="mcp-123",
            status=ConversionStatus.COMPLETED,
            output_data=b"pdf data",
            output_filename="test.pdf",
            created_at=Mock(),
            completed_at=Mock()
        )
        
        with patch.object(converter_registry, 'convert', return_value=mock_result):
            response = client.post("/api/v1/mcp/call", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["success"] is True
        assert data["result"]["job_id"] == "mcp-123"
    
    def test_mcp_call_unknown_method(self, client):
        """Test MCP call with unknown method."""
        request_data = {
            "method": "unknown/method",
            "params": {}
        }
        
        response = client.post("/api/v1/mcp/call", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["error"] is not None
        assert "Unknown method" in data["error"]
    
    def test_mcp_health_check(self, client):
        """Test MCP health check."""
        response = client.get("/api/v1/mcp/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "mcp_enabled" in data
        assert "status" in data


class TestMiddleware(TestBase):
    """Test middleware functionality."""
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/health")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
    
    def test_security_headers(self, client):
        """Test security headers are added."""
        response = client.get("/health")
        
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"
        assert "x-process-time" in response.headers
    
    def test_rate_limiting_headers(self, client):
        """Test rate limiting headers."""
        response = client.get("/health")
        
        assert "x-ratelimit-limit" in response.headers
        assert "x-ratelimit-remaining" in response.headers
        assert "x-ratelimit-reset" in response.headers
    
    def test_content_size_limit(self, client):
        """Test content size limiting middleware."""
        # This would require a very large request to test properly
        # For now, just verify the endpoint exists and works normally
        response = client.get("/health")
        assert response.status_code == 200


class TestErrorHandling(TestBase):
    """Test error handling and edge cases."""
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/v1/convert/markdown-to-pdf",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        
        assert response.status_code == 422  # Unprocessable entity
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        response = client.post("/api/v1/convert/markdown-to-pdf", json={})
        
        assert response.status_code == 422
        error_data = response.json()
        assert "field required" in str(error_data).lower()
    
    def test_invalid_output_format(self, client):
        """Test handling of invalid output format."""
        request_data = {
            "content": "# Test",
            "output_format": "invalid_format"
        }
        
        response = client.post("/api/v1/convert/", json=request_data)
        
        assert response.status_code == 422