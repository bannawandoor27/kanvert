"""
Main FastAPI application for the Kanvert document conversion server.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import logging
import structlog

from .config.settings import get_settings
from .api.routes import router as conversion_router
from .api.middleware import setup_middleware
from .mcp.routes import router as mcp_router
from .core.registry import converter_registry
from .utils.logging_config import setup_logging

# Try to import WeasyPrint-dependent services
try:
    from .services.markdown_pdf import MarkdownToPdfConverter
    WEASYPRINT_AVAILABLE = True
except ImportError as e:
    WEASYPRINT_AVAILABLE = False
    import warnings
    warnings.warn(
        f"WeasyPrint dependencies not available: {e}. "
        "PDF conversion will be disabled. Install system dependencies: "
        "brew install cairo pango gdk-pixbuf libffi",
        ImportWarning
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    settings = get_settings()
    
    # Setup logging
    setup_logging(settings)
    logger = structlog.get_logger(__name__)
    
    # Startup
    logger.info("Starting Kanvert application", version=settings.app_version)
    
    try:
        # Register converters if available
        if WEASYPRINT_AVAILABLE:
            markdown_converter = MarkdownToPdfConverter()
            converter_registry.register_converter(markdown_converter)
            logger.info("Markdown to PDF converter registered")
        else:
            logger.warning("PDF conversion disabled - WeasyPrint dependencies missing")
        
        # Create temp directory if needed
        import os
        os.makedirs(settings.temp_dir, exist_ok=True)
        
        logger.info("Application startup completed")
        
        yield
        
    except Exception as e:
        logger.error("Failed to start application", error=str(e))
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Kanvert application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Kanvert",
        description="Professional Document Conversion MCP Server",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development() else None,
        redoc_url="/redoc" if settings.is_development() else None,
        openapi_url="/openapi.json" if settings.is_development() else None,
    )
    
    # Setup middleware
    setup_middleware(app, settings)
    
    # Include routers
    app.include_router(conversion_router, prefix=settings.api_prefix)
    app.include_router(mcp_router, prefix=settings.api_prefix)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Application health check."""
        try:
            health_status = converter_registry.health_check()
            
            # Add application info
            health_status.update({
                "app_name": settings.app_name,
                "app_version": settings.app_version,
                "environment": settings.environment,
                "status": health_status.get("status", "unknown")
            })
            
            # Determine HTTP status
            http_status = status.HTTP_200_OK
            if health_status["status"] == "degraded":
                http_status = status.HTTP_207_MULTI_STATUS
            elif health_status.get("healthy_converters", 0) == 0:
                http_status = status.HTTP_503_SERVICE_UNAVAILABLE
            
            return JSONResponse(content=health_status, status_code=http_status)
            
        except Exception as e:
            return JSONResponse(
                content={
                    "app_name": settings.app_name,
                    "status": "error",
                    "message": str(e)
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": "Professional Document Conversion MCP Server",
            "docs_url": "/docs" if settings.is_development() else None,
            "health_url": "/health",
            "api_prefix": settings.api_prefix,
            "supported_formats": converter_registry.get_supported_formats()
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler for unhandled errors."""
        logger = structlog.get_logger(__name__)
        logger.error(
            "Unhandled exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            error_type=type(exc).__name__
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }
        )
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "kanvert.main:app",
        **settings.get_uvicorn_config()
    )