# Kanvert - Professional Document Conversion MCP Server

## 🎯 Project Overview

**Kanvert** is a professional, production-ready MCP (Model Context Protocol) server built with FastAPI that specializes in document conversion, starting with high-quality markdown to PDF conversion. It's designed to be modular, extensible, and perfect for AI integration.

## ✨ Key Features

- **🏗️ Professional Architecture**: Clean, modular design following SOLID principles
- **📄 High-Quality PDF Generation**: Professional typography with WeasyPrint
- **🤖 AI-Ready**: Full MCP protocol support for seamless AI integration
- **🚀 Production-Ready**: Docker deployment, comprehensive logging, health checks
- **🔧 Extensible**: Easy to add new conversion formats and services
- **🛡️ Secure**: Rate limiting, API keys, security headers
- **📊 Observable**: Structured logging, metrics, health monitoring
- **🧪 Well-Tested**: Comprehensive test suite with high coverage

## 📁 Project Structure

```
kanvert/
├── 📚 docs/                    # Documentation
│   ├── API.md                  # Complete API reference
│   └── GETTING_STARTED.md      # User guide
├── 🐳 docker-compose.yml       # Docker deployment
├── 🐳 Dockerfile              # Container configuration
├── 📋 requirements.txt         # Python dependencies
├── ⚙️ .env.example            # Environment template
├── 🧪 pytest.ini             # Test configuration
├── 📖 README.md               # Project overview
├── 🎯 examples/               # Usage examples
│   ├── basic_usage.py         # Basic conversion examples
│   └── mcp_integration.py     # MCP protocol examples
└── 📦 kanvert/               # Main package
    ├── 🏗️ core/              # Core business logic
    │   ├── base.py           # Base classes and interfaces
    │   └── registry.py       # Converter registry
    ├── 🔧 services/          # Conversion implementations
    │   └── markdown_pdf.py   # Markdown to PDF converter
    ├── 🌐 api/               # FastAPI application
    │   ├── routes.py         # API endpoints
    │   └── middleware.py     # Security, logging, etc.
    ├── 🤖 mcp/               # MCP protocol support
    │   ├── server.py         # MCP server implementation
    │   └── routes.py         # MCP API endpoints
    ├── ⚙️ config/            # Configuration management
    │   └── settings.py       # Environment-based config
    ├── 🛠️ utils/             # Utility functions
    │   └── logging_config.py # Structured logging
    ├── 🧪 tests/             # Comprehensive test suite
    │   ├── conftest.py       # Test configuration
    │   ├── test_core.py      # Core functionality tests
    │   ├── test_markdown_pdf.py # Converter tests
    │   └── test_api.py       # API integration tests
    └── main.py               # FastAPI application entry
```

## 🚀 Quick Start

### 1. Docker Deployment (Recommended)

```bash
# Clone and start
git clone <repository-url>
cd kanvert
docker-compose up --build

# Server available at http://localhost:8000
```

### 2. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Start server
uvicorn kanvert.main:app --reload
```

### 3. First Conversion

```bash
# Convert markdown to PDF
curl -X POST "http://localhost:8000/api/v1/convert/markdown-to-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Hello Kanvert!\n\nThis is **professional** PDF generation.",
    "output_format": "pdf",
    "options": {"title": "My First PDF"}
  }' \
  --output hello.pdf
```

## 🏗️ Architecture Highlights

### Core Design Principles

1. **Separation of Concerns**: Clear boundaries between conversion, API, and MCP layers
2. **Dependency Injection**: Configurable components for testing and flexibility
3. **Error Handling**: Comprehensive error handling with structured logging
4. **Extensibility**: Plugin-like architecture for new converters
5. **Observability**: Health checks, metrics, and monitoring built-in

### Key Components

- **`BaseConverter`**: Abstract base for all conversion services
- **`ConverterRegistry`**: Central registry for discovering and managing converters
- **`MarkdownToPdfConverter`**: High-quality PDF generation with WeasyPrint
- **`MCPServer`**: Full Model Context Protocol implementation
- **Middleware Stack**: Security, rate limiting, logging, CORS

## 📊 API Endpoints

### Document Conversion
- `POST /api/v1/convert/markdown-to-pdf` - Markdown to PDF conversion
- `POST /api/v1/convert/` - Generic conversion endpoint
- `GET /api/v1/convert/formats` - List supported formats
- `GET /api/v1/convert/health` - Conversion service health

### MCP Protocol
- `GET /api/v1/mcp/capabilities` - MCP server capabilities
- `POST /api/v1/mcp/call` - Execute MCP tools
- `GET /api/v1/mcp/tools` - List available tools

### Monitoring
- `GET /health` - Overall application health
- `GET /` - API information and documentation links

## 🤖 MCP Integration

Perfect for AI applications:

```python
# AI can use Kanvert through MCP protocol
mcp_request = {
    "method": "tools/call",
    "params": {
        "name": "convert_markdown_to_pdf",
        "arguments": {
            "content": "# AI-Generated Report\n\nContent here...",
            "title": "AI Report"
        }
    }
}
```

## 🔧 Extensibility

### Adding New Converters

```python
from kanvert.core.base import BaseConverter, ConversionFormat

