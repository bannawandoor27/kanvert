import React, { useState } from 'react';
import { 
  FileText, 
  Download, 
  Settings, 
  Zap, 
  Code,
  FileSpreadsheet,
  FileImage,
  Layout,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react';
import { Button, Badge, Card } from '../common';
import FileUpload from './FileUpload';
import { cn } from '../../utils';
import { toast } from 'react-hot-toast';

interface ConversionFormat {
  id: string;
  name: string;
  description: string;
  inputFormats: string[];
  outputFormat: string;
  icon: React.ReactNode;
  color: string;
  popular?: boolean;
  options?: ConversionOption[];
}

interface ConversionOption {
  id: string;
  name: string;
  description: string;
  type: 'select' | 'toggle' | 'number' | 'text';
  default: string | number | boolean;
  options?: { label: string; value: string | number | boolean }[];
  min?: number;
  max?: number;
}

interface ConversionJob {
  id: string;
  fileName: string;
  format: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  downloadUrl?: string;
  error?: string;
  startTime: Date;
  endTime?: Date;
}

const ConversionInterface: React.FC = () => {
  const [selectedFormat, setSelectedFormat] = useState<ConversionFormat | null>(null);
  const [conversionOptions, setConversionOptions] = useState<Record<string, string | number | boolean>>({});
  const [conversionJobs, setConversionJobs] = useState<ConversionJob[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const conversionFormats: ConversionFormat[] = [
    {
      id: 'markdown-pdf',
      name: 'Markdown to PDF',
      description: 'Convert Markdown files to professional PDF documents',
      inputFormats: ['.md', '.markdown'],
      outputFormat: 'PDF',
      icon: <FileText className="h-6 w-6" />,
      color: 'bg-blue-500',
      popular: true,
      options: [
        {
          id: 'theme',
          name: 'Theme',
          description: 'PDF styling theme',
          type: 'select',
          default: 'default',
          options: [
            { label: 'Default', value: 'default' },
            { label: 'GitHub', value: 'github' },
            { label: 'Minimal', value: 'minimal' },
            { label: 'Academic', value: 'academic' }
          ]
        },
        {
          id: 'pageSize',
          name: 'Page Size',
          description: 'Output page size',
          type: 'select',
          default: 'A4',
          options: [
            { label: 'A4', value: 'A4' },
            { label: 'Letter', value: 'Letter' },
            { label: 'Legal', value: 'Legal' }
          ]
        },
        {
          id: 'includeCodeHighlight',
          name: 'Code Highlighting',
          description: 'Enable syntax highlighting for code blocks',
          type: 'toggle',
          default: true
        }
      ]
    },
    {
      id: 'docx-pdf',
      name: 'Word to PDF',
      description: 'Convert Word documents to PDF format',
      inputFormats: ['.docx', '.doc'],
      outputFormat: 'PDF',
      icon: <FileText className="h-6 w-6" />,
      color: 'bg-green-500',
      popular: true,
      options: [
        {
          id: 'quality',
          name: 'Quality',
          description: 'PDF output quality',
          type: 'select',
          default: 'high',
          options: [
            { label: 'High', value: 'high' },
            { label: 'Medium', value: 'medium' },
            { label: 'Low', value: 'low' }
          ]
        },
        {
          id: 'preserveImages',
          name: 'Preserve Images',
          description: 'Keep original image quality',
          type: 'toggle',
          default: true
        }
      ]
    },
    {
      id: 'html-pdf',
      name: 'HTML to PDF',
      description: 'Convert HTML pages to PDF documents',
      inputFormats: ['.html', '.htm'],
      outputFormat: 'PDF',
      icon: <Code className="h-6 w-6" />,
      color: 'bg-purple-500',
      options: [
        {
          id: 'pageSize',
          name: 'Page Size',
          description: 'Output page size',
          type: 'select',
          default: 'A4',
          options: [
            { label: 'A4', value: 'A4' },
            { label: 'Letter', value: 'Letter' },
            { label: 'Legal', value: 'Legal' }
          ]
        },
        {
          id: 'landscape',
          name: 'Landscape',
          description: 'Use landscape orientation',
          type: 'toggle',
          default: false
        },
        {
          id: 'margins',
          name: 'Margins (mm)',
          description: 'Page margins',
          type: 'number',
          default: 20,
          min: 0,
          max: 50
        }
      ]
    },
    {
      id: 'excel-pdf',
      name: 'Excel to PDF',
      description: 'Convert spreadsheets to PDF format',
      inputFormats: ['.xlsx', '.xls'],
      outputFormat: 'PDF',
      icon: <FileSpreadsheet className="h-6 w-6" />,
      color: 'bg-orange-500',
      options: [
        {
          id: 'fitToPage',
          name: 'Fit to Page',
          description: 'Scale content to fit page width',
          type: 'toggle',
          default: true
        },
        {
          id: 'includeGridlines',
          name: 'Include Gridlines',
          description: 'Show cell gridlines in PDF',
          type: 'toggle',
          default: false
        }
      ]
    },
    {
      id: 'powerpoint-pdf',
      name: 'PowerPoint to PDF',
      description: 'Convert presentations to PDF format',
      inputFormats: ['.pptx', '.ppt'],
      outputFormat: 'PDF',
      icon: <FileImage className="h-6 w-6" />,
      color: 'bg-red-500',
      options: [
        {
          id: 'slidesPerPage',
          name: 'Slides Per Page',
          description: 'Number of slides per PDF page',
          type: 'select',
          default: 1,
          options: [
            { label: '1 slide', value: 1 },
            { label: '2 slides', value: 2 },
            { label: '4 slides', value: 4 },
            { label: '6 slides', value: 6 }
          ]
        },
        {
          id: 'includeNotes',
          name: 'Include Notes',
          description: 'Include speaker notes in PDF',
          type: 'toggle',
          default: false
        }
      ]
    }
  ];

  const handleFormatSelect = (format: ConversionFormat) => {
    setSelectedFormat(format);
    // Initialize default options
    const defaultOptions: Record<string, string | number | boolean> = {};
    format.options?.forEach(option => {
      defaultOptions[option.id] = option.default;
    });
    setConversionOptions(defaultOptions);
  };

  const handleOptionChange = (optionId: string, value: string | number | boolean) => {
    setConversionOptions(prev => ({
      ...prev,
      [optionId]: value
    }));
  };

  const handleFileSelect = (files: File[]) => {
    if (!selectedFormat) {
      toast.error('Please select a conversion format first');
      return;
    }

    files.forEach(file => {
      const job: ConversionJob = {
        id: `job-${Date.now()}-${Math.random()}`,
        fileName: file.name,
        format: selectedFormat.name,
        status: 'pending',
        progress: 0,
        startTime: new Date()
      };

      setConversionJobs(prev => [job, ...prev]);
      processConversion(job);
    });
  };

  const processConversion = async (job: ConversionJob) => {
    // Update status to processing
    setConversionJobs(prev =>
      prev.map(j => j.id === job.id ? { ...j, status: 'processing' } : j)
    );

    // Simulate conversion progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 10;
      
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        
        // Simulate success/failure (90% success rate)
        const success = Math.random() > 0.1;
        
        setConversionJobs(prev =>
          prev.map(j =>
            j.id === job.id
              ? {
                  ...j,
                  status: success ? 'completed' : 'failed',
                  progress: 100,
                  endTime: new Date(),
                  downloadUrl: success ? `#download-${j.id}` : undefined,
                  error: success ? undefined : 'Conversion failed due to file format issues'
                }
              : j
          )
        );

        if (success) {
          toast.success(`${job.fileName} converted successfully!`);
        } else {
          toast.error(`Failed to convert ${job.fileName}`);
        }
      } else {
        setConversionJobs(prev =>
          prev.map(j => j.id === job.id ? { ...j, progress } : j)
        );
      }
    }, 300);
  };

  const retryConversion = (jobId: string) => {
    const job = conversionJobs.find(j => j.id === jobId);
    if (job) {
      setConversionJobs(prev =>
        prev.map(j =>
          j.id === jobId
            ? { ...j, status: 'pending', progress: 0, error: undefined }
            : j
        )
      );
      processConversion(job);
    }
  };

  const downloadFile = (job: ConversionJob) => {
    if (job.downloadUrl) {
      // In a real app, this would trigger the actual download
      toast.success(`Downloading ${job.fileName.replace(/\.[^/.]+$/, '.pdf')}`);
    }
  };

  const getJobIcon = (status: ConversionJob['status']) => {
    switch (status) {
      case 'pending':
      case 'processing':
        return <Clock className="h-4 w-4 text-yellow-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getJobBadge = (status: ConversionJob['status']) => {
    const statusConfig = {
      pending: { variant: 'secondary' as const, label: 'Pending' },
      processing: { variant: 'warning' as const, label: 'Processing' },
      completed: { variant: 'success' as const, label: 'Completed' },
      failed: { variant: 'destructive' as const, label: 'Failed' }
    };

    const config = statusConfig[status];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Document Conversion
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Convert your documents to PDF with professional quality and customizable options
          </p>
        </div>

        {/* Format Selection */}
        <Card className="p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            1. Choose Conversion Format
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {conversionFormats.map((format) => (
              <button
                key={format.id}
                onClick={() => handleFormatSelect(format)}
                className={cn(
                  'relative p-6 border-2 rounded-lg text-left transition-all duration-200 hover:shadow-md',
                  selectedFormat?.id === format.id
                    ? 'border-brand-500 bg-brand-50'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                {format.popular && (
                  <div className="absolute -top-2 -right-2">
                    <Badge variant="warning" className="text-xs">
                      Popular
                    </Badge>
                  </div>
                )}
                <div className="flex items-start space-x-4">
                  <div className={cn('p-3 rounded-lg', format.color)}>
                    <div className="text-white">
                      {format.icon}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {format.name}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2">
                      {format.description}
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {format.inputFormats.map(ext => (
                        <span
                          key={ext}
                          className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                        >
                          {ext}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </Card>

        {/* Conversion Options */}
        {selectedFormat && selectedFormat.options && (
          <Card className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-gray-900">
                2. Conversion Options
              </h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAdvanced(!showAdvanced)}
                leftIcon={<Settings className="h-4 w-4" />}
              >
                {showAdvanced ? 'Hide' : 'Show'} Advanced
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {selectedFormat.options.map((option) => (
                <div key={option.id} className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    {option.name}
                  </label>
                  <p className="text-xs text-gray-500">{option.description}</p>
                  
                  {option.type === 'select' && (
                    <select
                      value={conversionOptions[option.id] || option.default}
                      onChange={(e) => handleOptionChange(option.id, e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
                    >
                      {option.options?.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  )}
                  
                  {option.type === 'toggle' && (
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={conversionOptions[option.id] ?? option.default}
                        onChange={(e) => handleOptionChange(option.id, e.target.checked)}
                        className="h-4 w-4 text-brand-600 focus:ring-brand-500 border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-600">Enabled</span>
                    </label>
                  )}
                  
                  {option.type === 'number' && (
                    <input
                      type="number"
                      value={conversionOptions[option.id] || option.default}
                      onChange={(e) => handleOptionChange(option.id, parseInt(e.target.value))}
                      min={option.min}
                      max={option.max}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  )}
                  
                  {option.type === 'text' && (
                    <input
                      type="text"
                      value={conversionOptions[option.id] || option.default}
                      onChange={(e) => handleOptionChange(option.id, e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  )}
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* File Upload */}
        <Card className="p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            3. Upload Files
          </h2>
          {selectedFormat ? (
            <FileUpload
              onFileSelect={handleFileSelect}
              acceptedFileTypes={selectedFormat.inputFormats}
              maxFileSize={50 * 1024 * 1024} // 50MB
              maxFiles={10}
            />
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <Layout className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Please select a conversion format first</p>
            </div>
          )}
        </Card>

        {/* Conversion Jobs */}
        {conversionJobs.length > 0 && (
          <Card className="p-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">
              Conversion Jobs ({conversionJobs.length})
            </h2>
            <div className="space-y-3">
              {conversionJobs.map((job) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3 min-w-0 flex-1">
                    {getJobIcon(job.status)}
                    <div className="min-w-0 flex-1">
                      <p className="font-medium text-gray-900 truncate">
                        {job.fileName}
                      </p>
                      <p className="text-sm text-gray-500">
                        {job.format} • Started {job.startTime.toLocaleTimeString()}
                      </p>
                      {job.error && (
                        <p className="text-sm text-red-600 mt-1">{job.error}</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    {/* Progress Bar */}
                    {(job.status === 'pending' || job.status === 'processing') && (
                      <div className="w-32">
                        <div className="bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-brand-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${job.progress}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1 text-center">
                          {Math.round(job.progress)}%
                        </p>
                      </div>
                    )}

                    {/* Status Badge */}
                    {getJobBadge(job.status)}

                    {/* Actions */}
                    <div className="flex items-center space-x-2">
                      {job.status === 'completed' && (
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => downloadFile(job)}
                          leftIcon={<Download className="h-4 w-4" />}
                        >
                          Download
                        </Button>
                      )}
                      
                      {job.status === 'failed' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => retryConversion(job.id)}
                          leftIcon={<Zap className="h-4 w-4" />}
                        >
                          Retry
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ConversionInterface;