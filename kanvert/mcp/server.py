"""
MCP (Model Context Protocol) server using the official FastMCP framework.
"""

import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

from ..core.base import ConversionRequest, ConversionFormat, ConversionStatus
from ..core.registry import converter_registry
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Application context for MCP server."""
    settings: Any
    registry: Any


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle for MCP server."""
    settings = get_settings()
    logger.info("Starting MCP server", server_name=settings.mcp_server_name)
    
    try:
        yield AppContext(
            settings=settings,
            registry=converter_registry
        )
    finally:
        logger.info("Shutting down MCP server")


# Create the FastMCP server instance
mcp_server = FastMCP(
    name="kanvert",
    lifespan=app_lifespan
)


@mcp_server.tool()
async def convert_markdown_to_pdf(
    content: str,
    title: Optional[str] = None,
    include_toc: bool = False,
    custom_css: Optional[str] = None,
    ctx: Context[ServerSession, AppContext] = None
) -> Dict[str, Any]:
    """
    Convert markdown content to a professionally formatted PDF document.
    
    Args:
        content: Markdown content to convert to PDF
        title: Document title for the PDF header
        include_toc: Include table of contents in the PDF
        custom_css: Additional CSS styling for the PDF
        ctx: MCP context (automatically injected)
        
    Returns:
        Conversion result with success status and metadata
    """
    try:
        if not content or not content.strip():
            raise ValueError("Content is required and cannot be empty")
        
        await ctx.info(f"Starting markdown to PDF conversion")
        
        # Build conversion options
        options = {}
        if title:
            options["title"] = title
        if include_toc:
            options["include_toc"] = include_toc
        if custom_css:
            options["custom_css"] = custom_css
        
        # Create conversion request
        request = ConversionRequest(
            content=content,
            output_format=ConversionFormat.PDF,
            options=options
        )
        
        # Perform conversion using the registry
        registry = ctx.request_context.lifespan_context.registry
        result = await registry.convert(request, "markdown_to_pdf")
        
        if result.status == ConversionStatus.COMPLETED:
            await ctx.info(f"Conversion completed successfully: {result.job_id}")
            return {
                "success": True,
                "job_id": result.job_id,
                "filename": result.output_filename,
                "size_bytes": len(result.output_data) if result.output_data else 0,
                "metadata": result.metadata,
                "message": "PDF generated successfully"
            }
        else:
            await ctx.error(f"Conversion failed: {result.error_message}")
            return {
                "success": False,
                "error": result.error_message,
                "job_id": result.job_id
            }
    
    except Exception as e:
        error_msg = f"Failed to convert markdown to PDF: {str(e)}"
        await ctx.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


@mcp_server.tool()
async def convert_document(
    content: str,
    output_format: str,
    options: Optional[Dict[str, Any]] = None,
    ctx: Context[ServerSession, AppContext] = None
) -> Dict[str, Any]:
    """
    Convert document content between different formats.
    
    Args:
        content: Content to convert
        output_format: Target output format (pdf, html, docx)
        options: Format-specific conversion options
        ctx: MCP context (automatically injected)
        
    Returns:
        Conversion result with success status and metadata
    """
    try:
        if not content or not content.strip():
            raise ValueError("Content is required and cannot be empty")
        
        # Validate output format
        try:
            format_enum = ConversionFormat(output_format.lower())
        except ValueError:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        await ctx.info(f"Starting conversion to {output_format}")
        
        # Create conversion request
        request = ConversionRequest(
            content=content,
            output_format=format_enum,
            options=options or {}
        )
        
        # Perform conversion using the registry
        registry = ctx.request_context.lifespan_context.registry
        result = await registry.convert(request)
        
        if result.status == ConversionStatus.COMPLETED:
            await ctx.info(f"Conversion to {output_format} completed: {result.job_id}")
            return {
                "success": True,
                "job_id": result.job_id,
                "filename": result.output_filename,
                "size_bytes": len(result.output_data) if result.output_data else 0,
                "metadata": result.metadata,
                "message": f"Conversion to {output_format} completed successfully"
            }
        else:
            await ctx.error(f"Conversion to {output_format} failed: {result.error_message}")
            return {
                "success": False,
                "error": result.error_message,
                "job_id": result.job_id
            }
    
    except Exception as e:
        error_msg = f"Failed to convert document: {str(e)}"
        await ctx.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


