# Getting Started with Kanvert

Welcome to Kanvert! This guide will help you get up and running with the professional document conversion MCP server.

## What is Kanvert?

Kanvert is a professional, modular document conversion server that specializes in converting markdown to high-quality PDFs. It's built with FastAPI and designed to be:

- **Professional**: Enterprise-grade code quality and architecture
- **Modular**: Easily extensible for new conversion types
- **Robust**: Comprehensive error handling and logging
- **Scalable**: Docker-ready with production deployment support
- **AI-Ready**: Full MCP (Model Context Protocol) support for AI integration

## Quick Start

### Option 1: Using Docker (Recommended)

The fastest way to get Kanvert running is with Docker:

```bash
# Clone the repository
git clone <your-repo-url>
cd kanvert

# Start the server
docker-compose up --build

# The server will be available at http://localhost:8000
```

### Option 2: Local Development

If you prefer to run locally:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Start the development server
uvicorn kanvert.main:app --reload --host 0.0.0.0 --port 8000
```

## Your First Conversion

Let's convert some markdown to PDF!

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/convert/markdown-to-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Hello Kanvert!\n\nThis is my **first** PDF conversion.\n\n## Features\n- Professional formatting\n- Easy to use\n- Fast conversion",
    "output_format": "pdf",
    "options": {
      "title": "My First PDF"
    }
  }' \
  --output my-first-pdf.pdf

echo "PDF created: my-first-pdf.pdf"
```

### Using Python

```python
import requests

# Prepare your markdown content
markdown_content = """
# My First Kanvert Document

Welcome to **Kanvert**! This document demonstrates the basic features.

## What Can Kanvert Do?

- Convert markdown to professional PDFs
- Support for code syntax highlighting
- Mathematical equations: $E = mc^2$
- Tables, lists, and more!

## Code Example

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("Kanvert"))
```

## Conclusion

Document conversion has never been easier!
"""

# Convert to PDF
response = requests.post(
    "http://localhost:8000/api/v1/convert/markdown-to-pdf",
    json={
        "content": markdown_content,
        "output_format": "pdf",
        "options": {
            "title": "My First Document",
            "include_toc": True
        }
    }
)

if response.status_code == 200:
    with open("my-document.pdf", "wb") as f:
        f.write(response.content)
    print("✅ PDF created successfully!")
    print(f"📄 Job ID: {response.headers.get('X-Job-ID')}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

async function createPDF() {
    const markdown = `
# JavaScript + Kanvert

This PDF was created using **Node.js** and the Kanvert API.

## Benefits
- RESTful API
- JSON input/output
- Professional results

\`\`\`javascript
const kanvert = require('kanvert-client');
await kanvert.convertToPDF(markdown);
\`\`\`
`;

    try {
        const response = await axios.post(
            'http://localhost:8000/api/v1/convert/markdown-to-pdf',
            {
                content: markdown,
                output_format: 'pdf',
                options: {
                    title: 'JavaScript Example',
                    include_toc: true
                }
            },
            { responseType: 'arraybuffer' }
        );

        fs.writeFileSync('javascript-example.pdf', response.data);
        console.log('✅ PDF created: javascript-example.pdf');
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

createPDF();
```

## Exploring the API

### Check Server Health

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "app_name": "Kanvert",
  "app_version": "1.0.0",
  "environment": "development",
  "status": "healthy",
  "total_converters": 1,
  "healthy_converters": 1
}
```

### List Available Formats

```bash
curl http://localhost:8000/api/v1/convert/formats
```

### Get Converter Information

```bash
curl http://localhost:8000/api/v1/convert/converters
```

## Advanced Features

### Custom Styling with CSS

```python
import requests

markdown_with_custom_style = """
# Custom Styled Document

This document uses custom CSS for unique formatting.

## Highlighted Section
This section will have special styling.

### Code Block
```python
print("Custom styled code!")
```
"""

custom_css = """
body {
    font-family: 'Georgia', serif;
    color: #2c3e50;
}

