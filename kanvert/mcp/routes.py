"""
MCP (Model Context Protocol) API routes.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import logging

from .server import mcp_server, MCPRequest, MCPResponse
from ..config.settings import get_settings, Settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp"])


class MCPCallRequest(BaseModel):
    """Request model for MCP tool calls."""
    method: str
    params: Dict[str, Any] = {}


@router.post("/call", response_model=MCPResponse)
async def mcp_call(
    request: MCPCallRequest,
    settings: Settings = Depends(get_settings)
) -> MCPResponse:
    """
    Execute MCP protocol calls.
    
    Supports standard MCP methods:
    - tools/list: List available tools
    - tools/call: Execute a specific tool
    - server/capabilities: Get server capabilities
    """
    if not settings.mcp_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP protocol is disabled"
        )
    
    try:
        mcp_request = MCPRequest(method=request.method, params=request.params)
        response = await mcp_server.handle_request(mcp_request)
        return response
        
    except Exception as e:
        logger.error(f"MCP call error: {str(e)}")
        return MCPResponse(error=str(e))


@router.get("/capabilities")
async def get_mcp_capabilities(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Get MCP server capabilities and available tools."""
    if not settings.mcp_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP protocol is disabled"
        )
    
    try:
        return mcp_server.get_capabilities()
    except Exception as e:
        logger.error(f"Error getting MCP capabilities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve MCP capabilities"
        )


@router.get("/tools")
async def list_mcp_tools(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """List all available MCP tools with their schemas."""
    if not settings.mcp_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP protocol is disabled"
        )
    
    try:
        request = MCPRequest(method="tools/list", params={})
        response = await mcp_server.handle_request(request)
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error
            )
        
        return response.result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing MCP tools: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list MCP tools"
        )


@router.get("/health")
async def mcp_health_check(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Health check for MCP services."""
    try:
        return {
            "mcp_enabled": settings.mcp_enabled,
            "server_name": settings.mcp_server_name,
            "version": settings.mcp_version,
            "tools_count": len(mcp_server.tools),
            "status": "healthy" if settings.mcp_enabled else "disabled"
        }
    except Exception as e:
        logger.error(f"MCP health check error: {str(e)}")
        return {
            "mcp_enabled": settings.mcp_enabled,
            "status": "error",
            "error": str(e)
        }