import React, { useState } from 'react';
import {
  Copy,
  Check,
  Book,
  Code,
  Globe,
  FileText,
  Zap,
  Shield,
  Clock,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, Button } from '../common';

interface ApiEndpoint {
  id: string;
  method: string;
  path: string;
  title: string;
  description: string;
  requestBody: {
    contentType: string;
    schema: string;
    example: string;
  };
  responses: Array<{
    status: number;
    description: string;
    example: string;
  }>;
  example: {
    request: string;
    response: string;
  };
}

const ApiDocumentation: React.FC = () => {
  const [activeEndpoint, setActiveEndpoint] = useState<string>('markdown-pdf');
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  
  const apiKey = 'your_api_key_here';

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const endpoints: ApiEndpoint[] = [
    {
      id: 'markdown-pdf',
      method: 'POST',
      path: '/api/v1/convert/markdown-to-pdf',
      title: 'Markdown to PDF',
      description: 'Convert Markdown documents to professional PDF files',
      requestBody: {
        contentType: 'application/json',
        schema: `{
  "content": "string",
  "options": {
    "theme": "string",
    "pageSize": "string",
    "includeCodeHighlight": "boolean"
  },
  "metadata": {
    "filename": "string"
  }
}`,
        example: `{
  "content": "# Hello World\\n\\nThis is a **markdown** document.",
  "options": {
    "theme": "github",
    "pageSize": "A4",
    "includeCodeHighlight": true
  },
  "metadata": {
    "filename": "document.md"
  }
}`
      },
      responses: [
        {
          status: 200,
          description: 'Successfully converted document',
          example: 'Binary PDF data with appropriate headers'
        },
        {
          status: 400,
          description: 'Invalid request parameters',
          example: `{
  "error": "Invalid content format",
  "code": "INVALID_CONTENT",
  "details": "Content must be valid Markdown"
}`
        }
      ],
      example: {
        request: `curl -X POST "https://api.kanvert.com/v1/convert/markdown-to-pdf" \\
  -H "Authorization: Bearer ${apiKey}" \\
  -H "Content-Type: application/json" \\
  -d '{"content": "# My Document\\nHello **world**!", "options": {"theme": "github"}}' \\
  --output document.pdf`,
        response: `HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="document.pdf"
X-Job-ID: job_123456789

%PDF-1.4 Binary PDF content...`
      }
    },
    {
      id: 'docx-pdf',
      method: 'POST',
      path: '/api/v1/convert/docx-to-pdf',
      title: 'DOCX to PDF',
      description: 'Convert Microsoft Word documents to PDF format',
      requestBody: {
        contentType: 'multipart/form-data',
        schema: `{
  "file": "File",
  "options": {
    "quality": "string",
    "preserveImages": "boolean"
  }
}`,
        example: `Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="document.docx"
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document

[Binary file content]
------WebKitFormBoundary--`
      },
      responses: [
        {
          status: 200,
          description: 'Successfully converted document',
          example: 'Binary PDF data'
        }
      ],
      example: {
        request: `curl -X POST "https://api.kanvert.com/v1/convert/docx-to-pdf" \\
  -H "Authorization: Bearer ${apiKey}" \\
  -F "file=@document.docx" \\
  -F 'options={"quality": "high"}' \\
  --output converted.pdf`,
        response: `HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="converted.pdf"`
      }
    }
  ];

  const codeExamples = {
    javascript: `// Install the Kanvert SDK
npm install @kanvert/sdk

// Initialize the client
import { KanvertClient } from '@kanvert/sdk';

const client = new KanvertClient('${apiKey}');

// Convert Markdown to PDF
const convertMarkdown = async () => {
  try {
    const result = await client.convert.markdownToPdf({
      content: '# Hello World\\n\\nThis is **markdown**!',
      options: {
        theme: 'github',
        pageSize: 'A4'
      }
    });
    
    console.log('Conversion completed:', result.jobId);
    const pdf = await result.download();
    
  } catch (error) {
    console.error('Conversion failed:', error);
  }
};`,
    python: `# Install the Kanvert Python SDK
pip install kanvert-python

import kanvert

# Initialize the client
client = kanvert.Client(api_key='${apiKey}')

# Convert Markdown to PDF
def convert_markdown():
    try:
        result = client.convert.markdown_to_pdf(
            content='# Hello World\\n\\nThis is **markdown**!',
            options={
                'theme': 'github',
                'page_size': 'A4'
            }
        )
        
        print(f'Conversion completed: {result.job_id}')
        
        # Download the PDF
        with open('output.pdf', 'wb') as f:
            f.write(result.download())
            
    except Exception as e:
        print(f'Conversion failed: {e}')`,
    php: `<?php
// Install the Kanvert PHP SDK
composer require kanvert/php-sdk

require_once 'vendor/autoload.php';

use Kanvert\\Client;

// Initialize the client
$client = new Client('${apiKey}');

// Convert Markdown to PDF
try {
    $result = $client->convert->markdownToPdf([
        'content' => '# Hello World\\n\\nThis is **markdown**!',
        'options' => [
            'theme' => 'github',
            'pageSize' => 'A4'
        ]
    ]);
    
    echo 'Conversion completed: ' . $result->jobId;
    
    // Download the PDF
    file_put_contents('output.pdf', $result->download());
    
} catch (Exception $e) {
    echo 'Conversion failed: ' . $e->getMessage();
}`
  };

  const activeEndpointData = endpoints.find(e => e.id === activeEndpoint);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">API Documentation</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Powerful REST API for document conversion. Integrate Kanvert's conversion capabilities 
          into your applications with our comprehensive API.
        </p>
      </div>

      {/* Getting Started */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-5 w-5 text-brand-600" />
            <span>Getting Started</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Authentication</h3>
            <p className="text-gray-600 mb-4">
              All API requests require authentication using your API key. Include it in the Authorization header:
            </p>
            <div className="bg-gray-50 p-4 rounded-lg border">
              <code className="text-sm text-gray-800">
                Authorization: Bearer your_api_key_here
              </code>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Base URL</h3>
            <div className="bg-gray-50 p-4 rounded-lg border">
              <code className="text-sm text-gray-800">
                https://api.kanvert.com/v1
              </code>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Rate Limits</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="font-semibold text-gray-900">Free</p>
                <p className="text-sm text-gray-600">100 requests/hour</p>
              </div>
              <div className="text-center p-4 bg-brand-50 rounded-lg">
                <p className="font-semibold text-brand-900">Professional</p>
                <p className="text-sm text-brand-600">1,000 requests/hour</p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <p className="font-semibold text-purple-900">Enterprise</p>
                <p className="text-sm text-purple-600">10,000 requests/hour</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Endpoints */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Endpoints</CardTitle>
            </CardHeader>
            <CardContent>
              <nav className="space-y-2">
                {endpoints.map((endpoint) => (
                  <button
                    key={endpoint.id}
                    onClick={() => setActiveEndpoint(endpoint.id)}
                    className={`w-full flex items-center justify-between p-3 rounded-lg text-left transition-colors ${
                      activeEndpoint === endpoint.id
                        ? 'bg-brand-50 text-brand-700 border border-brand-200'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs font-medium px-2 py-1 rounded ${
                        endpoint.method === 'POST' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {endpoint.method}
                      </span>
                      <span className="text-sm font-medium">{endpoint.title}</span>
                    </div>
                    <ChevronRight className="h-4 w-4" />
                  </button>
                ))}
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          {activeEndpointData && (
            <>
              {/* Endpoint Details */}
              <Card>
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <span className={`text-xs font-medium px-3 py-1 rounded ${
                      activeEndpointData.method === 'POST' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                    }`}>
                      {activeEndpointData.method}
                    </span>
                    <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                      {activeEndpointData.path}
                    </code>
                  </div>
                  <CardTitle>{activeEndpointData.title}</CardTitle>
                  <p className="text-gray-600">{activeEndpointData.description}</p>
                </CardHeader>
                <CardContent>
                  {/* Request Body */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Request Body</h3>
                    <div>
                      <p className="text-sm text-gray-600 mb-2">Content-Type: {activeEndpointData.requestBody.contentType}</p>
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-medium mb-2">Schema</h4>
                          <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-x-auto">
                            {activeEndpointData.requestBody.schema}
                          </pre>
                        </div>
                        <div>
                          <h4 className="font-medium mb-2">Example</h4>
                          <div className="relative">
                            <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-x-auto pr-12">
                              {activeEndpointData.requestBody.example}
                            </pre>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="absolute top-2 right-2"
                              onClick={() => copyToClipboard(activeEndpointData.requestBody.example, 'request-example')}
                            >
                              {copiedCode === 'request-example' ? (
                                <Check className="h-4 w-4 text-green-600" />
                              ) : (
                                <Copy className="h-4 w-4" />
                              )}
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Responses */}
                  <div className="space-y-4 mt-8">
                    <h3 className="text-lg font-semibold">Responses</h3>
                    <div className="space-y-4">
                      {activeEndpointData.responses.map((response, index) => (
                        <div key={index} className="border rounded-lg p-4">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className={`text-xs font-medium px-2 py-1 rounded ${
                              response.status === 200 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {response.status}
                            </span>
                            <span className="text-sm font-medium">{response.description}</span>
                          </div>
                          <pre className="bg-gray-50 p-3 rounded text-sm text-gray-700">
                            {response.example}
                          </pre>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* cURL Example */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Code className="h-5 w-5" />
                    <span>cURL Example</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Request</h4>
                      <div className="relative">
                        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto pr-12">
                          {activeEndpointData.example.request}
                        </pre>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="absolute top-2 right-2 text-gray-300 hover:text-white"
                          onClick={() => copyToClipboard(activeEndpointData.example.request, 'curl-request')}
                        >
                          {copiedCode === 'curl-request' ? (
                            <Check className="h-4 w-4 text-green-400" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Response</h4>
                      <pre className="bg-gray-50 p-4 rounded-lg text-sm text-gray-700 overflow-x-auto">
                        {activeEndpointData.example.response}
                      </pre>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>

      {/* SDK Examples */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Book className="h-5 w-5" />
            <span>SDK Examples</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {Object.entries(codeExamples).map(([language, code]) => (
              <div key={language} className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium capitalize">{language}</h4>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(code, `sdk-${language}`)}
                  >
                    {copiedCode === `sdk-${language}` ? (
                      <Check className="h-4 w-4 text-green-600" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-xs overflow-x-auto">
                  {code}
                </pre>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Support */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span>Support & Resources</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <a
              href="#"
              className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Book className="h-5 w-5 text-brand-600" />
              <div>
                <p className="font-medium">Guides</p>
                <p className="text-sm text-gray-600">Step-by-step tutorials</p>
              </div>
            </a>
            <a
              href="#"
              className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Code className="h-5 w-5 text-brand-600" />
              <div>
                <p className="font-medium">Examples</p>
                <p className="text-sm text-gray-600">Sample implementations</p>
              </div>
            </a>
            <a
              href="#"
              className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Globe className="h-5 w-5 text-brand-600" />
              <div>
                <p className="font-medium">Community</p>
                <p className="text-sm text-gray-600">Developer forums</p>
              </div>
            </a>
            <a
              href="#"
              className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ExternalLink className="h-5 w-5 text-brand-600" />
              <div>
                <p className="font-medium">Status</p>
                <p className="text-sm text-gray-600">API status page</p>
              </div>
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ApiDocumentation;