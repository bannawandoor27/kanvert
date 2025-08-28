"""
Tests for core functionality - base classes and registry.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from kanvert.core.base import (
    BaseConverter, 
    ConversionFormat, 
    ConversionRequest, 
    ConversionResult,
    ConversionStatus,
    ConversionJob,
    ConversionError,
    ValidationError,
    ProcessingError
)
from kanvert.core.registry import ConverterRegistry


class MockConverter(BaseConverter):
    """Mock converter for testing."""
    
    def __init__(self, name="mock", formats=None, should_fail=False):
        super().__init__(name, formats or [ConversionFormat.PDF])
        self.should_fail = should_fail
        self.convert_called = False
        self.validate_called = False
    
    def validate_request(self, request: ConversionRequest) -> bool:
        self.validate_called = True
        if self.should_fail:
            return False
        return request.content and request.output_format in self.supported_formats
    
    async def convert(self, request: ConversionRequest) -> ConversionResult:
        self.convert_called = True
        
        if self.should_fail:
            return ConversionResult(
                job_id="test-job",
                status=ConversionStatus.FAILED,
                error_message="Mock conversion failed",
                created_at=datetime.utcnow()
            )
        
        return ConversionResult(
            job_id="test-job",
            status=ConversionStatus.COMPLETED,
            output_data=b"mock pdf data",
            output_filename="test.pdf",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )


class TestConversionModels:
    """Test core data models."""
    
    def test_conversion_request_creation(self):
        """Test ConversionRequest creation."""
        request = ConversionRequest(
            content="# Test",
            output_format=ConversionFormat.PDF,
            options={"title": "Test Document"}
        )
        
        assert request.content == "# Test"
        assert request.output_format == ConversionFormat.PDF
        assert request.options["title"] == "Test Document"
    
    def test_conversion_result_creation(self):
        """Test ConversionResult creation."""
        result = ConversionResult(
            job_id="test-123",
            status=ConversionStatus.COMPLETED,
            output_data=b"test data",
            created_at=datetime.utcnow()
        )
        
        assert result.job_id == "test-123"
        assert result.status == ConversionStatus.COMPLETED
        assert result.output_data == b"test data"
        assert result.created_at is not None
    
    def test_conversion_job_auto_id(self):
        """Test ConversionJob auto-generates ID and timestamp."""
        request = ConversionRequest(
            content="test",
            output_format=ConversionFormat.PDF
        )
        job = ConversionJob(request=request)
        
        assert job.job_id is not None
        assert job.created_at is not None
        assert job.request == request
    
    def test_conversion_errors(self):
        """Test custom exception classes."""
        # Test ConversionError
        error = ConversionError("Test error", job_id="job-123", details={"key": "value"})
        assert str(error) == "Test error"
        assert error.job_id == "job-123"
        assert error.details["key"] == "value"
        
        # Test ValidationError
        validation_error = ValidationError("Validation failed")
        assert str(validation_error) == "Validation failed"
        assert isinstance(validation_error, ConversionError)
        
        # Test ProcessingError
        processing_error = ProcessingError("Processing failed")
        assert str(processing_error) == "Processing failed"
        assert isinstance(processing_error, ConversionError)


class TestBaseConverter:
    """Test BaseConverter abstract class."""
    
    def test_converter_initialization(self):
        """Test converter initialization."""
        converter = MockConverter("test-converter", [ConversionFormat.PDF, ConversionFormat.HTML])
        
        assert converter.name == "test-converter"
        assert ConversionFormat.PDF in converter.supported_formats
        assert ConversionFormat.HTML in converter.supported_formats
    
    def test_supports_format(self):
        """Test format support checking."""
        converter = MockConverter(formats=[ConversionFormat.PDF])
        
        assert converter.supports_format(ConversionFormat.PDF)
        assert not converter.supports_format(ConversionFormat.HTML)
    
    def test_get_capabilities(self):
        """Test capabilities retrieval."""
        converter = MockConverter("test", [ConversionFormat.PDF])
        capabilities = converter.get_capabilities()
        
        assert capabilities["name"] == "test"
        assert "pdf" in capabilities["supported_formats"]
        assert "description" in capabilities
    
    @pytest.mark.asyncio
    async def test_successful_conversion(self):
        """Test successful conversion."""
        converter = MockConverter()
        request = ConversionRequest(
            content="# Test",
            output_format=ConversionFormat.PDF
        )
        
        result = await converter.convert(request)
        
        assert converter.convert_called
        assert result.status == ConversionStatus.COMPLETED
        assert result.output_data == b"mock pdf data"
    
    @pytest.mark.asyncio
    async def test_failed_conversion(self):
        """Test failed conversion."""
        converter = MockConverter(should_fail=True)
        request = ConversionRequest(
            content="# Test",
            output_format=ConversionFormat.PDF
        )
        
        result = await converter.convert(request)
        
        assert result.status == ConversionStatus.FAILED
        assert result.error_message == "Mock conversion failed"
    
    def test_validation(self):
        """Test request validation."""
        converter = MockConverter()
        
        # Valid request
        valid_request = ConversionRequest(
            content="# Test",
            output_format=ConversionFormat.PDF
        )
        assert converter.validate_request(valid_request)
        
        # Invalid request (unsupported format)
        invalid_request = ConversionRequest(
            content="# Test",
            output_format=ConversionFormat.DOCX
        )
        assert not converter.validate_request(invalid_request)


class TestConverterRegistry:
    """Test ConverterRegistry functionality."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = ConverterRegistry()
        
        assert len(registry._converters) == 0
        assert len(registry._format_mapping) == 0
    
    def test_register_converter(self):
        """Test converter registration."""
        registry = ConverterRegistry()
        converter = MockConverter("test", [ConversionFormat.PDF])
        
        registry.register_converter(converter)
        
        assert "test" in registry._converters
        assert registry._converters["test"] == converter
        assert "pdf" in registry._format_mapping
        assert "test" in registry._format_mapping["pdf"]
    
    def test_register_duplicate_converter(self):
        """Test registering duplicate converter raises error."""
        registry = ConverterRegistry()
        converter1 = MockConverter("test")
        converter2 = MockConverter("test")
        
        registry.register_converter(converter1)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register_converter(converter2)
    
    def test_unregister_converter(self):
        """Test converter unregistration."""
        registry = ConverterRegistry()
        converter = MockConverter("test", [ConversionFormat.PDF])
        
        registry.register_converter(converter)
        assert "test" in registry._converters
        
        registry.unregister_converter("test")
        assert "test" not in registry._converters
        assert "pdf" not in registry._format_mapping
    
    def test_get_converter(self):
        """Test getting converter by name."""
        registry = ConverterRegistry()
        converter = MockConverter("test")
        
        registry.register_converter(converter)
        
        assert registry.get_converter("test") == converter
        assert registry.get_converter("nonexistent") is None
    
    def test_get_converters_for_format(self):
        """Test getting converters by format."""
        registry = ConverterRegistry()
        converter1 = MockConverter("conv1", [ConversionFormat.PDF])
        converter2 = MockConverter("conv2", [ConversionFormat.PDF, ConversionFormat.HTML])
        
        registry.register_converter(converter1)
        registry.register_converter(converter2)
        
        pdf_converters = registry.get_converters_for_format(ConversionFormat.PDF)
        html_converters = registry.get_converters_for_format(ConversionFormat.HTML)
        
        assert len(pdf_converters) == 2
        assert len(html_converters) == 1
        assert converter1 in pdf_converters
        assert converter2 in pdf_converters
        assert converter2 in html_converters
    
    def test_find_best_converter(self):
        """Test finding best converter for request."""
        registry = ConverterRegistry()
        converter = MockConverter("test", [ConversionFormat.PDF])
        
        registry.register_converter(converter)
        
        request = ConversionRequest(
            content="# Test",
            output_format=ConversionFormat.PDF
        )
        
        best = registry.find_best_converter(request)
        assert best == converter
        
        # Test no converter for unsupported format
        unsupported_request = ConversionRequest(
            content="# Test",
            output_format=ConversionFormat.DOCX
        )
        
        best = registry.find_best_converter(unsupported_request)
        assert best is None
    
    @pytest.mark.asyncio
    async def test_registry_convert(self):
        """Test conversion through registry."""
        registry = ConverterRegistry()
        converter = MockConverter("test", [ConversionFormat.PDF])
        
        registry.register_converter(converter)
        
        request = ConversionRequest(
            content="# Test",
            output_format=ConversionFormat.PDF
        )
        
        result = await registry.convert(request)
        
        assert converter.convert_called
        assert result.status == ConversionStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_registry_convert_specific_converter(self):
        """Test conversion with specific converter name."""
        registry = ConverterRegistry()
        converter = MockConverter("test", [ConversionFormat.PDF])
        
        registry.register_converter(converter)
        
        request = ConversionRequest(
            content="# Test",
            output_format=ConversionFormat.PDF
        )
        
        result = await registry.convert(request, "test")
        
        assert converter.convert_called
        assert result.status == ConversionStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_registry_convert_no_converter(self):
        """Test conversion fails when no converter available."""
        registry = ConverterRegistry()
        
        request = ConversionRequest(
            content="# Test",
            output_format=ConversionFormat.PDF
        )
        
        with pytest.raises(ValidationError, match="No converter available"):
            await registry.convert(request)
    
    def test_list_converters(self):
        """Test listing all converters."""
        registry = ConverterRegistry()
        converter1 = MockConverter("conv1")
        converter2 = MockConverter("conv2")
        
        registry.register_converter(converter1)
        registry.register_converter(converter2)
        
        converters = registry.list_converters()
        
        assert len(converters) == 2
        names = [c["name"] for c in converters]
        assert "conv1" in names
        assert "conv2" in names
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        registry = ConverterRegistry()
        converter1 = MockConverter("conv1", [ConversionFormat.PDF])
        converter2 = MockConverter("conv2", [ConversionFormat.HTML])
        
        registry.register_converter(converter1)
        registry.register_converter(converter2)
        
        formats = registry.get_supported_formats()
        
        assert "pdf" in formats
        assert "html" in formats
    
    def test_health_check(self):
        """Test registry health check."""
        registry = ConverterRegistry()
        converter = MockConverter("test")
        
        registry.register_converter(converter)
        
        health = registry.health_check()
        
        assert health["total_converters"] == 1
        assert health["healthy_converters"] == 1
        assert health["status"] == "healthy"
        assert "test" in health["converters"]