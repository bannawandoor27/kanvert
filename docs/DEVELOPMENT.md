# Development Guide

## 🚀 Modern Python Development with uv

Kanvert uses `uv` for fast, reliable package management and dependency resolution. This guide covers the development workflow.

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) installed

### Installing uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

## 🏗️ Project Setup

### 1. Clone and Initialize

```bash
git clone https://github.com/bannawandoor27/kanvert.git
cd kanvert

# Create virtual environment and install dependencies
uv sync
```

### 2. Development Dependencies

The project includes development dependencies in `pyproject.toml`:

```bash
# Install with dev dependencies (default with uv sync)
uv sync

# Or install specific groups
uv sync --group dev
uv sync --group test
uv sync --group docs
```

## 🛠️ Development Workflow

### Running the Server

```bash
# Development server with auto-reload
uv run uvicorn kanvert.main:app --reload --host 0.0.0.0 --port 8000

# Or use the configured script
uv run kanvert
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=kanvert --cov-report=html

# Run specific test types
uv run pytest -m "not slow"  # Skip slow tests
uv run pytest -m integration  # Only integration tests
```

### Code Quality

```bash
# Format code
uv run black kanvert/
uv run isort kanvert/

# Lint code
uv run flake8 kanvert/
uv run mypy kanvert/

# Run all quality checks
uv run pre-commit run --all-files
```

### MCP Server Testing

```bash
# Test FastMCP integration
uv run python test_uv_fastmcp.py

# Run standalone MCP server
uv run python standalone_mcp_server.py
```

## 📦 Package Management

### Adding Dependencies

```bash
# Add production dependency
uv add fastapi

# Add development dependency
uv add --group dev pytest

# Add with version constraints
uv add "fastapi>=0.100.0"

# Add from git
uv add git+https://github.com/user/repo.git
```

### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add fastapi --upgrade

# Check for outdated packages
uv tree --outdated
```

### Removing Dependencies

```bash
# Remove a dependency
uv remove package-name

# Remove from specific group
uv remove --group dev package-name
```

## 🔧 Configuration

### pyproject.toml Structure

```toml
[project]
# Basic project metadata
dependencies = [...]  # Production dependencies

[project.optional-dependencies]
dev = [...]    # Development dependencies
test = [...]   # Testing dependencies
docs = [...]   # Documentation dependencies

[tool.uv]
dev-dependencies = [...]  # uv-specific dev dependencies

[tool.black]      # Black formatter config
[tool.isort]      # Import sorter config
[tool.mypy]       # Type checker config
[tool.pytest.ini_options]  # Test runner config
```

### Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit for your setup
vim .env
```

## 🐳 Docker Development

### Building with uv

```bash
# Build Docker image
docker-compose build

# Run with Docker
docker-compose up
```

### Multi-stage Dockerfile

The project uses a multi-stage Dockerfile that:
1. Uses uv for fast dependency installation
2. Creates optimized production image
3. Includes health checks

## 🧪 Testing Strategy

### Test Types

- **Unit Tests**: Core functionality (`test_core.py`)
- **Integration Tests**: API endpoints (`test_api.py`) 
- **Service Tests**: Document conversion (`test_markdown_pdf.py`)
- **MCP Tests**: FastMCP protocol (`test_uv_fastmcp.py`)

### Running Specific Tests

```bash
# Run unit tests only
uv run pytest kanvert/tests/test_core.py

# Run with specific markers
uv run pytest -m "unit"
uv run pytest -m "integration"
uv run pytest -m "not slow"

# Run with verbose output
uv run pytest -v

# Run with debugging
uv run pytest -s --pdb
```

### Coverage Reports

```bash
# Generate HTML coverage report
uv run pytest --cov=kanvert --cov-report=html

# View in browser
open htmlcov/index.html
```

## 🔍 Debugging

### Development Server

```bash
# Run with debug mode
uv run uvicorn kanvert.main:app --reload --log-level debug

# Run with profiling
uv run python -m cProfile -o profile.stats -m uvicorn kanvert.main:app
```

### FastMCP Debugging

```bash
# Test MCP server directly
uv run mcp dev standalone_mcp_server.py

# Test with MCP inspector
uv run mcp install standalone_mcp_server.py
```

## 🚀 Performance

### Dependency Resolution

uv provides significant performance improvements:
- **10-100x faster** dependency resolution
- **Parallel downloads** and installs
- **Lockfile generation** for reproducible builds
- **Cross-platform compatibility**

### Build Optimization

```bash
# Create optimized build
uv build

# Install from wheel
uv pip install dist/kanvert-*.whl
```

## 📚 Documentation

### Building Docs

```bash
# Install docs dependencies
uv sync --group docs

# Build documentation
uv run mkdocs build

# Serve locally
uv run mkdocs serve
```

### API Documentation

FastAPI automatically generates OpenAPI docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

### Pre-commit Setup

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files
```

### Code Style

- **Black**: Code formatting
- **isort**: Import sorting  
- **flake8**: Linting
- **mypy**: Type checking

### Pull Request Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test: `uv run pytest`
4. Format code: `uv run black . && uv run isort .`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push branch: `git push origin feature/amazing-feature`
7. Create Pull Request

## 🔧 Troubleshooting

### Common Issues

#### uv not found
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal
```

#### Dependencies not resolving
```bash
# Clear uv cache
uv cache clean

# Re-sync dependencies
uv sync --reinstall
```

#### WeasyPrint issues (macOS)
```bash
# Install system dependencies
brew install cairo pango gdk-pixbuf libffi
```

#### Permission errors
```bash
# Check Python installation
which python3
ls -la $(which python3)

# Use uv's managed Python
uv python install 3.11
uv run python --version
```

### Getting Help

- **uv docs**: https://docs.astral.sh/uv/
- **FastMCP docs**: https://github.com/modelcontextprotocol/python-sdk
- **FastAPI docs**: https://fastapi.tiangolo.com/
- **Project issues**: https://github.com/bannawandoor27/kanvert/issues

## 🌟 Benefits of uv

- ⚡ **Fast**: 10-100x faster than pip
- 🔒 **Reliable**: Lockfiles for reproducible installs
- 🧹 **Clean**: Better dependency resolution
- 🔧 **Modern**: Built for Python 3.7+
- 🐍 **Compatible**: Drop-in pip replacement
- 🌍 **Cross-platform**: Works everywhere

Happy coding! 🚀