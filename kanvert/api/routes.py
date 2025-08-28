"""
FastAPI routes for document conversion endpoints.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging

from ..core.base import ConversionRequest, ConversionFormat, ConversionStatus, ComparisonRequest
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


class DocumentComparisonRequest(BaseModel):
    """API model for document comparison requests."""
    document_1: str = Field(..., description="First document (file path, URL, or base64 content)", min_length=1)
    document_2: str = Field(..., description="Second document (file path, URL, or base64 content)", min_length=1)
    comparison_type: str = Field(default="both", description="Type of comparison: 'content', 'formatting', or 'both'")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Comparison options")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Request metadata")


class OfficeConversionRequest(BaseModel):
    """API model for Office document conversion requests."""
    content: str = Field(..., description="Office document content (file path, URL, or base64 content)", min_length=1)
    input_format: str = Field(..., description="Input format (xlsx, pptx, docx, etc.)")
    output_format: ConversionFormat = Field(default=ConversionFormat.PDF, description="Target output format")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Conversion options")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Request metadata")


@router.post("/docx-compare", tags=["DOCX Compare"])
async def compare_docx_documents(
    request: DocumentComparisonRequest,
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """
    **DOCX Compare API - Compare Word documents for differences in content and formatting**
    
    This professional API analyzes two DOCX documents and provides detailed comparison results
    including content differences, formatting changes, and similarity scores.
    
    **Features:**
    - Content difference analysis with line-by-line comparison
    - Formatting comparison (styles, fonts, alignment)
    - Similarity scoring using advanced algorithms
    - Detailed reporting with actionable insights
    - Track changes visualization
    - Statistical analysis
    
    **Request Parameters:**
    - **document_1**: First DOCX document (file path, URL, or base64 content)
    - **document_2**: Second DOCX document (file path, URL, or base64 content)
    - **comparison_type**: Type of comparison ('content', 'formatting', or 'both')
    - **options**: Optional comparison settings:
        - **include_formatting**: Include formatting analysis (default: true)
        - **detailed_analysis**: Generate detailed report (default: true)
        - **similarity_threshold**: Minimum similarity score (0.0-1.0)
    
    **Response:**
    Returns comprehensive comparison results including differences found, similarity score,
    detailed analysis, and actionable recommendations.
    """
    try:
        # Validate content size
        total_size = len(request.document_1) + len(request.document_2)
        if total_size > settings.max_content_size * 2:  # Allow double size for comparison
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Combined document size exceeds maximum limit"
            )
        
        # Create comparison request
        comparison_request = ComparisonRequest(
            document_1=request.document_1,
            document_2=request.document_2,
            comparison_type=request.comparison_type,
            options=request.options or {},
            metadata=request.metadata
        )
        
        # Perform comparison using DOCX compare service
        converter = converter_registry.get_converter("docx_compare")
        if not converter:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="DOCX comparison service not available"
            )
        
        result = await converter.compare_documents(comparison_request)
        
        if result.status == ConversionStatus.COMPLETED:
            return {
                "job_id": result.job_id,
                "status": result.status.value,
                "differences_found": result.differences_found,
                "similarity_score": result.similarity_score,
                "summary": result.summary,
                "content_differences": result.content_differences,
                "formatting_differences": result.formatting_differences,
                "detailed_report": result.detailed_report,
                "metadata": result.metadata,
                "processing_time": (result.completed_at - result.created_at).total_seconds() if result.completed_at else None
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error_message or "Document comparison failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DOCX comparison error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal comparison error: {str(e)}"
        )


@router.post("/docx-to-pdf", tags=["DOCX to PDF"])
async def convert_docx_to_pdf(
    request: ConversionRequestModel,
    settings: Settings = Depends(get_settings)
) -> Response:
    """
    **DOCX to PDF API - Convert Word DOCX documents to PDF, fast and accurate**
    
    This professional API converts DOCX documents to high-quality PDF files while
    preserving formatting, layout, and document structure.
    
    **Features:**
    - High-quality PDF output with preserved formatting
    - Multiple conversion engines for optimal results
    - Custom page settings and margins
    - Password protection support
    - Batch processing capabilities
    - Watermark support
    
    **Request Parameters:**
    - **content**: DOCX document content (file path, URL, or base64 content)
    - **options**: Optional conversion settings:
        - **method**: Conversion method ('auto', 'docx2pdf', 'word_com', 'libreoffice')
        - **page_width**: Custom page width in inches
        - **page_height**: Custom page height in inches
        - **margins**: Page margins configuration
        - **password**: Password protection for output PDF
        - **bookmarks**: Include document bookmarks (default: true)
    
    **Response:**
    Returns the converted PDF file as binary data with appropriate headers.
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
        
        # Perform conversion using DOCX to PDF service
        result = await converter_registry.convert(conversion_request, "docx_to_pdf")
        
        if result.status == ConversionStatus.COMPLETED:
            return Response(
                content=result.output_data,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={result.output_filename}",
                    "X-Job-ID": result.job_id,
                    "X-Content-Size": str(len(result.output_data)),
                    "X-Conversion-Method": result.metadata.get("conversion_method", "unknown")
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error_message or "DOCX to PDF conversion failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DOCX to PDF conversion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal conversion error: {str(e)}"
        )