h1 {
    color: #e74c3c;
    border-bottom: 3px solid #3498db;
    padding-bottom: 10px;
}

h2 {
    color: #27ae60;
    background-color: #ecf0f1;
    padding: 10px;
    border-left: 5px solid #27ae60;
}

code {
    background-color: #f39c12;
    color: white;
    padding: 2px 4px;
    border-radius: 3px;
}

pre {
    border: 2px dashed #9b59b6;
    background-color: #fdf2e9;
}
"""

response = requests.post(
    "http://localhost:8000/api/v1/convert/markdown-to-pdf",
    json={
        "content": markdown_with_custom_style,
        "output_format": "pdf",
        "options": {
            "title": "Custom Styled Document",
            "custom_css": custom_css
        }
    }
)

with open("custom-styled.pdf", "wb") as f:
    f.write(response.content)
```

### Mathematical Documents

```python
import requests

math_document = """
# Mathematical Document

## Basic Equations

Linear equation: $y = mx + b$

## Advanced Formulas

The quadratic formula:
$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

Einstein's mass-energy equivalence:
$$E = mc^2$$

## Statistical Formulas

Normal distribution:
$$f(x) = \\frac{1}{\\sqrt{2\\pi\\sigma^2}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}$$

## Matrix Notation

$$\\begin{bmatrix}
a & b \\\\
c & d
\\end{bmatrix}$$
"""

response = requests.post(
    "http://localhost:8000/api/v1/convert/markdown-to-pdf",
    json={
        "content": math_document,
        "output_format": "pdf",
        "options": {
            "title": "Mathematical Document",
            "include_toc": True
        }
    }
)

with open("math-document.pdf", "wb") as f:
    f.write(response.content)
```

## MCP Integration for AI

Kanvert supports the Model Context Protocol, making it perfect for AI integration:

### Get MCP Capabilities

```bash
curl http://localhost:8000/api/v1/mcp/capabilities
```

### Use MCP Tools

```python
import requests

# Call MCP tool for AI integration
mcp_request = {
    "method": "tools/call",
    "params": {
        "name": "convert_markdown_to_pdf",
        "arguments": {
            "content": "# AI Generated Report\n\nThis document was created by an AI using the MCP protocol.",
            "title": "AI Report",
            "include_toc": False
        }
    }
}

response = requests.post(
    "http://localhost:8000/api/v1/mcp/call",
    json=mcp_request
)

result = response.json()
if result.get("result", {}).get("success"):
    print("✅ AI conversion successful!")
    print(f"Job ID: {result['result']['job_id']}")
else:
    print("❌ AI conversion failed:", result.get("error"))
```

## Production Deployment

### Using Docker Compose

1. **Configure Environment**:
   ```bash
   # Copy and edit environment file
   cp .env.example .env
   
   # Edit for production
   vim .env
   ```

2. **Update docker-compose.yml**:
   ```yaml
   version: '3.8'
   services:
     kanvert:
       build: .
       ports:
         - "8000:8000"
       environment:
         - ENVIRONMENT=production
         - LOG_LEVEL=INFO
         - API_KEY=your-secure-api-key
       volumes:
         - ./logs:/app/logs
       restart: unless-stopped
   ```

3. **Deploy**:
   ```bash
   docker-compose up -d
   ```

### Environment Variables

Key production settings:

```bash
# Security
SECRET_KEY=your-super-secret-key-change-this
API_KEY=optional-api-key-for-authentication

# Performance
WORKERS=4
MAX_CONTENT_SIZE=10485760  # 10MB
CONVERSION_TIMEOUT=300     # 5 minutes

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/kanvert.log

# Features
MCP_ENABLED=true
CORS_ORIGINS=["https://yourdomain.com"]
```

## Best Practices

### Content Guidelines

1. **Optimize Images**: Use web-optimized images for faster processing
2. **Limit Size**: Keep documents under 5MB for best performance
3. **Simple Math**: Complex LaTeX may increase processing time
4. **Test Locally**: Always test complex documents locally first

### Error Handling

```python
import requests
from requests.exceptions import Timeout, HTTPError

def safe_convert(content, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/convert/markdown-to-pdf",
                json={"content": content, "output_format": "pdf"},
                timeout=30
            )
            response.raise_for_status()
            return response.content
            
        except Timeout:
            print(f"Attempt {attempt + 1}: Timeout, retrying...")
        except HTTPError as e:
            if e.response.status_code == 413:
                print("Content too large, reducing size...")
                # Implement content reduction logic
                break
            else:
                print(f"HTTP error {e.response.status_code}: {e.response.text}")
                break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    
    return None
```

### Performance Tips

1. **Batch Processing**: For multiple documents, consider queuing
2. **Caching**: Cache frequently converted templates
3. **Monitoring**: Use health endpoints to monitor performance
4. **Scaling**: Run multiple instances behind a load balancer

## Common Use Cases

### Technical Documentation

```python
# Generate API documentation
api_docs = """
# API Documentation

