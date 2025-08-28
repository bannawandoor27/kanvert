# Production-ready Dockerfile for Kanvert MCP Server
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Create non-root user
RUN groupadd --gid 1000 kanvert && \
    useradd --uid 1000 --gid kanvert --shell /bin/bash --create-home kanvert

# Install system dependencies for WeasyPrint and other tools
RUN apt-get update && apt-get install -y \
    # WeasyPrint dependencies
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    # Font support
    fonts-liberation \
    fonts-dejavu-core \
    fontconfig \
    # Build dependencies
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy pyproject.toml and uv.lock first (for better Docker layer caching)
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv
RUN uv sync --frozen

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/temp /app/logs && \
    chown -R kanvert:kanvert /app

# Switch to non-root user
USER kanvert

# Create environment file template
RUN echo "# Kanvert Configuration\n\
APP_NAME=Kanvert\n\
ENVIRONMENT=production\n\
HOST=0.0.0.0\n\
PORT=8000\n\
LOG_LEVEL=INFO\n\
LOG_FORMAT=json\n\
TEMP_DIR=/app/temp\n\
MAX_CONTENT_SIZE=5242880\n\
MCP_ENABLED=true" > .env.template

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Command to run the application
CMD ["uv", "run", "uvicorn", "kanvert.main:app", "--host", "0.0.0.0", "--port", "8000"]