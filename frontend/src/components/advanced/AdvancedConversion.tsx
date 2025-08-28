import React, { useState } from 'react';
import {
  Settings,
  Plus,
  Trash2,
  Play,
  Pause,
  RotateCcw,
  Download,
  Upload,
  Clock,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Copy,
  FolderOpen,
  Zap,
  Layers,
  Calendar,
  Filter
} from 'lucide-react';
import { Button, Badge, Card, Input } from '../common';
import FileUpload from '../conversion/FileUpload';
import { cn } from '../../utils';
import { toast } from 'react-hot-toast';

interface BatchJob {
  id: string;
  name: string;
  files: BatchFile[];
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'paused';
  progress: number;
  createdAt: Date;
  completedAt?: Date;
  options: ConversionOptions;
}

interface BatchFile {
  id: string;
  file: File;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'skipped';
  progress: number;
  outputUrl?: string;
  error?: string;
}

interface ConversionOptions {
  outputFormat: string;
  quality: string;
  pageSize: string;
  orientation: 'portrait' | 'landscape';
  margins: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  watermark?: {
    enabled: boolean;
    text: string;
    opacity: number;
    position: string;
  };
  password?: {
    enabled: boolean;
    value: string;
  };
  compression: number;
  includeMetadata: boolean;
  customCss?: string;
  javascript?: string;
}

interface ConversionTemplate {
  id: string;
  name: string;
  description: string;
  options: ConversionOptions;
  isDefault?: boolean;
}

