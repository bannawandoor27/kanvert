"""
Core base classes and interfaces for the document conversion system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from enum import Enum
from pydantic import BaseModel
import uuid
from datetime import datetime


class ConversionFormat(str, Enum):
    """Supported conversion formats."""
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    # Add more formats as needed


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
    
    def __init__(self, name: str, supported_formats: list[ConversionFormat]):
        self.name = name
        self.supported_formats = supported_formats
    
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
            "description": self.__doc__ or f"{self.name} converter"
        }


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