@router.post("/html-to-pdf", tags=["HTML to PDF"])
async def convert_html_to_pdf(
    request: ConversionRequestModel,
    settings: Settings = Depends(get_settings)
) -> Response:
    """
    **HTML to PDF API - HTML PDF generator API using Google Chrome browser**
    
    This professional API converts HTML content to PDF using the Chrome browser engine,
    ensuring accurate rendering with full CSS support and JavaScript execution.
    
    **Features:**
    - Chrome browser engine for pixel-perfect rendering
    - Full CSS support including print styles and media queries
    - JavaScript execution for dynamic content
    - Custom page settings and margins
    - Header and footer support with templates
    - High-resolution output
    - URL and HTML content support
    
    **Request Parameters:**
    - **content**: HTML content or URL to convert
    - **options**: Optional conversion settings:
        - **engine**: Browser engine ('playwright', 'selenium')
        - **page_size**: Page size ('A4', 'Letter', or custom)
        - **page_width**: Custom page width
        - **page_height**: Custom page height
        - **margins**: Page margins (top, bottom, left, right)
        - **landscape**: Landscape orientation (default: false)
        - **print_background**: Include background graphics (default: true)
        - **scale**: Page scale factor (0.1-2.0)
        - **header_template**: Custom header HTML template
        - **footer_template**: Custom footer HTML template
        - **javascript**: Custom JavaScript to execute
        - **wait_time**: Wait time for page loading (ms)
        - **viewport**: Browser viewport settings
    
    **Response:**
    Returns the converted PDF file as binary data with appropriate headers.
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
        
        # Perform conversion using HTML to PDF service
        result = await converter_registry.convert(conversion_request, "html_to_pdf")
        
        if result.status == ConversionStatus.COMPLETED:
            return Response(
                content=result.output_data,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={result.output_filename}",
                    "X-Job-ID": result.job_id,
                    "X-Content-Size": str(len(result.output_data)),
                    "X-Engine-Used": result.metadata.get("engine_used", "unknown")
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error_message or "HTML to PDF conversion failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"HTML to PDF conversion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal conversion error: {str(e)}"
        )


@router.post("/office-to-pdf", tags=["Office to PDF"])
async def convert_office_to_pdf(
    request: OfficeConversionRequest,
    settings: Settings = Depends(get_settings)
) -> Response:
    """
    **Office to PDF API - Convert Office documents to PDF, fast and accurate**
    
    This professional API converts various Office document formats (Excel, PowerPoint, Word)
    to high-quality PDF files while preserving charts, tables, and complex formatting.
    
    **Supported Formats:**
    - Excel: .xlsx, .xls, .xlsm
    - PowerPoint: .pptx, .ppt, .pptm
    - OpenDocument: .ods, .odp, .odt
    
    **Features:**
    - High-quality PDF output with preserved formatting
    - Multiple conversion engines for optimal results
    - Chart and image handling
    - Custom page settings and print areas
    - Batch processing support
    - Cross-platform compatibility
    
    **Request Parameters:**
    - **content**: Office document content (file path, URL, or base64 content)
    - **input_format**: Input format (xlsx, pptx, docx, etc.)
    - **options**: Optional conversion settings:
        - **method**: Conversion method ('auto', 'office_com', 'libreoffice', 'openpyxl_html')
        - **page_size**: Page size for output
        - **orientation**: Page orientation ('portrait', 'landscape')
        - **margins**: Page margins configuration
        - **fit_to_page**: Fit content to page (Excel)
        - **print_area**: Specific print area (Excel)
        - **worksheets**: Specific worksheets to convert (Excel)
        - **export_filter**: LibreOffice export filter
    
    **Response:**
    Returns the converted PDF file as binary data with appropriate headers.
    """
    try:
        # Validate content size
        if len(request.content) > settings.max_content_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Content size exceeds maximum limit of {settings.max_content_size} bytes"
            )
        
        # Add input format to options
        options = request.options or {}
        options['input_format'] = request.input_format
        
        # Create conversion request
        conversion_request = ConversionRequest(
            content=request.content,
            output_format=request.output_format,
            options=options,
            metadata=request.metadata
        )
        
        # Perform conversion using Office to PDF service
        result = await converter_registry.convert(conversion_request, "office_to_pdf")
        
        if result.status == ConversionStatus.COMPLETED:
            return Response(
                content=result.output_data,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={result.output_filename}",
                    "X-Job-ID": result.job_id,
                    "X-Content-Size": str(len(result.output_data)),
                    "X-Input-Format": request.input_format,
                    "X-Conversion-Method": result.metadata.get("conversion_method", "unknown")
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error_message or "Office to PDF conversion failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Office to PDF conversion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal conversion error: {str(e)}"
        )


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