@mcp_server.tool()
async def list_supported_formats(
    ctx: Context[ServerSession, AppContext] = None
) -> Dict[str, Any]:
    """
    Get list of supported document conversion formats and converters.
    
    Args:
        ctx: MCP context (automatically injected)
        
    Returns:
        Dictionary with supported formats and converter information
    """
    try:
        await ctx.info("Retrieving supported formats")
        
        registry = ctx.request_context.lifespan_context.registry
        
        return {
            "supported_formats": registry.get_supported_formats(),
            "converters": registry.list_converters(),
            "total_converters": len(registry._converters)
        }
    
    except Exception as e:
        error_msg = f"Failed to retrieve supported formats: {str(e)}"
        await ctx.error(error_msg)
        return {
            "error": error_msg
        }


@mcp_server.tool()
async def health_check(
    ctx: Context[ServerSession, AppContext] = None
) -> Dict[str, Any]:
    """
    Perform health check on the conversion services.
    
    Args:
        ctx: MCP context (automatically injected)
        
    Returns:
        Health status information
    """
    try:
        await ctx.debug("Performing health check")
        
        registry = ctx.request_context.lifespan_context.registry
        settings = ctx.request_context.lifespan_context.settings
        
        health_status = registry.health_check()
        health_status.update({
            "mcp_server": {
                "name": settings.mcp_server_name,
                "version": settings.mcp_version,
                "enabled": settings.mcp_enabled
            },
            "timestamp": health_status.get("timestamp")
        })
        
        await ctx.info(f"Health check completed: {health_status['status']}")
        return health_status
    
    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        await ctx.error(error_msg)
        return {
            "status": "error",
            "error": error_msg
        }


# Resource for getting server information
@mcp_server.resource("server://info")
async def get_server_info() -> str:
    """
    Get server information and capabilities.
    
    Returns:
        JSON string with server information
    """
    settings = get_settings()
    info = {
        "name": "Kanvert MCP Server",
        "description": "Professional document conversion server with MCP support",
        "version": settings.app_version,
        "mcp_version": settings.mcp_version,
        "capabilities": {
            "document_conversion": True,
            "markdown_to_pdf": True,
            "custom_styling": True,
            "table_of_contents": True,
            "math_equations": True,
            "code_highlighting": True
        },
        "supported_formats": converter_registry.get_supported_formats()
    }
    
    import json
    return json.dumps(info, indent=2)


# Prompt for document conversion assistance
@mcp_server.prompt()
async def conversion_assistant(
    task: str,
    format: str = "pdf",
    style: str = "professional"
) -> str:
    """
    Generate a prompt for document conversion assistance.
    
    Args:
        task: The conversion task to assist with
        format: Target format for the conversion
        style: Style preference for the output
        
    Returns:
        Formatted prompt for the AI assistant
    """
    styles = {
        "professional": "clean, business-appropriate formatting with proper typography",
        "academic": "scholarly formatting with citations and formal structure",
        "creative": "visually appealing with custom styling and graphics",
        "technical": "code-focused with syntax highlighting and technical diagrams"
    }
    
    style_desc = styles.get(style, styles["professional"])
    
    return f"""Please help with the following document conversion task:

Task: {task}
Target Format: {format.upper()}
Style: {style_desc}

Provide guidance on:
1. Content structure and organization
2. Formatting recommendations
3. Any special considerations for {format} output
4. Tips for optimal conversion quality

If you need to convert content, use the convert_markdown_to_pdf or convert_document tools available through this MCP server."""


def get_mcp_server() -> FastMCP:
    """Get the configured MCP server instance."""
    return mcp_server