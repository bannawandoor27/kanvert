"""
Test configuration and base test classes.
"""

import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from typing import AsyncGenerator, Generator
import tempfile
import shutil
from pathlib import Path

from kanvert.main import create_app
from kanvert.config.settings import Settings
from kanvert.core.registry import converter_registry


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        environment="testing",
        debug=True,
        log_level="DEBUG",
        temp_dir=tempfile.mkdtemp(),
        max_content_size=1024 * 1024,  # 1MB for tests
        conversion_timeout=30,
        mcp_enabled=True,
        rate_limit_requests=1000  # High limit for tests
    )


@pytest.fixture
def app(test_settings):
    """Create FastAPI test application."""
    # Override settings
    from kanvert.config.settings import settings
    for key, value in test_settings.dict().items():
        setattr(settings, key, value)
    
    app = create_app()
    return app


@pytest.fixture
def client(app) -> Generator[TestClient, None, None]:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_markdown() -> str:
    """Sample markdown content for testing."""
    return """# Test Document

This is a **test document** with various markdown features.

## Code Block

```python
def hello_world():
    print("Hello, World!")
```

## List

- Item 1
- Item 2
- Item 3

## Table

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |

## Math

The formula is: $E = mc^2$

## Blockquote

> This is a blockquote with some important information.

## Link

[FastAPI Documentation](https://fastapi.tiangolo.com/)
"""


@pytest.fixture
def complex_markdown() -> str:
    """Complex markdown for advanced testing."""
    return """# Advanced Document

## Table of Contents
- [Section 1](#section-1)
- [Section 2](#section-2)
- [Code Examples](#code-examples)

## Section 1

This section contains **bold text**, *italic text*, and `inline code`.

### Subsection 1.1

Here's a task list:

- [x] Completed task
- [ ] Pending task
- [ ] Another pending task

## Section 2

### Mathematical Expressions

Inline math: $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$

Block math:

$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

## Code Examples

### Python

```python
import asyncio
from typing import List

async def process_data(data: List[str]) -> List[str]:
    \"\"\"Process a list of strings asynchronously.\"\"\"
    results = []
    for item in data:
        result = await some_async_operation(item)
        results.append(result)
    return results
```

### JavaScript

```javascript
const fetchData = async (url) => {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
};
```

## Advanced Table

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| Markdown to PDF | ✅ Complete | High | Working well |
| HTML to PDF | 🔄 In Progress | Medium | Next version |
| DOCX Support | 📋 Planned | Low | Future release |

## Footnotes

Here's a sentence with a footnote[^1].

[^1]: This is the footnote content.

---

**End of document**
"""


@pytest.fixture(autouse=True)
def cleanup_registry():
    """Ensure registry is clean between tests."""
    # Clear registry before test
    converter_registry._converters.clear()
    converter_registry._format_mapping.clear()
    
    yield
    
    # Clean up after test if needed
    pass


class TestBase:
    """Base test class with common utilities."""
    
    def assert_pdf_content(self, pdf_data: bytes) -> None:
        """Assert that the data is valid PDF content."""
        assert pdf_data is not None
        assert len(pdf_data) > 0
        assert pdf_data.startswith(b'%PDF-')
        assert b'%%EOF' in pdf_data
    
    def assert_successful_response(self, response, expected_status: int = 200) -> None:
        """Assert that the response is successful."""
        assert response.status_code == expected_status
        if hasattr(response, 'json'):
            data = response.json()
            if 'error' in data:
                pytest.fail(f"Response contains error: {data['error']}")
    
    def create_conversion_request(self, content: str, **options) -> dict:
        """Create a standard conversion request."""
        return {
            "content": content,
            "output_format": "pdf",
            "options": options
        }