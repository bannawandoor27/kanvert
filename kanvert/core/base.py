"""
Core base classes and interfaces for the document conversion system.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class ConversionFormat(str, Enum):
    """Supported conversion formats."""
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    TXT = "txt"
    RTF = "rtf"
    ODT = "odt"
    
    # Special format for comparison operations
    COMPARISON = "comparison"


class ConversionStatus(str, Enum):
    """Status of a conversion job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConversionRequest(BaseModel):
    """Base model for conversion requests."""
    content: str
    output_format: ConversionFormat
    options: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ComparisonRequest(BaseModel):
    """Model for document comparison requests."""
    document_1: str  # Content or file path of first document
    document_2: str  # Content or file path of second document
    comparison_type: str = "content"  # "content", "formatting", "both"
    options: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversionResult(BaseModel):
    """Result of a conversion operation."""
    job_id: str
    status: ConversionStatus
    output_data: Optional[bytes] = None
    output_filename: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class ComparisonResult(BaseModel):
    """Result of a document comparison operation."""
    job_id: str
    status: ConversionStatus
    differences_found: bool
    similarity_score: Optional[float] = None  # 0.0 to 1.0
    content_differences: Optional[Dict[str, Any]] = None
    formatting_differences: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    detailed_report: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class ConversionJob(BaseModel):
    """Represents a conversion job in the system."""
    job_id: str = None
    request: ConversionRequest
    result: Optional[ConversionResult] = None
    created_at: datetime = None
    
    def __init__(self, **data):
        if 'job_id' not in data or data['job_id'] is None:
            data['job_id'] = str(uuid.uuid4())
        if 'created_at' not in data or data['created_at'] is None:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)


class BaseConverter(ABC):
    """
    Abstract base class for all document converters.
    
    This class defines the interface that all converters must implement,
    ensuring consistency and extensibility across different conversion types.
    """
    
    def __init__(self, name: str, supported_formats: List[ConversionFormat]):
        self.name = name
        self.supported_formats = supported_formats
        self._health_status = "unknown"
        self._initialization_errors: List[str] = []
        self._is_initialized = False
        
        # Initialize the converter
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the converter. Override in subclasses for custom initialization."""
        try:
            self._perform_initialization()
            self._health_status = "healthy"
            self._is_initialized = True
        except Exception as e:
            self._health_status = "unhealthy"
            self._initialization_errors.append(str(e))
            self._is_initialized = False
    
    def _perform_initialization(self) -> None:
        """Override this method in subclasses for custom initialization logic."""
        pass
    
    @abstractmethod
    async def convert(self, request: ConversionRequest) -> ConversionResult:
        """
        Convert the input content to the specified format.
        
        Args:
            request: The conversion request containing content and options
            
        Returns:
            ConversionResult: The result of the conversion operation
            
        Raises:
            ConversionError: If the conversion fails
        """
        pass
    
    @abstractmethod
    def validate_request(self, request: ConversionRequest) -> bool:
        """
        Validate that the conversion request is valid for this converter.
        
        Args:
            request: The conversion request to validate
            
        Returns:
            bool: True if the request is valid, False otherwise
        """
        pass
    
    def supports_format(self, format: ConversionFormat) -> bool:
        """Check if this converter supports the given output format."""
        return format in self.supported_formats
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this converter."""
        return {
            "name": self.name,
            "supported_formats": [fmt.value for fmt in self.supported_formats],
            "description": self.__doc__ or f"{self.name} converter",
            "health_status": self._health_status,
            "is_initialized": self._is_initialized,
            "initialization_errors": self._initialization_errors
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status information."""
        return {
            "status": self._health_status,
            "is_initialized": self._is_initialized,
            "errors": self._initialization_errors,
            "supported_formats": [fmt.value for fmt in self.supported_formats]
        }
    
    def _create_result_success(
        self, 
        job_id: str, 
        output_data: bytes, 
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversionResult:
        """Helper to create successful conversion result."""
        return ConversionResult(
            job_id=job_id,
            status=ConversionStatus.COMPLETED,
            output_data=output_data,
            output_filename=filename or f"{job_id}.{self.supported_formats[0].value}",
            metadata=metadata,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
    
    def _create_result_failure(
        self, 
        job_id: str, 
        error_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversionResult:
        """Helper to create failed conversion result."""
        return ConversionResult(
            job_id=job_id,
            status=ConversionStatus.FAILED,
            error_message=error_message,
            metadata=metadata,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
    
    def _generate_job_id(self, prefix: Optional[str] = None) -> str:
        """Generate a unique job ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}"
        return f"{self.name}_{timestamp}_{unique_id}"
    
    async def _run_in_executor(self, func, *args):
        """Run a blocking function in an executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)


class ConversionError(Exception):
    """Custom exception for conversion errors."""
    
    def __init__(self, message: str, job_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.job_id = job_id
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ConversionError):
    """Exception raised when request validation fails."""
    pass


class ProcessingError(ConversionError):
    """Exception raised during document processing."""
    pass


class ConfigurationError(ConversionError):
    """Exception raised for configuration-related errors."""
    pass