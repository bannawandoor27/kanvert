# Kanvert API Documentation

## Overview

Kanvert is a professional document conversion MCP (Model Context Protocol) server built with FastAPI. It provides high-quality document conversion services with a focus on markdown to PDF conversion.

## Quick Start

### Using Docker (Recommended)

```bash
# Clone and start the server
git clone <repository-url>
cd kanvert
docker-compose up --build

# The server will be available at http://localhost:8000
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Run the server
uvicorn kanvert.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Base URL
- Development: `http://localhost:8000`
- API Base Path: `/api/v1`

### Health Check

#### `GET /health`
Check the overall health of the application and conversion services.

**Response:**
```json
{
  "app_name": "Kanvert",
  "app_version": "1.0.0",
  "environment": "development",
  "status": "healthy",
  "total_converters": 1,
  "healthy_converters": 1,
  "converters": {
    "markdown_to_pdf": "healthy"
  },
  "supported_formats": ["pdf"]
}
```

### Document Conversion

#### `POST /api/v1/convert/markdown-to-pdf`
Convert markdown content to a professionally formatted PDF.

**Request Body:**
```json
{
  "content": "# My Document\n\nThis is **markdown** content with [links](https://example.com).",
  "output_format": "pdf",
  "options": {
    "title": "My Document Title",
    "include_toc": true,
    "custom_css": "body { font-family: Arial; }"
  },
  "metadata": {
    "author": "John Doe",
    "subject": "Document Conversion"
  }
}
```

**Response:**
- **Content-Type:** `application/pdf`
- **Headers:**
  - `Content-Disposition: attachment; filename=document.pdf`
  - `X-Job-ID: unique-job-identifier`
  - `X-Content-Size: size-in-bytes`

**Supported Options:**
- `title`: Document title for PDF header
- `include_toc`: Include table of contents (boolean)
- `custom_css`: Additional CSS styling
- `page_size`: Page size (A4, Letter, etc.)
- `margins`: Page margins

#### `POST /api/v1/convert/`
Generic document conversion endpoint supporting multiple formats.

**Request Body:**
```json
{
  "content": "# Document Content",
  "output_format": "pdf",
  "options": {},
  "metadata": {}
}
```

**Supported Formats:**
- `pdf`: Portable Document Format
- `html`: HyperText Markup Language
- `docx`: Microsoft Word Document (planned)

### Service Information

#### `GET /api/v1/convert/formats`
List supported conversion formats and available converters.

**Response:**
```json
{
  "supported_formats": ["pdf", "html"],
  "converters": [
    {
      "name": "markdown_to_pdf",
      "supported_formats": ["pdf"],
      "description": "Convert Markdown to high-quality PDF",
      "features": [
        "Professional typography",
        "Code syntax highlighting",
        "Math equation support",
        "Table of contents generation"
      ]
    }
  ]
}
```

#### `GET /api/v1/convert/converters`
Get detailed information about available converters.

#### `GET /api/v1/convert/health`
Health check specific to conversion services.

## MCP Protocol Support

Kanvert implements the Model Context Protocol for AI integration.

### MCP Endpoints

#### `GET /api/v1/mcp/capabilities`
Get MCP server capabilities and available tools.

**Response:**
```json
{
  "server": {
    "name": "kanvert",
    "version": "1.0.0"
  },
  "tools": [
    {
      "name": "convert_markdown_to_pdf",
      "description": "Convert markdown content to PDF",
      "input_schema": {
        "type": "object",
        "properties": {
          "content": {"type": "string"},
          "title": {"type": "string"},
          "include_toc": {"type": "boolean"}
        },
        "required": ["content"]
      }
    }
  ]
}
```

#### `POST /api/v1/mcp/call`
Execute MCP protocol calls.

**Available Methods:**
- `tools/list`: List available tools
- `tools/call`: Execute a specific tool
- `server/capabilities`: Get server capabilities

**Example Tool Call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "convert_markdown_to_pdf",
    "arguments": {
      "content": "# AI Generated Document\n\nThis PDF was generated via MCP.",
      "title": "AI Document",
      "include_toc": false
    }
  }
}
```

## Usage Examples

### Python Client

```python
import requests
import json