## Authentication
All endpoints require authentication via API key.

## Endpoints

### POST /api/users
Create a new user.

```json
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

### GET /api/users/{id}
Get user by ID.

Response:
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```
"""

# Convert with professional styling for technical docs
requests.post(url, json={
    "content": api_docs,
    "output_format": "pdf",
    "options": {
        "title": "API Documentation v1.0",
        "include_toc": True
    }
})
```

### Reports and Analytics

```python
# Generate business report
report = f"""
# Monthly Sales Report - {datetime.now().strftime('%B %Y')}

## Executive Summary
Total sales increased by **15%** compared to last month.

## Key Metrics
- Revenue: ${revenue:,.2f}
- Units Sold: {units:,}
- Customer Acquisition: {new_customers}

## Performance by Category
{generate_category_table()}

## Recommendations
Based on the data analysis, we recommend:
1. Increase marketing in high-performing categories
2. Optimize inventory for popular products
3. Expand customer retention programs
"""

# Convert to PDF for stakeholder distribution
```

### Educational Content

```python
# Create educational materials
lesson = """
# Introduction to Python Programming

## Learning Objectives
By the end of this lesson, you will:
- Understand Python syntax
- Write your first program
- Use variables and data types

## Getting Started

### Installation
1. Download Python from python.org
2. Install with default settings
3. Open terminal/command prompt

### Your First Program
```python
print("Hello, World!")
```

## Variables and Data Types

### Strings
```python
name = "Alice"
message = f"Hello, {name}!"
```

### Numbers
```python
age = 25
height = 5.6
```

## Exercise
Write a program that calculates the area of a circle.

```python
import math

radius = 5
area = math.pi * radius ** 2
print(f"Area: {area:.2f}")
```
"""
```

## Troubleshooting

### Common Issues

1. **"Module not found" errors**:
   ```bash
   pip install -r requirements.txt
   ```

2. **WeasyPrint installation issues**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libcairo2-dev libpango1.0-dev

   # macOS
   brew install cairo pango gdk-pixbuf libffi
   ```

3. **Docker build failures**:
   ```bash
   # Clean rebuild
   docker-compose down
   docker-compose build --no-cache
   docker-compose up
   ```

4. **PDF generation timeouts**:
   - Reduce document complexity
   - Increase timeout in configuration
   - Split large documents

### Getting Help

1. Check server health: `curl http://localhost:8000/health`
2. Review logs for detailed error messages
3. Test with simple markdown first
4. Verify all dependencies are installed

## Next Steps

Now that you're up and running with Kanvert:

1. **Explore Advanced Features**: Try custom CSS, math equations, and complex layouts
2. **Integrate with Your Applications**: Build Kanvert into your workflow
3. **Scale for Production**: Deploy with proper monitoring and security
4. **Extend Functionality**: Add new converters for additional formats
5. **AI Integration**: Use MCP protocol for AI-powered document generation

## Resources

- **API Documentation**: See `docs/API.md` for complete API reference
- **Architecture Guide**: Learn about the modular design
- **Contributing**: Help improve Kanvert with new features
- **Examples**: Check the `examples/` directory for more use cases

Happy converting! 🚀