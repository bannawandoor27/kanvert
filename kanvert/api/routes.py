"""
FastAPI routes for document conversion endpoints.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging

from ..core.base import ConversionRequest, ConversionFormat, ConversionStatus
from ..core.registry import converter_registry
from ..config.settings import get_settings, Settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/convert", tags=["conversion"])


class ConversionRequestModel(BaseModel):
    """API model for conversion requests."""
    content: str = Field(..., description="Content to convert", min_length=1)
    output_format: ConversionFormat = Field(..., description="Target output format")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Conversion options")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Request metadata")


class ConversionResponseModel(BaseModel):
    """API model for conversion responses."""
    job_id: str
    status: ConversionStatus
    message: Optional[str] = None
    download_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ErrorResponseModel(BaseModel):
    """API model for error responses."""
    error: str
    message: str
    job_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@router.post("/markdown-to-pdf", response_model=ConversionResponseModel)
async def convert_markdown_to_pdf(
    request: ConversionRequestModel,
    settings: Settings = Depends(get_settings)
) -> ConversionResponseModel:
    """
    Convert markdown content to PDF.
    
    - **content**: Markdown content to convert
    - **options**: Optional conversion parameters:
        - **title**: Document title
        - **include_toc**: Include table of contents
        - **custom_css**: Additional CSS styling
    """
    try:
        # Validate content size
        if len(request.content) > settings.max_content_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Content size exceeds maximum limit of {settings.max_content_size} bytes"
            )
        
        # Create conversion request
        conversion_request = ConversionRequest(
            content=request.content,
            output_format=ConversionFormat.PDF,
            options=request.options,
            metadata=request.metadata
        )
        
        # Perform conversion
        result = await converter_registry.convert(conversion_request, "markdown_to_pdf")
        
        if result.status == ConversionStatus.COMPLETED:
            # Store PDF data temporarily (in production, use proper storage)
            # For now, we'll return the data directly
            return Response(
                content=result.output_data,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={result.output_filename}",
                    "X-Job-ID": result.job_id,
                    "X-Content-Size": str(len(result.output_data))
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error_message or "Conversion failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal conversion error: {str(e)}"
        )


@router.post("/", response_model=ConversionResponseModel)
async def convert_document(
    request: ConversionRequestModel,
    converter_name: Optional[str] = None,
    settings: Settings = Depends(get_settings)
) -> ConversionResponseModel:
    """
    Generic document conversion endpoint.
    
    - **content**: Content to convert
    - **output_format**: Target format (pdf, html, etc.)
    - **options**: Format-specific options
    - **converter_name**: Optional specific converter to use
    """
    try:
        # Validate content size
        if len(request.content) > settings.max_content_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Content size exceeds maximum limit of {settings.max_content_size} bytes"
            )
        
        # Create conversion request
        conversion_request = ConversionRequest(
            content=request.content,
            output_format=request.output_format,
            options=request.options,
            metadata=request.metadata
        )
        
        # Perform conversion
        result = await converter_registry.convert(conversion_request, converter_name)
        
        if result.status == ConversionStatus.COMPLETED:
            # Determine media type based on format
            media_type_map = {
                ConversionFormat.PDF: "application/pdf",
                ConversionFormat.HTML: "text/html",
                ConversionFormat.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }
            
            media_type = media_type_map.get(request.output_format, "application/octet-stream")
            
            return Response(
                content=result.output_data,
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename={result.output_filename}",
                    "X-Job-ID": result.job_id,
                    "X-Content-Size": str(len(result.output_data))
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error_message or "Conversion failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generic conversion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal conversion error: {str(e)}"
        )


@router.get("/formats")
async def get_supported_formats() -> Dict[str, Any]:
    """Get list of supported conversion formats and converters."""
    try:
        return {
            "supported_formats": converter_registry.get_supported_formats(),
            "converters": converter_registry.list_converters()
        }
    except Exception as e:
        logger.error(f"Error getting formats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve supported formats"
        )


@router.get("/converters")
async def get_converters() -> Dict[str, Any]:
    """Get detailed information about available converters."""
    try:
        return {
            "converters": converter_registry.list_converters(),
            "total": len(converter_registry._converters)
        }
    except Exception as e:
        logger.error(f"Error getting converters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve converter information"
        )


@router.get("/health")
async def conversion_health_check() -> Dict[str, Any]:
    """Health check for conversion services."""
    try:
        health_status = converter_registry.health_check()
        
        # Determine HTTP status based on health
        http_status = status.HTTP_200_OK
        if health_status["status"] == "degraded":
            http_status = status.HTTP_207_MULTI_STATUS
        elif health_status["healthy_converters"] == 0:
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            content=health_status,
            status_code=http_status
        )
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return JSONResponse(
            content={
                "status": "error",
                "message": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )