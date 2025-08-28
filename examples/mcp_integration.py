#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Integration Example

This script demonstrates how to use Kanvert's MCP protocol support
for AI-powered document generation and conversion.
"""

import requests
import json
import sys
from datetime import datetime


class KanvertMCPClient:
    """MCP client for Kanvert integration."""
    
    def __init__(self, base_url="http://localhost:8000", api_key=None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def get_mcp_capabilities(self):
        """Get MCP server capabilities."""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/mcp/capabilities")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_mcp_tools(self):
        """List available MCP tools."""
        return self.mcp_call("tools/list", {})
    
    def mcp_call(self, method, params):
        """Make an MCP protocol call."""
        try:
            payload = {
                "method": method,
                "params": params
            }
            response = self.session.post(f"{self.base_url}/api/v1/mcp/call", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def convert_markdown_via_mcp(self, content, **options):
        """Convert markdown to PDF using MCP protocol."""
        return self.mcp_call("tools/call", {
            "name": "convert_markdown_to_pdf",
            "arguments": {
                "content": content,
                **options
            }
        })
    
    def list_formats_via_mcp(self):
        """List supported formats using MCP protocol."""
        return self.mcp_call("tools/call", {
            "name": "list_supported_formats",
            "arguments": {}
        })


def demonstrate_mcp_basics():
    """Demonstrate basic MCP functionality."""
    print("🔧 MCP Protocol Demonstration")
    print("=" * 50)
    
    client = KanvertMCPClient()
    
    # Get capabilities
    print("\n📋 MCP Server Capabilities:")
    capabilities = client.get_mcp_capabilities()
    if "error" in capabilities:
        print(f"❌ Error getting capabilities: {capabilities['error']}")
        return
    
    print(f"   Server: {capabilities['server']['name']} v{capabilities['server']['version']}")
    print(f"   Tools available: {len(capabilities['tools'])}")
    
    # List tools
    print("\n🛠️  Available MCP Tools:")
    tools_response = client.list_mcp_tools()
    if "error" in tools_response:
        print(f"❌ Error listing tools: {tools_response['error']}")
        return
    
    tools = tools_response.get("result", {}).get("tools", [])
    for tool in tools:
        print(f"   • {tool['name']}: {tool['description']}")
    
    return client


def ai_document_generation_example(client):
    """Example of AI-powered document generation using MCP."""
    print("\n🤖 AI Document Generation Example")
    print("-" * 50)
    
    # Simulate AI-generated content (in real usage, this would come from an AI model)
    ai_generated_content = f"""
# AI-Generated Technical Report
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Topic:** Advanced Document Processing Systems

## Executive Summary

This report analyzes the current state of document processing technologies and their impact on modern business workflows. Our analysis reveals significant opportunities for automation and efficiency improvements.

## Key Findings

### 1. Current Market Landscape

The document processing market has evolved rapidly:

- **Traditional Methods:** Manual processing, prone to errors
- **Modern Solutions:** AI-powered automation, 85% accuracy improvement
- **Future Trends:** Real-time processing, multi-format support

### 2. Technology Stack Analysis

```python
# Modern document processing pipeline
class DocumentProcessor:
    def __init__(self):
        self.converters = {{
            'markdown': MarkdownConverter(),
            'html': HTMLConverter(), 
            'docx': DocxConverter()
        }}
    
    async def process(self, content, output_format):
        converter = self.converters.get(content.type)
        return await converter.convert(content, output_format)
```

### 3. Performance Metrics

| Metric | Traditional | AI-Enhanced | Improvement |
|--------|-------------|-------------|-------------|
| Processing Speed | 5 min/doc | 30 sec/doc | 90% faster |
| Accuracy Rate | 73% | 96% | +23% |
| Cost per Document | $2.50 | $0.15 | 94% reduction |
| User Satisfaction | 6.2/10 | 9.1/10 | +47% |

## Technical Implementation

### Architecture Overview

Our system implements a microservices architecture:

1. **Input Layer:** Multiple format support
2. **Processing Engine:** AI-powered conversion
3. **Output Layer:** Professional formatting
4. **API Gateway:** RESTful and MCP protocol support

### Mathematical Models

The conversion quality is optimized using:

$$Q = \\frac{\\sum_{i=1}^{n} w_i \\cdot f_i(x)}{\\sum_{i=1}^{n} w_i}$$

Where:
- $Q$ = Overall quality score
- $w_i$ = Weight for feature $i$
- $f_i(x)$ = Feature extraction function

## Recommendations

### Short-term (0-6 months)
1. Implement automated quality checks
2. Expand format support to include presentations
3. Develop real-time collaboration features

### Medium-term (6-18 months)
1. Machine learning model optimization
2. Cloud-native deployment
3. Advanced analytics dashboard

### Long-term (18+ months)
1. AI-powered content generation
2. Multi-language support
3. Integration with enterprise systems

## Risk Assessment

### Technical Risks
- **Data Security:** Implement end-to-end encryption
- **Scalability:** Design for horizontal scaling
- **Reliability:** 99.9% uptime target

### Business Risks
- **Market Competition:** Continuous innovation required
- **Technology Changes:** Adaptive architecture needed
- **User Adoption:** Comprehensive training programs

## Conclusion

The integration of AI technologies in document processing represents a paradigm shift. Organizations that adopt these technologies early will gain significant competitive advantages.

> "The future belongs to organizations that can transform information into insight, and insight into action."

## Next Steps

1. **Pilot Program:** Start with 50 documents/day
2. **Measurement:** Track key performance indicators
3. **Scaling:** Gradual rollout to full organization
4. **Optimization:** Continuous improvement based on feedback

---