const AdvancedConversion: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'batch' | 'templates' | 'scheduler'>('batch');
  const [batchJobs, setBatchJobs] = useState<BatchJob[]>([]);
  const [currentJob, setCurrentJob] = useState<Partial<BatchJob> | null>(null);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);

  const defaultOptions: ConversionOptions = {
    outputFormat: 'pdf',
    quality: 'high',
    pageSize: 'A4',
    orientation: 'portrait',
    margins: { top: 20, bottom: 20, left: 20, right: 20 },
    watermark: { enabled: false, text: '', opacity: 50, position: 'bottom-right' },
    password: { enabled: false, value: '' },
    compression: 80,
    includeMetadata: true
  };

  const [options, setOptions] = useState<ConversionOptions>(defaultOptions);

  const templates: ConversionTemplate[] = [
    {
      id: 'standard',
      name: 'Standard PDF',
      description: 'Basic PDF conversion with default settings',
      options: defaultOptions,
      isDefault: true
    },
    {
      id: 'print-ready',
      name: 'Print Ready',
      description: 'High-quality PDF optimized for printing',
      options: {
        ...defaultOptions,
        quality: 'ultra',
        pageSize: 'A4',
        margins: { top: 25, bottom: 25, left: 25, right: 25 },
        compression: 95
      }
    },
    {
      id: 'web-optimized',
      name: 'Web Optimized',
      description: 'Compressed PDF for web distribution',
      options: {
        ...defaultOptions,
        quality: 'medium',
        compression: 60,
        includeMetadata: false
      }
    },
    {
      id: 'secure',
      name: 'Secure Document',
      description: 'Password-protected PDF with watermark',
      options: {
        ...defaultOptions,
        password: { enabled: true, value: '' },
        watermark: {
          enabled: true,
          text: 'CONFIDENTIAL',
          opacity: 30,
          position: 'center'
        }
      }
    }
  ];

  const createBatchJob = () => {
    const newJob: BatchJob = {
      id: `job_${Date.now()}`,
      name: `Batch Job ${batchJobs.length + 1}`,
      files: [],
      status: 'pending',
      progress: 0,
      createdAt: new Date(),
      options: { ...options }
    };

    setBatchJobs(prev => [newJob, ...prev]);
    setCurrentJob(newJob);
  };

  const updateJobOptions = (updates: Partial<ConversionOptions>) => {
    setOptions(prev => ({ ...prev, ...updates }));
    
    if (currentJob) {
      setBatchJobs(prev =>
        prev.map(job =>
          job.id === currentJob.id
            ? { ...job, options: { ...job.options, ...updates } }
            : job
        )
      );
    }
  };

  const addFilesToJob = (files: File[]) => {
    if (!currentJob) {
      createBatchJob();
    }

    const batchFiles: BatchFile[] = files.map(file => ({
      id: `file_${Date.now()}_${Math.random()}`,
      file,
      status: 'pending',
      progress: 0
    }));

    setBatchJobs(prev =>
      prev.map(job =>
        job.id === (currentJob?.id || prev[0]?.id)
          ? { ...job, files: [...job.files, ...batchFiles] }
          : job
      )
    );
  };

  const startBatchJob = (jobId: string) => {
    setBatchJobs(prev =>
      prev.map(job =>
        job.id === jobId ? { ...job, status: 'processing' } : job
      )
    );

    // Simulate batch processing
    const job = batchJobs.find(j => j.id === jobId);
    if (job) {
      processBatchFiles(job);
    }
  };

  const processBatchFiles = (job: BatchJob) => {
    let completedFiles = 0;
    const totalFiles = job.files.length;

    job.files.forEach((file, index) => {
      setTimeout(() => {
        // Simulate file processing
        const processingTime = Math.random() * 3000 + 1000;
        
        setBatchJobs(prev =>
          prev.map(j =>
            j.id === job.id
              ? {
                  ...j,
                  files: j.files.map(f =>
                    f.id === file.id
                      ? { ...f, status: 'processing' }
                      : f
                  )
                }
              : j
          )
        );

        setTimeout(() => {
          const success = Math.random() > 0.1; // 90% success rate
          completedFiles++;
          
          setBatchJobs(prev =>
            prev.map(j =>
              j.id === job.id
                ? {
                    ...j,
                    files: j.files.map(f =>
                      f.id === file.id
                        ? {
                            ...f,
                            status: success ? 'completed' : 'failed',
                            progress: 100,
                            outputUrl: success ? `#download_${f.id}` : undefined,
                            error: success ? undefined : 'Conversion failed'
                          }
                        : f
                    ),
                    progress: (completedFiles / totalFiles) * 100,
                    status: completedFiles === totalFiles ? 'completed' : 'processing',
                    completedAt: completedFiles === totalFiles ? new Date() : undefined
                  }
                : j
            )
          );

          if (completedFiles === totalFiles) {
            toast.success(`Batch job completed: ${completedFiles}/${totalFiles} files processed`);
          }
        }, processingTime);
      }, index * 500);
    });
  };

  const pauseBatchJob = (jobId: string) => {
    setBatchJobs(prev =>
      prev.map(job =>
        job.id === jobId ? { ...job, status: 'paused' } : job
      )
    );
    toast.info('Batch job paused');
  };

  const downloadAllFiles = (jobId: string) => {
    const job = batchJobs.find(j => j.id === jobId);
    const completedFiles = job?.files.filter(f => f.status === 'completed') || [];
    toast.success(`Downloading ${completedFiles.length} files as ZIP`);
  };

  const applyTemplate = (template: ConversionTemplate) => {
    setOptions(template.options);
    toast.success(`Applied template: ${template.name}`);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-gray-500" />;
      case 'processing':
        return <Zap className="h-4 w-4 text-yellow-500 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'paused':
        return <Pause className="h-4 w-4 text-orange-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      pending: 'secondary' as const,
      processing: 'warning' as const,
      completed: 'success' as const,
      failed: 'destructive' as const,
      paused: 'warning' as const
    };
    
    return (
      <Badge variant={variants[status as keyof typeof variants] || 'secondary'}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const renderBatchProcessing = () => (
    <div className="space-y-6">
      {/* Create New Job */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Create Batch Job</h3>
          <Button
            variant="primary"
            onClick={createBatchJob}
            leftIcon={<Plus className="h-4 w-4" />}
          >
            New Batch Job
          </Button>
        </div>

        {currentJob && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Name
              </label>
              <Input
                value={currentJob.name || ''}
                onChange={(e) => setCurrentJob(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter job name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Files
              </label>
              <FileUpload
                onFileSelect={addFilesToJob}
                multiple={true}
                maxFiles={50}
              />
            </div>
          </div>
        )}
      </Card>

      {/* Advanced Options */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Conversion Options</h3>
          <Button
            variant="ghost"
            onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
            leftIcon={<Settings className="h-4 w-4" />}
          >
            {showAdvancedOptions ? 'Hide' : 'Show'} Advanced
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Output Format
            </label>
            <select
              value={options.outputFormat}
              onChange={(e) => updateJobOptions({ outputFormat: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500"
            >
              <option value="pdf">PDF</option>
              <option value="docx">Word Document</option>
              <option value="html">HTML</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Quality
            </label>
            <select
              value={options.quality}
              onChange={(e) => updateJobOptions({ quality: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="ultra">Ultra</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Page Size
            </label>
            <select
              value={options.pageSize}
              onChange={(e) => updateJobOptions({ pageSize: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500"
            >
              <option value="A4">A4</option>
              <option value="Letter">Letter</option>
              <option value="Legal">Legal</option>
              <option value="A3">A3</option>
            </select>
          </div>
        </div>

        {showAdvancedOptions && (
          <div className="mt-6 pt-6 border-t border-gray-200 space-y-6">
            {/* Margins */}
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Margins (mm)</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {(['top', 'bottom', 'left', 'right'] as const).map((side) => (
                  <div key={side}>
                    <label className="block text-sm text-gray-700 mb-1 capitalize">
                      {side}
                    </label>
                    <Input
                      type="number"
                      value={options.margins[side]}
                      onChange={(e) => updateJobOptions({
                        margins: {
                          ...options.margins,
                          [side]: parseInt(e.target.value) || 0
                        }
                      })}
                      min="0"
                      max="100"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Watermark */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900">Watermark</h4>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={options.watermark?.enabled || false}
                    onChange={(e) => updateJobOptions({
                      watermark: {
                        ...options.watermark,
                        enabled: e.target.checked
                      }
                    })}
                    className="h-4 w-4 text-brand-600 focus:ring-brand-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable watermark</span>
                </label>
              </div>
              
              {options.watermark?.enabled && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Input
                    placeholder="Watermark text"
                    value={options.watermark.text}
                    onChange={(e) => updateJobOptions({
                      watermark: {
                        ...options.watermark,
                        text: e.target.value
                      }
                    })}
                  />
                  <Input
                    type="number"
                    placeholder="Opacity (0-100)"
                    value={options.watermark.opacity}
                    onChange={(e) => updateJobOptions({
                      watermark: {
                        ...options.watermark,
                        opacity: parseInt(e.target.value) || 50
                      }
                    })}
                    min="0"
                    max="100"
                  />
                  <select
                    value={options.watermark.position}
                    onChange={(e) => updateJobOptions({
                      watermark: {
                        ...options.watermark,
                        position: e.target.value
                      }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500"
                  >
                    <option value="center">Center</option>
                    <option value="top-left">Top Left</option>
                    <option value="top-right">Top Right</option>
                    <option value="bottom-left">Bottom Left</option>
                    <option value="bottom-right">Bottom Right</option>
                  </select>
                </div>
              )}
            </div>

            {/* Password Protection */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900">Password Protection</h4>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={options.password?.enabled || false}
                    onChange={(e) => updateJobOptions({
                      password: {
                        ...options.password,
                        enabled: e.target.checked
                      }
                    })}
                    className="h-4 w-4 text-brand-600 focus:ring-brand-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Password protect PDF</span>
                </label>
              </div>
              
              {options.password?.enabled && (
                <Input
                  type="password"
                  placeholder="Enter password"
                  value={options.password.value}
                  onChange={(e) => updateJobOptions({
                    password: {
                      ...options.password,
                      value: e.target.value
                    }
                  })}
                />
              )}
            </div>
          </div>
        )}
      </Card>

      {/* Active Jobs */}
      {batchJobs.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Batch Jobs</h3>
          <div className="space-y-4">
            {batchJobs.map((job) => (
              <div
                key={job.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-medium text-gray-900">{job.name}</h4>
                    <p className="text-sm text-gray-600">
                      {job.files.length} files • Created {job.createdAt.toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(job.status)}
                    {getStatusBadge(job.status)}
                  </div>
                </div>

                {/* Progress Bar */}
                {job.status === 'processing' && (
                  <div className="mb-3">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Progress</span>
                      <span>{Math.round(job.progress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-brand-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${job.progress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* File List */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-3">
                  {job.files.slice(0, 4).map((file) => (
                    <div key={file.id} className="flex items-center space-x-2 text-sm">
                      {getStatusIcon(file.status)}
                      <span className="truncate">{file.file.name}</span>
                    </div>
                  ))}
                  {job.files.length > 4 && (
                    <div className="text-sm text-gray-500">
                      +{job.files.length - 4} more files
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex space-x-2">
                  {job.status === 'pending' && (
                    <Button
                      size="sm"
                      onClick={() => startBatchJob(job.id)}
                      leftIcon={<Play className="h-4 w-4" />}
                    >
                      Start
                    </Button>
                  )}
                  
                  {job.status === 'processing' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => pauseBatchJob(job.id)}
                      leftIcon={<Pause className="h-4 w-4" />}
                    >
                      Pause
                    </Button>
                  )}
                  
                  {job.status === 'completed' && (
                    <Button
                      size="sm"
                      variant="primary"
                      onClick={() => downloadAllFiles(job.id)}
                      leftIcon={<Download className="h-4 w-4" />}
                    >
                      Download All
                    </Button>
                  )}
                  
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );

  const renderTemplates = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Conversion Templates</h3>
        <Button variant="primary" leftIcon={<Plus className="h-4 w-4" />}>
          Create Template
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {templates.map((template) => (
          <Card key={template.id} className="p-6">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h4 className="font-medium text-gray-900">{template.name}</h4>
                {template.isDefault && (
                  <Badge variant="info" className="mt-1">Default</Badge>
                )}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => applyTemplate(template)}
              >
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
            
            <p className="text-sm text-gray-600 mb-4">{template.description}</p>
            
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">Quality:</span>
                <span className="font-medium">{template.options.quality}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Page Size:</span>
                <span className="font-medium">{template.options.pageSize}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Compression:</span>
                <span className="font-medium">{template.options.compression}%</span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderScheduler = () => (
    <div className="text-center py-12">
      <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">Scheduled Conversions</h3>
      <p className="text-gray-600 mb-6">
        Schedule batch conversions to run at specific times or intervals
      </p>
      <Button variant="primary">Create Schedule</Button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Advanced Conversion Tools
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Batch processing, advanced options, and conversion automation for power users
          </p>
        </div>

        {/* Tabs */}
        <div className="flex justify-center">
          <div className="flex space-x-1 bg-white p-1 rounded-lg border border-gray-200">
            {[
              { id: 'batch', name: 'Batch Processing', icon: Layers },
              { id: 'templates', name: 'Templates', icon: Copy },
              { id: 'scheduler', name: 'Scheduler', icon: Calendar }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={cn(
                    'flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
                    activeTab === tab.id
                      ? 'bg-brand-600 text-white'
                      : 'text-gray-600 hover:text-gray-900'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'batch' && renderBatchProcessing()}
        {activeTab === 'templates' && renderTemplates()}
        {activeTab === 'scheduler' && renderScheduler()}
      </div>
    </div>
  );
};

export default AdvancedConversion;