class HTMLToPdfConverter(BaseConverter):
    def __init__(self):
        super().__init__(
            name="html_to_pdf",
            supported_formats=[ConversionFormat.PDF]
        )
    
    async def convert(self, request):
        # Implementation here
        pass

# Register with the system
from kanvert.core.registry import converter_registry
converter_registry.register_converter(HTMLToPdfConverter())
```

### Environment Configuration

```bash
# Core settings
APP_NAME=Kanvert
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key
API_KEY=optional-api-key

# Conversion limits
MAX_CONTENT_SIZE=5242880  # 5MB
CONVERSION_TIMEOUT=300    # 5 minutes

# Features
MCP_ENABLED=true
LOG_LEVEL=INFO
```

## 🧪 Testing

Comprehensive test suite with high coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=kanvert --cov-report=html

# Run specific test types
pytest -m "not slow"        # Skip slow tests
pytest -m integration       # Integration tests only
pytest kanvert/tests/test_core.py  # Specific module
```

## 🚀 Production Deployment

### Docker Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  kanvert:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - API_KEY=${API_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Scaling Considerations

- **Horizontal Scaling**: Run multiple instances behind load balancer
- **Resource Management**: Monitor memory usage for large documents
- **Caching**: Implement Redis for request caching and rate limiting
- **Monitoring**: Use health endpoints for load balancer checks

## 📈 Performance

### Benchmarks

- **Simple Documents**: ~500ms conversion time
- **Complex Documents**: ~2-5s depending on content
- **Memory Usage**: ~50-200MB per conversion
- **Concurrent Requests**: Handles 10+ simultaneous conversions

### Optimization Tips

1. **Content Size**: Keep documents under 5MB for best performance
2. **Image Optimization**: Use web-optimized images
3. **CSS Complexity**: Simple styles convert faster
4. **Math Equations**: Limit complex LaTeX for speed

## 🛡️ Security Features

- **Rate Limiting**: 100 requests/minute per IP (configurable)
- **API Key Authentication**: Optional API key protection
- **Security Headers**: HSTS, CSP, XSS protection
- **Input Validation**: Comprehensive request validation
- **Content Size Limits**: Prevent resource exhaustion

## 📝 Logging and Monitoring

### Structured Logging

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Conversion completed",
  "job_id": "pdf_20240115_103000_abc123",
  "duration_ms": 1250,
  "content_size": 2048
}
```

### Health Monitoring

- **Application Health**: `/health` endpoint
- **Service Health**: Component-level health checks
- **Metrics**: Response times, error rates, conversion stats

## 🌟 Use Cases

### 1. Documentation Generation
- API documentation from markdown
- Technical specifications
- User manuals and guides

### 2. Report Generation
- Business reports with charts
- Analytics dashboards
- Automated reporting pipelines

### 3. AI Integration
- AI-generated document conversion
- Content processing workflows
- Automated document creation

### 4. Content Publishing
- Blog posts to PDF
- Educational materials
- Marketing collateral

## 🤝 Contributing

### Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd kanvert
pip install -r requirements.txt
pip install -e .

# Run tests
pytest

# Code quality
black kanvert/
isort kanvert/
flake8 kanvert/
mypy kanvert/
```

### Adding Features

1. **New Converters**: Follow the `BaseConverter` interface
2. **API Endpoints**: Add to appropriate router modules
3. **MCP Tools**: Register with the MCP server
4. **Tests**: Maintain high test coverage
5. **Documentation**: Update API docs and examples

## 📞 Support

### Troubleshooting

1. **Check Health**: `curl http://localhost:8000/health`
2. **Review Logs**: Structured JSON logs available
3. **Test Simple**: Start with basic markdown
4. **Verify Dependencies**: Ensure WeasyPrint system deps installed

### Common Issues

- **WeasyPrint Dependencies**: Install system packages for Cairo/Pango
- **Large Documents**: Increase timeout or split content
- **Memory Usage**: Monitor resource consumption
- **Font Issues**: Ensure fonts available in container

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for professional document conversion**

Kanvert represents a modern approach to document conversion:
- Clean, maintainable architecture
- Production-ready deployment
- AI-first design with MCP protocol
- Comprehensive testing and documentation
- Extensible for future requirements

Perfect for teams needing reliable, high-quality document conversion with AI integration capabilities.