**Report Classification:** Internal Use  
**Generated by:** AI Document Intelligence System  
**Review Date:** {(datetime.now()).strftime('%Y-%m-%d')}
"""
    
    print("📄 Converting AI-generated content via MCP...")
    
    result = client.convert_markdown_via_mcp(
        content=ai_generated_content,
        title="AI-Generated Technical Report",
        include_toc=True
    )
    
    if result.get("error"):
        print(f"❌ MCP conversion failed: {result['error']}")
        return
    
    mcp_result = result.get("result", {})
    if mcp_result.get("success"):
        print("✅ AI document conversion successful!")
        print(f"   Job ID: {mcp_result['job_id']}")
        print(f"   Filename: {mcp_result['filename']}")
        print(f"   Size: {mcp_result['size_bytes']:,} bytes")
        print(f"   Message: {mcp_result['message']}")
    else:
        print(f"❌ AI conversion failed: {mcp_result.get('error', 'Unknown error')}")


def automated_report_generation(client):
    """Example of automated report generation using MCP."""
    print("\n📊 Automated Report Generation")
    print("-" * 50)
    
    # Simulate data from various sources (databases, APIs, etc.)
    data = {
        "sales": {"revenue": 125430, "orders": 1247, "growth": 15.3},
        "customers": {"new": 234, "churn_rate": 5.3, "satisfaction": 4.6},
        "products": {"enterprise": 145, "professional": 289, "standard": 421}
    }
    
    # Generate report content dynamically
    report_content = f"""
# Automated Weekly Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Period:** Week {datetime.now().isocalendar()[1]}, {datetime.now().year}

## Performance Summary

This week's performance shows strong momentum across all key areas:

### Financial Performance
- **Revenue:** ${data['sales']['revenue']:,} (+{data['sales']['growth']}%)
- **Orders:** {data['sales']['orders']:,}
- **Average Order Value:** ${data['sales']['revenue']/data['sales']['orders']:.2f}

### Customer Metrics
- **New Customers:** {data['customers']['new']}
- **Churn Rate:** {data['customers']['churn_rate']}%
- **Satisfaction Score:** {data['customers']['satisfaction']}/5.0

## Product Performance

| Product | Units Sold | Revenue Share |
|---------|------------|---------------|
| Enterprise | {data['products']['enterprise']} | {data['products']['enterprise']/sum(data['products'].values())*100:.1f}% |
| Professional | {data['products']['professional']} | {data['products']['professional']/sum(data['products'].values())*100:.1f}% |
| Standard | {data['products']['standard']} | {data['products']['standard']/sum(data['products'].values())*100:.1f}% |

## Trends Analysis

```python
# Weekly growth calculation
def calculate_growth(current, previous):
    return ((current - previous) / previous) * 100

weekly_growth = calculate_growth(
    current_revenue={data['sales']['revenue']},
    previous_revenue={data['sales']['revenue'] * 0.85:.0f}
)
print(f"Growth rate: {{weekly_growth:.1f}}%")
```

## Key Actions for Next Week

1. **Sales Team:** Focus on enterprise customers
2. **Marketing:** Increase professional tier promotion
3. **Support:** Maintain satisfaction above 4.5/5
4. **Product:** Analyze standard tier feedback

## Automated Insights

Based on data analysis:

> Revenue growth of +{data['sales']['growth']}% indicates strong market demand. Continue current strategies while monitoring customer satisfaction metrics.

---

*This report was automatically generated using AI and MCP protocols.*
"""
    
    print("🔄 Generating automated report via MCP...")
    
    result = client.convert_markdown_via_mcp(
        content=report_content,
        title=f"Weekly Report - Week {datetime.now().isocalendar()[1]}",
        include_toc=False
    )
    
    if result.get("error"):
        print(f"❌ Automated report generation failed: {result['error']}")
        return
    
    mcp_result = result.get("result", {})
    if mcp_result.get("success"):
        print("✅ Automated report generation successful!")
        print(f"   Job ID: {mcp_result['job_id']}")
        print(f"   Report saved: {mcp_result['filename']}")
    else:
        print(f"❌ Report generation failed: {mcp_result.get('error', 'Unknown error')}")


def mcp_format_discovery(client):
    """Demonstrate format discovery via MCP."""
    print("\n🔍 Format Discovery via MCP")
    print("-" * 50)
    
    result = client.list_formats_via_mcp()
    
    if result.get("error"):
        print(f"❌ Format discovery failed: {result['error']}")
        return
    
    mcp_result = result.get("result", {})
    
    print("📋 Available Conversion Formats:")
    for fmt in mcp_result.get("supported_formats", []):
        print(f"   • {fmt}")
    
    print(f"\n🔧 Total Converters: {mcp_result.get('total_converters', 0)}")
    
    print("\n📖 Converter Details:")
    for converter in mcp_result.get("converters", []):
        print(f"   • {converter['name']}")
        print(f"     Formats: {', '.join(converter.get('supported_formats', []))}")
        print(f"     Description: {converter.get('description', 'N/A')}")


def main():
    """Main demonstration function."""
    print("🚀 Kanvert MCP Integration Examples")
    print("=" * 60)
    
    try:
        # Basic MCP demonstration
        client = demonstrate_mcp_basics()
        if not client:
            return
        
        # AI document generation
        ai_document_generation_example(client)
        
        # Automated reporting
        automated_report_generation(client)
        
        # Format discovery
        mcp_format_discovery(client)
        
        print("\n🎉 MCP Integration Examples Completed!")
        print("\nMCP Protocol Benefits:")
        print("   • Standardized AI tool integration")
        print("   • Type-safe tool definitions")
        print("   • Automatic capability discovery")
        print("   • Error handling and validation")
        print("   • Perfect for AI agent workflows")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()