"""
MCP (Model Context Protocol) integration for AI tool support.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json
import logging

from ..core.base import ConversionRequest, ConversionFormat
from ..core.registry import converter_registry
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class MCPTool(BaseModel):
    """MCP tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPRequest(BaseModel):
    """MCP request model."""
    method: str
    params: Dict[str, Any]


class MCPResponse(BaseModel):
    """MCP response model."""
    result: Optional[Any] = None
    error: Optional[str] = None


class MCPServer:
    """
    MCP (Model Context Protocol) server for document conversion tools.
    
    Provides AI models with document conversion capabilities through
    standardized tool interfaces.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, MCPTool]:
        """Register available MCP tools."""
        tools = {}
        
        # Markdown to PDF tool
        tools["convert_markdown_to_pdf"] = MCPTool(
            name="convert_markdown_to_pdf",
            description="Convert markdown content to a professionally formatted PDF document",
            input_schema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Markdown content to convert to PDF"
                    },
                    "title": {
                        "type": "string",
                        "description": "Document title for the PDF header"
                    },
                    "include_toc": {
                        "type": "boolean",
                        "description": "Include table of contents in the PDF",
                        "default": False
                    },
                    "custom_css": {
                        "type": "string",
                        "description": "Additional CSS styling for the PDF"
                    }
                },
                "required": ["content"]
            }
        )
        
        # Generic conversion tool
        tools["convert_document"] = MCPTool(
            name="convert_document",
            description="Convert document content between different formats",
            input_schema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Content to convert"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["pdf", "html", "docx"],
                        "description": "Target output format"
                    },
                    "options": {
                        "type": "object",
                        "description": "Format-specific conversion options"
                    }
                },
                "required": ["content", "output_format"]
            }
        )
        
        # List formats tool
        tools["list_supported_formats"] = MCPTool(
            name="list_supported_formats",
            description="Get list of supported document conversion formats and converters",
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
        
        return tools
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get MCP server capabilities."""
        return {
            "server": {
                "name": self.settings.mcp_server_name,
                "version": self.settings.mcp_version
            },
            "tools": [tool.dict() for tool in self.tools.values()],
            "protocol_version": "1.0.0"
        }
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle MCP tool requests.
        
        Args:
            request: MCP request containing method and parameters
            
        Returns:
            MCP response with result or error
        """
        try:
            if request.method == "tools/list":
                return MCPResponse(result={"tools": [tool.dict() for tool in self.tools.values()]})
            
            elif request.method == "tools/call":
                tool_name = request.params.get("name")
                arguments = request.params.get("arguments", {})
                
                if tool_name not in self.tools:
                    return MCPResponse(error=f"Unknown tool: {tool_name}")
                
                result = await self._execute_tool(tool_name, arguments)
                return MCPResponse(result=result)
            
            elif request.method == "server/capabilities":
                return MCPResponse(result=self.get_capabilities())
            
            else:
                return MCPResponse(error=f"Unknown method: {request.method}")
                
        except Exception as e:
            logger.error(f"MCP request error: {str(e)}")
            return MCPResponse(error=str(e))
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific MCP tool.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if tool_name == "convert_markdown_to_pdf":
            return await self._convert_markdown_to_pdf(arguments)
        
        elif tool_name == "convert_document":
            return await self._convert_document(arguments)
        
        elif tool_name == "list_supported_formats":
            return await self._list_supported_formats()
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _convert_markdown_to_pdf(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute markdown to PDF conversion."""
        content = arguments.get("content")
        if not content:
            raise ValueError("Content is required")
        
        # Build options
        options = {}
        if "title" in arguments:
            options["title"] = arguments["title"]
        if "include_toc" in arguments:
            options["include_toc"] = arguments["include_toc"]
        if "custom_css" in arguments:
            options["custom_css"] = arguments["custom_css"]
        
        # Create conversion request
        request = ConversionRequest(
            content=content,
            output_format=ConversionFormat.PDF,
            options=options
        )
        
        # Perform conversion
        result = await converter_registry.convert(request, "markdown_to_pdf")
        
        if result.status.value == "completed":
            # For MCP, we'll return metadata and indicate success
            # The actual PDF data would be handled separately
            return {
                "success": True,
                "job_id": result.job_id,
                "filename": result.output_filename,
                "size_bytes": len(result.output_data) if result.output_data else 0,
                "metadata": result.metadata,
                "message": "PDF generated successfully"
            }
        else:
            return {
                "success": False,
                "error": result.error_message,
                "job_id": result.job_id
            }
    
    async def _convert_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic document conversion."""
        content = arguments.get("content")
        output_format = arguments.get("output_format")
        
        if not content:
            raise ValueError("Content is required")
        if not output_format:
            raise ValueError("Output format is required")
        
        # Create conversion request
        request = ConversionRequest(
            content=content,
            output_format=ConversionFormat(output_format),
            options=arguments.get("options", {})
        )
        
        # Perform conversion
        result = await converter_registry.convert(request)
        
        if result.status.value == "completed":
            return {
                "success": True,
                "job_id": result.job_id,
                "filename": result.output_filename,
                "size_bytes": len(result.output_data) if result.output_data else 0,
                "metadata": result.metadata,
                "message": f"Conversion to {output_format} completed successfully"
            }
        else:
            return {
                "success": False,
                "error": result.error_message,
                "job_id": result.job_id
            }
    
    async def _list_supported_formats(self) -> Dict[str, Any]:
        """List supported conversion formats."""
        return {
            "supported_formats": converter_registry.get_supported_formats(),
            "converters": converter_registry.list_converters(),
            "total_converters": len(converter_registry._converters)
        }


# Global MCP server instance
mcp_server = MCPServer()