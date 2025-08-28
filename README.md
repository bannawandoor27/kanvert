# Kanvert - Professional Document Conversion MCP Server

A professional, modular MCP (Model Context Protocol) server built with FastAPI for document conversion services. Currently supports markdown to PDF conversion with an extensible architecture for additional conversion APIs.

## Features

- 🚀 **Professional Architecture**: Modular, extensible design following SOLID principles
- 📄 **Markdown to PDF**: High-quality PDF generation from markdown with custom styling
- 🔌 **MCP Protocol**: Full Model Context Protocol support for AI integration
- 🛡️ **Robust Error Handling**: Comprehensive error handling and logging
- 🐳 **Docker Ready**: Production-ready Docker deployment
- 📊 **Monitoring**: Built-in health checks and metrics
- 🧪 **Well Tested**: Comprehensive test suite with high coverage
- 🔧 **Configurable**: Environment-based configuration management

## Quick Start

### Using Docker (Recommended)

```bash
# Build and run
docker-compose up --build

# The server will be available at http://localhost:8000
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn kanvert.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
- `GET /health` - Server health status

### Document Conversion
- `POST /api/v1/convert/markdown-to-pdf` - Convert markdown to PDF

### MCP Integration
- `POST /mcp/call` - MCP protocol endpoint
- `GET /mcp/capabilities` - List available MCP tools

## Architecture

The project follows a clean, modular architecture:

```
kanvert/
├── core/           # Core business logic and interfaces
├── services/       # Conversion service implementations  
├── api/           # FastAPI routes and middleware
├── mcp/           # MCP protocol implementation
├── config/        # Configuration management
├── utils/         # Utility functions and helpers
└── tests/         # Comprehensive test suite
```

## Adding New Conversion Services

The architecture is designed for easy extension. To add a new conversion service:

1. Create a new service class inheriting from `BaseConverter`
2. Implement the required conversion methods
3. Register the service in the router
4. Add MCP tool definitions

## Contributing

1. Follow the existing code style (Black, isort, flake8)
2. Add tests for new features
3. Update documentation
4. Submit a pull request

## License

MIT License - see LICENSE file for details.