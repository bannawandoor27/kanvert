"""
MCP (Model Context Protocol) API routes for FastMCP integration.
"""

import json
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from io import StringIO

from .server import get_mcp_server
from ..config.settings import get_settings, Settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp"])


class MCPToolCall(BaseModel):
    """Request model for MCP tool calls."""
    name: str
    arguments: Dict[str, Any] = {}


class MCPMessage(BaseModel):
    """MCP protocol message."""
    method: str
    params: Optional[Dict[str, Any]] = None


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
        mcp = get_mcp_server()
        
        # Get tools from FastMCP server
        tools_list = await mcp.list_tools()
        tools = []
        
        for tool in tools_list:
            tools.append({
                "name": tool.name,
                "description": tool.description or f"Tool: {tool.name}",
                "input_schema": tool.input_schema
            })
        
        # Get resources
        resource_templates = await mcp.list_resource_templates()
        resources = []
        for template in resource_templates:
            resources.append({
                "uri": template.uri_template,
                "name": template.name or template.uri_template,
                "description": template.description or f"Resource: {template.uri_template}"
            })
        
        # Get prompts
        prompts_list = await mcp.list_prompts()
        prompts = []
        for prompt in prompts_list:
            prompts.append({
                "name": prompt.name,
                "description": prompt.description or f"Prompt: {prompt.name}"
            })
        
        return {
            "server": {
                "name": settings.mcp_server_name,
                "version": settings.mcp_version
            },
            "protocol_version": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": True, "listChanged": True},
                "prompts": {"listChanged": True},
                "logging": {}
            },
            "tools": tools,
            "resources": resources,
            "prompts": prompts
        }
        
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
        mcp = get_mcp_server()
        tools_list = await mcp.list_tools()
        tools = []
        
        for tool in tools_list:
            tools.append({
                "name": tool.name,
                "description": tool.description or f"Tool: {tool.name}"
            })
        
        return {"tools": tools}
        
    except Exception as e:
        logger.error(f"Error listing MCP tools: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list MCP tools"
        )


@router.post("/call")
async def call_mcp_tool(
    tool_call: MCPToolCall,
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Execute an MCP tool call."""
    if not settings.mcp_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP protocol is disabled"
        )
    
    try:
        mcp = get_mcp_server()
        
        # Call the tool using FastMCP API
        try:
            result = await mcp.call_tool(tool_call.name, tool_call.arguments)
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as tool_error:
            logger.error(f"Tool execution error: {str(tool_error)}")
            return {
                "success": False,
                "error": str(tool_error)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MCP tool call error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute tool: {str(e)}"
        )


@router.get("/resources/{resource_uri:path}")
async def get_mcp_resource(
    resource_uri: str,
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Get an MCP resource by URI."""
    if not settings.mcp_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP protocol is disabled"
        )
    
    try:
        mcp = get_mcp_server()
        
        # Use FastMCP API to read resource
        try:
            content = await mcp.read_resource(resource_uri)
            return {
                "uri": resource_uri,
                "mimeType": "application/json",
                "text": content
            }
        except Exception as resource_error:
            logger.error(f"Resource error: {str(resource_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resource error: {str(resource_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MCP resource error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get resource: {str(e)}"
        )


@router.get("/health")
async def mcp_health_check(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Health check for MCP services."""
    try:
        mcp = get_mcp_server()
        tools_list = await mcp.list_tools()
        resource_templates = await mcp.list_resource_templates()
        prompts_list = await mcp.list_prompts()
        
        return {
            "mcp_enabled": settings.mcp_enabled,
            "server_name": settings.mcp_server_name,
            "version": settings.mcp_version,
            "tools_count": len(tools_list),
            "resources_count": len(resource_templates),
            "prompts_count": len(prompts_list),
            "status": "healthy" if settings.mcp_enabled else "disabled"
        }
    except Exception as e:
        logger.error(f"MCP health check error: {str(e)}")
        return {
            "mcp_enabled": settings.mcp_enabled,
            "status": "error",
            "error": str(e)
        }


# Additional endpoint for direct MCP protocol communication
@router.post("/protocol")
async def mcp_protocol_handler(
    request: Request,
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """Handle direct MCP protocol messages."""
    if not settings.mcp_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP protocol is disabled"
        )
    
    try:
        # This would be used for direct MCP protocol communication
        # For now, return a basic response
        body = await request.json()
        
        response = {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "message": "MCP protocol endpoint available",
                "server": settings.mcp_server_name
            }
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"MCP protocol error: {str(e)}")
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -1,
                "message": str(e)
            }
        }
        return JSONResponse(content=error_response, status_code=500)