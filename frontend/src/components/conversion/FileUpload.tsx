import React, { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Upload,
  FileText,
  X,
  AlertCircle,
  CheckCircle,
  Download,
  RefreshCw,
  File,
  Image,
  FileSpreadsheet,
  FileImage,
  Code
} from 'lucide-react';
import { Button, Badge } from '../common';
import { cn } from '../../utils';
import { toast } from 'react-hot-toast';

interface FileRejection {
  file: File;
  errors: FileError[];
}

interface FileError {
  code: string;
  message: string;
}

interface FileUploadProps {
  onFileSelect?: (files: File[]) => void;
  onFileRemove?: (fileId: string) => void;
  acceptedFileTypes?: string[];
  maxFileSize?: number; // in bytes
  maxFiles?: number;
  multiple?: boolean;
  disabled?: boolean;
  className?: string;
}

interface UploadedFile {
  id: string;
  file: File;
  status: 'uploading' | 'success' | 'error' | 'converting' | 'converted';
  progress: number;
  error?: string;
  downloadUrl?: string;
  convertedFileName?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onFileRemove,
  acceptedFileTypes = [
    '.md', '.docx', '.doc', '.html', '.htm', 
    '.xlsx', '.xls', '.pptx', '.ppt', '.pdf',
    '.txt', '.rtf', '.odt', '.ods', '.odp'
  ],
  maxFileSize = 50 * 1024 * 1024, // 50MB
  maxFiles = 10,
  multiple = true,
  disabled = false,
  className
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      errors.forEach((error: FileError) => {
        if (error.code === 'file-too-large') {
          toast.error(`File ${file.name} is too large. Max size is ${formatFileSize(maxFileSize)}`);
        } else if (error.code === 'file-invalid-type') {
          toast.error(`File ${file.name} has an unsupported format`);
        } else if (error.code === 'too-many-files') {
          toast.error(`Too many files. Maximum allowed is ${maxFiles}`);
        }
      });
    });

    // Handle accepted files
    if (acceptedFiles.length > 0) {
      const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
        id: `${file.name}-${Date.now()}-${Math.random()}`,
        file,
        status: 'uploading',
        progress: 0
      }));

      setUploadedFiles(prev => [...prev, ...newFiles]);

      // Simulate file upload progress
      newFiles.forEach((uploadedFile, index) => {
        simulateUploadProgress(uploadedFile.id, index * 500);
      });

      onFileSelect?.(acceptedFiles);
    }
  }, [maxFileSize, maxFiles, onFileSelect]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/html': ['.html', '.htm'],
      'text/markdown': ['.md'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'text/plain': ['.txt'],
      'application/rtf': ['.rtf'],
      'application/vnd.oasis.opendocument.text': ['.odt'],
      'application/vnd.oasis.opendocument.spreadsheet': ['.ods'],
      'application/vnd.oasis.opendocument.presentation': ['.odp']
    },
    maxSize: maxFileSize,
    maxFiles: multiple ? maxFiles : 1,
    multiple,
    disabled
  });

  const simulateUploadProgress = (fileId: string, delay = 0) => {
    setTimeout(() => {
      let progress = 0;
      const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
          setUploadedFiles(prev =>
            prev.map(f =>
              f.id === fileId
                ? { ...f, status: 'success', progress: 100 }
                : f
            )
          );
        } else {
          setUploadedFiles(prev =>
            prev.map(f =>
              f.id === fileId ? { ...f, progress } : f
            )
          );
        }
      }, 200);
    }, delay);
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    onFileRemove?.(fileId);
  };

  const retryUpload = (fileId: string) => {
    setUploadedFiles(prev =>
      prev.map(f =>
        f.id === fileId
          ? { ...f, status: 'uploading', progress: 0, error: undefined }
          : f
      )
    );
    simulateUploadProgress(fileId);
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.toLowerCase().split('.').pop();
    
    switch (extension) {
      case 'pdf':
        return <FileText className="h-5 w-5 text-red-500" />;
      case 'docx':
      case 'doc':
      case 'odt':
        return <FileText className="h-5 w-5 text-blue-500" />;
      case 'xlsx':
      case 'xls':
      case 'ods':
        return <FileSpreadsheet className="h-5 w-5 text-green-500" />;
      case 'pptx':
      case 'ppt':
      case 'odp':
        return <FileImage className="h-5 w-5 text-orange-500" />;
      case 'html':
      case 'htm':
        return <Code className="h-5 w-5 text-purple-500" />;
      case 'md':
        return <FileText className="h-5 w-5 text-gray-500" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
      case 'bmp':
        return <Image className="h-5 w-5 text-pink-500" />;
      default:
        return <File className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusBadge = (status: UploadedFile['status']) => {
    const statusConfig = {
      uploading: { variant: 'secondary' as const, label: 'Uploading', icon: RefreshCw },
      success: { variant: 'success' as const, label: 'Ready', icon: CheckCircle },
      error: { variant: 'destructive' as const, label: 'Failed', icon: AlertCircle },
      converting: { variant: 'warning' as const, label: 'Converting', icon: RefreshCw },
      converted: { variant: 'info' as const, label: 'Converted', icon: Download }
    };

    const config = statusConfig[status];
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="text-xs">
        <Icon className={cn('h-3 w-3 mr-1', status === 'uploading' || status === 'converting' ? 'animate-spin' : '')} />
        {config.label}
      </Badge>
    );
  };

  return (
    <div className={cn('w-full', className)}>
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={cn(
          'relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200',
          isDragActive && !isDragReject && 'border-brand-500 bg-brand-50',
          isDragReject && 'border-red-500 bg-red-50',
          !isDragActive && 'border-gray-300 hover:border-gray-400 hover:bg-gray-50',
          disabled && 'cursor-not-allowed opacity-50'
        )}
      >
        <input {...getInputProps()} ref={fileInputRef} />
        
        <div className="space-y-4">
          <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
            <Upload className={cn(
              'h-8 w-8',
              isDragActive && !isDragReject && 'text-brand-500',
              isDragReject && 'text-red-500',
              !isDragActive && 'text-gray-400'
            )} />
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {isDragActive
                ? isDragReject
                  ? 'Some files are not supported'
                  : 'Drop files here'
                : 'Upload your documents'
              }
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {isDragActive
                ? 'Release to upload'
                : `Drag & drop files here, or click to browse`
              }
            </p>
          </div>

          <div className="text-xs text-gray-500">
            <p>Supported formats: {acceptedFileTypes.join(', ')}</p>
            <p>Maximum file size: {formatFileSize(maxFileSize)}</p>
            {multiple && <p>Maximum files: {maxFiles}</p>}
          </div>
        </div>
      </div>

      {/* File List */}
      {uploadedFiles.length > 0 && (
        <div className="mt-6 space-y-3">
          <h4 className="text-sm font-medium text-gray-900">
            Uploaded Files ({uploadedFiles.length})
          </h4>
          <div className="space-y-2">
            {uploadedFiles.map((uploadedFile) => (
              <div
                key={uploadedFile.id}
                className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg"
              >
                <div className="flex items-center space-x-3 min-w-0 flex-1">
                  {getFileIcon(uploadedFile.file.name)}
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {uploadedFile.file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(uploadedFile.file.size)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {/* Progress Bar */}
                  {uploadedFile.status === 'uploading' && (
                    <div className="w-24">
                      <div className="bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-brand-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${uploadedFile.progress}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1 text-center">
                        {Math.round(uploadedFile.progress)}%
                      </p>
                    </div>
                  )}

                  {/* Status Badge */}
                  {getStatusBadge(uploadedFile.status)}

                  {/* Actions */}
                  <div className="flex items-center space-x-1">
                    {uploadedFile.status === 'error' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => retryUpload(uploadedFile.id)}
                        className="p-1"
                      >
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                    )}
                    
                    {uploadedFile.status === 'converted' && uploadedFile.downloadUrl && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(uploadedFile.downloadUrl, '_blank')}
                        className="p-1"
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    )}

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(uploadedFile.id)}
                      className="p-1 text-red-500 hover:text-red-600"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error Messages */}
      {uploadedFiles.some(f => f.status === 'error') && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-red-400 mt-0.5" />
            <div className="ml-3">
              <h4 className="text-sm font-medium text-red-800">Upload Errors</h4>
              <div className="mt-1 text-sm text-red-700 space-y-1">
                {uploadedFiles
                  .filter(f => f.status === 'error')
                  .map(f => (
                    <p key={f.id}>
                      {f.file.name}: {f.error || 'Upload failed'}
                    </p>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;