# Basic conversion
def convert_markdown_to_pdf(markdown_content, title=None):
    url = "http://localhost:8000/api/v1/convert/markdown-to-pdf"
    
    payload = {
        "content": markdown_content,
        "output_format": "pdf",
        "options": {
            "title": title or "Document",
            "include_toc": True
        }
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        # Save PDF
        with open("output.pdf", "wb") as f:
            f.write(response.content)
        print(f"PDF saved! Job ID: {response.headers.get('X-Job-ID')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Example usage
markdown = """
# My Report

## Introduction
This is a **sample report** generated from markdown.

## Features
- Professional formatting
- Code highlighting
- Math support: $E = mc^2$

## Code Example
```python
def hello_world():
    print("Hello from PDF!")
```

## Conclusion
Document conversion made easy!
"""

convert_markdown_to_pdf(markdown, "Sample Report")
```

### cURL Examples

```bash
# Basic conversion
curl -X POST "http://localhost:8000/api/v1/convert/markdown-to-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Hello PDF\n\nThis is **markdown** content.",
    "output_format": "pdf",
    "options": {
      "title": "Hello PDF",
      "include_toc": false
    }
  }' \
  --output document.pdf

# Check health
curl -X GET "http://localhost:8000/health"

# List supported formats
curl -X GET "http://localhost:8000/api/v1/convert/formats"

# MCP capabilities
curl -X GET "http://localhost:8000/api/v1/mcp/capabilities"
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');
const fs = require('fs');

async function convertMarkdownToPdf(content, options = {}) {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/v1/convert/markdown-to-pdf',
      {
        content: content,
        output_format: 'pdf',
        options: options
      },
      {
        responseType: 'arraybuffer',
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    // Save PDF
    fs.writeFileSync('output.pdf', response.data);
    console.log(`PDF saved! Job ID: ${response.headers['x-job-id']}`);
    
    return response.data;
  } catch (error) {
    console.error('Conversion failed:', error.response?.data || error.message);
    throw error;
  }
}

// Example usage
const markdown = `
# JavaScript Report

This document was generated using **Node.js** and the Kanvert API.

## Features
- Easy integration
- Professional output
- RESTful API

\`\`\`javascript
console.log("Hello from PDF!");
\`\`\`
`;

convertMarkdownToPdf(markdown, {
  title: "JavaScript Report",
  include_toc: true
});
```

## Advanced Features

### Custom CSS Styling

```json
{
  "content": "# Custom Styled Document\n\nThis has custom styling.",
  "output_format": "pdf",
  "options": {
    "custom_css": "
      body { font-family: 'Helvetica', sans-serif; }
      h1 { color: #2c3e50; border-bottom: 3px solid #3498db; }
      .highlight { background-color: yellow; }
    "
  }
}
```

### Math and Code Support

```markdown
# Technical Document

## Mathematical Formula
The quadratic formula is:

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

## Code Block with Syntax Highlighting
```python
import numpy as np
import matplotlib.pyplot as plt

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Plot
plt.plot(x, y)
plt.title('Sine Wave')
plt.show()
```

## Task List
- [x] Implement PDF generation
- [x] Add syntax highlighting
- [ ] Add more output formats
```

### Error Handling

```python
import requests

def safe_convert(content):
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/convert/markdown-to-pdf",
            json={"content": content, "output_format": "pdf"},
            timeout=30
        )
        response.raise_for_status()
        return response.content
    
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 413:
            print("Content too large")
        elif e.response.status_code == 422:
            print("Invalid request format")
        elif e.response.status_code == 500:
            print("Server error during conversion")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    return None
```

## Configuration

### Environment Variables

```bash
# Application Settings
APP_NAME=Kanvert
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-here
API_KEY=optional-api-key

# Conversion Limits
MAX_CONTENT_SIZE=5242880  # 5MB
CONVERSION_TIMEOUT=300    # 5 minutes

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# MCP Support
MCP_ENABLED=true
```

### Docker Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  kanvert:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

## Monitoring and Observability

### Health Checks

The application provides multiple health check endpoints:

- `/health` - Overall application health
- `/api/v1/convert/health` - Conversion services health
- `/api/v1/mcp/health` - MCP protocol health

### Logging

Structured JSON logging is available with configurable levels:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Request completed successfully",
  "method": "POST",
  "path": "/api/v1/convert/markdown-to-pdf",
  "status_code": 200,
  "duration_ms": 1250,
  "job_id": "pdf_20240115_103000_abc123"
}
```

### Metrics

Response headers include useful metrics:

- `X-Process-Time`: Request processing time
- `X-Job-ID`: Unique job identifier
- `X-Content-Size`: Output size in bytes
- `X-RateLimit-*`: Rate limiting information

## Security

### API Key Authentication

```bash
# Set API key in environment
export API_KEY=your-secure-api-key

# Use in requests
curl -H "X-API-Key: your-secure-api-key" \
  http://localhost:8000/api/v1/convert/formats
```

### Rate Limiting

Default rate limit: 100 requests per minute per IP address.

### Content Security

- Maximum request size: 10MB
- Maximum conversion content: 5MB
- Request timeout: 5 minutes
- Security headers included in all responses

## Extending Kanvert

### Adding New Converters

```python
from kanvert.core.base import BaseConverter, ConversionFormat

class CustomConverter(BaseConverter):
    def __init__(self):
        super().__init__(
            name="custom_converter",
            supported_formats=[ConversionFormat.HTML]
        )
    
    def validate_request(self, request):
        # Implement validation logic
        return True
    
    async def convert(self, request):
        # Implement conversion logic
        pass

# Register the converter
from kanvert.core.registry import converter_registry
converter_registry.register_converter(CustomConverter())
```

### Custom MCP Tools

```python
from kanvert.mcp.server import mcp_server

# Add custom tool to MCP server
custom_tool = MCPTool(
    name="custom_tool",
    description="Custom conversion tool",
    input_schema={
        "type": "object",
        "properties": {
            "input": {"type": "string"}
        }
    }
)

mcp_server.tools["custom_tool"] = custom_tool
```

## Support and Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd kanvert

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
pytest

# Run with hot reload
uvicorn kanvert.main:app --reload
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=kanvert

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests
```

### Code Quality

```bash
# Format code
black kanvert/
isort kanvert/

# Lint code
flake8 kanvert/
mypy kanvert/
```

## Troubleshooting

### Common Issues

1. **WeasyPrint Installation Issues**
   ```bash
   # Install system dependencies (Ubuntu/Debian)
   sudo apt-get install libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev
   
   # Install system dependencies (macOS)
   brew install cairo pango gdk-pixbuf libffi
   ```

2. **Large Document Timeouts**
   - Increase `CONVERSION_TIMEOUT` environment variable
   - Split large documents into smaller sections
   - Use simpler markdown without complex formatting

3. **Memory Issues**
   - Monitor memory usage with large documents
   - Consider horizontal scaling with multiple instances
   - Implement document size limits appropriate for your environment

4. **Font Issues in PDF**
   - Install additional fonts in Docker container
   - Use web-safe fonts in custom CSS
   - Verify font availability with WeasyPrint

### Support

For issues and questions:
- Check the health endpoints for service status
- Review application logs for detailed error information
- Ensure all dependencies are properly installed
- Verify environment configuration

## License

MIT License - see LICENSE file for details.