#!/usr/bin/env python3
"""
Example script demonstrating basic Kanvert usage.

This script shows how to:
1. Convert simple markdown to PDF
2. Use custom options
3. Handle errors gracefully
4. Save results to files
"""

import requests
import json
import sys
from pathlib import Path


class KanvertClient:
    """Simple Kanvert client for document conversion."""
    
    def __init__(self, base_url="http://localhost:8000", api_key=None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def convert_markdown_to_pdf(self, content, output_file=None, **options):
        """Convert markdown content to PDF."""
        url = f"{self.base_url}/api/v1/convert/markdown-to-pdf"
        
        payload = {
            "content": content,
            "output_format": "pdf",
            "options": options
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            # Save to file if specified
            if output_file:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"✅ PDF saved to: {output_file}")
            
            return {
                "success": True,
                "data": response.content,
                "job_id": response.headers.get("X-Job-ID"),
                "content_size": len(response.content)
            }
            
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out"}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def health_check(self):
        """Check server health."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_supported_formats(self):
        """Get supported conversion formats."""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/convert/formats", timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def main():
    """Main example function."""
    print("🔄 Kanvert Example Script")
    print("=" * 40)
    
    # Initialize client
    client = KanvertClient()
    
    # Check server health
    print("\n📊 Checking server health...")
    health = client.health_check()
    if health.get("status") == "healthy":
        print("✅ Server is healthy")
    else:
        print("❌ Server health check failed:", health)
        return
    
    # Example 1: Simple conversion
    print("\n📝 Example 1: Simple Markdown to PDF")
    simple_markdown = """
# Welcome to Kanvert!

This is a **simple example** of markdown to PDF conversion.

## Features
- Professional formatting
- Easy to use API
- Fast conversion

## Code Example
```python
print("Hello, Kanvert!")
```

Thank you for using Kanvert! 🚀
"""
    
    result = client.convert_markdown_to_pdf(
        content=simple_markdown,
        output_file="simple_example.pdf",
        title="Simple Example",
        include_toc=False
    )
    
    if result["success"]:
        print(f"✅ Simple conversion successful!")
        print(f"   Job ID: {result['job_id']}")
        print(f"   File size: {result['content_size']:,} bytes")
    else:
        print(f"❌ Simple conversion failed: {result['error']}")
    
    # Example 2: Advanced features
    print("\n📚 Example 2: Advanced Features")
    advanced_markdown = """
# Advanced Kanvert Document

## Table of Contents
This document demonstrates advanced Kanvert features.

## Mathematical Equations

### Inline Math
The quadratic formula is $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$.

### Block Math
Einstein's mass-energy equivalence:

$$E = mc^2$$

## Code Blocks with Syntax Highlighting

### Python
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Generate first 10 numbers
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### JavaScript
```javascript
const apiCall = async (url) => {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API call failed:', error);
    }
};
```

## Tables

| Feature | Status | Priority |
|---------|--------|----------|
| PDF Generation | ✅ Complete | High |
| Math Support | ✅ Complete | High |
| Custom CSS | ✅ Complete | Medium |
| DOCX Export | 🔄 Planned | Low |

## Task Lists

- [x] Implement basic conversion
- [x] Add math support
- [x] Create examples
- [ ] Add more output formats
- [ ] Build web interface

## Blockquotes

> "The best way to predict the future is to invent it." 
> 
> — Alan Kay

## Links and Images

Visit [Kanvert Documentation](https://example.com/kanvert-docs) for more information.

---

**Generated with Kanvert** - Professional Document Conversion
"""

    custom_css = """
    body {
        font-family: 'Georgia', serif;
        line-height: 1.8;
        color: #2c3e50;
    }
    
    h1 {
        color: #e74c3c;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }
    
    h2 {
        color: #27ae60;
        margin-top: 2em;
    }
    
    blockquote {
        border-left: 4px solid #f39c12;
        background-color: #fdf6e3;
        padding: 1em;
        font-style: italic;
    }
    
    .math {
        background-color: #ecf0f1;
        padding: 1em;
        border-radius: 5px;
        text-align: center;
    }
    
    table {
        border-collapse: collapse;
        margin: 1em 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    th {
        background-color: #34495e;
        color: white;
    }
    
    code {
        background-color: #e8f4fd;
        color: #2c3e50;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
    }
    """
    
    result = client.convert_markdown_to_pdf(
        content=advanced_markdown,
        output_file="advanced_example.pdf",
        title="Advanced Kanvert Features",
        include_toc=True,
        custom_css=custom_css
    )
    
    if result["success"]:
        print(f"✅ Advanced conversion successful!")
        print(f"   Job ID: {result['job_id']}")
        print(f"   File size: {result['content_size']:,} bytes")
    else:
        print(f"❌ Advanced conversion failed: {result['error']}")
    
    # Example 3: Report generation
    print("\n📊 Example 3: Business Report")
    
    import datetime
    current_date = datetime.datetime.now()
    
    report_content = f"""
# Monthly Business Report
**Period:** {current_date.strftime('%B %Y')}  
**Generated:** {current_date.strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This month showed strong performance across all key metrics:

- **Revenue Growth:** +15.3% compared to last month
- **Customer Acquisition:** 234 new customers
- **Retention Rate:** 94.7%
- **Customer Satisfaction:** 4.6/5.0

## Key Performance Indicators

### Sales Metrics

| Metric | Current Month | Last Month | Change |
|--------|---------------|------------|--------|
| Revenue | $125,430 | $108,650 | +15.3% |
| Orders | 1,247 | 1,089 | +14.5% |
| Avg Order Value | $100.58 | $99.77 | +0.8% |
| Conversion Rate | 3.2% | 2.9% | +0.3% |

### Customer Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| New Customers | 234 | 200 | ✅ Above |
| Churn Rate | 5.3% | 6.0% | ✅ Below |
| Lifetime Value | $1,247 | $1,200 | ✅ Above |
| Support Tickets | 89 | 100 | ✅ Below |

## Regional Performance

### North America
- Revenue: $78,250 (62.4% of total)
- Growth: +12.7%
- Top products: Enterprise, Professional

### Europe
- Revenue: $31,290 (24.9% of total)
- Growth: +18.2%
- Top products: Standard, Professional

### Asia-Pacific
- Revenue: $15,890 (12.7% of total)
- Growth: +22.1%
- Top products: Basic, Standard

## Product Analysis

```python
# Top performing products (units sold)
products = {{
    'Enterprise': 145,
    'Professional': 289,
    'Standard': 421,
    'Basic': 392
}}

for product, units in products.items():
    revenue = units * product_prices[product]
    print(f"{{product}}: {{units}} units, ${{revenue:,.2f}}")
```

## Action Items

1. **Marketing**: Increase budget for Asia-Pacific region (+22% growth)
2. **Product**: Develop new features for Enterprise tier
3. **Support**: Maintain current support quality (satisfaction 4.6/5)
4. **Sales**: Focus on Professional tier (highest growth potential)

## Financial Forecast

Based on current trends, we project:

### Q4 Estimates
- **Revenue:** $385,000 - $420,000
- **Growth Rate:** 12-18% month-over-month
- **New Customers:** 650-750

### Risk Factors
- Seasonal variations in Q4
- Increased competition
- Economic uncertainty

### Opportunities
- Holiday season promotions
- Partnership expansion
- Product line extension

## Conclusion

Strong performance this month positions us well for Q4 targets. Key focus areas:

> Continue momentum in Asia-Pacific, optimize Enterprise offerings, and maintain excellent customer satisfaction.

---

**Report prepared by:** Business Intelligence Team  
**Next review:** {(current_date + datetime.timedelta(days=30)).strftime('%Y-%m-%d')}
"""
    
    result = client.convert_markdown_to_pdf(
        content=report_content,
        output_file="business_report.pdf",
        title="Monthly Business Report",
        include_toc=True
    )
    
    if result["success"]:
        print(f"✅ Report generation successful!")
        print(f"   Job ID: {result['job_id']}")
        print(f"   File size: {result['content_size']:,} bytes")
    else:
        print(f"❌ Report generation failed: {result['error']}")
    
    # Show supported formats
    print("\n🔧 Supported Formats:")
    formats = client.get_supported_formats()
    if "supported_formats" in formats:
        for fmt in formats["supported_formats"]:
            print(f"   • {fmt}")
    
    print("\n🎉 Examples completed!")
    print("\nGenerated files:")
    for filename in ["simple_example.pdf", "advanced_example.pdf", "business_report.pdf"]:
        if Path(filename).exists():
            size = Path(filename).stat().st_size
            print(f"   📄 {filename} ({size:,} bytes)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Script failed: {e}")
        sys.exit(1)