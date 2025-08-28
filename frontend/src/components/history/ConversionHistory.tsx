import React, { useState, useMemo } from 'react';
import {
  Search,
  Filter,
  Calendar,
  Download,
  Trash2,
  RefreshCw,
  ChevronDown,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock,
  Eye,
  MoreVertical,
  Archive,
  Share
} from 'lucide-react';
import { Button, Badge, Card, Input } from '../common';
import { cn } from '../../utils';
import { toast } from 'react-hot-toast';

interface ConversionRecord {
  id: string;
  fileName: string;
  originalFormat: string;
  targetFormat: string;
  status: 'completed' | 'failed' | 'processing' | 'archived';
  createdAt: Date;
  completedAt?: Date;
  fileSize: number;
  downloadUrl?: string;
  error?: string;
  duration?: number; // in seconds
}

interface FilterOptions {
  status: string;
  format: string;
  dateRange: string;
  search: string;
}

const ConversionHistory: React.FC = () => {
  const [records] = useState<ConversionRecord[]>([
    {
      id: '1',
      fileName: 'project-report.docx',
      originalFormat: 'DOCX',
      targetFormat: 'PDF',
      status: 'completed',
      createdAt: new Date('2024-01-15T10:30:00'),
      completedAt: new Date('2024-01-15T10:30:45'),
      fileSize: 2456789,
      downloadUrl: '#download-1',
      duration: 45
    },
    {
      id: '2',
      fileName: 'presentation.pptx',
      originalFormat: 'PPTX',
      targetFormat: 'PDF',
      status: 'completed',
      createdAt: new Date('2024-01-14T14:22:00'),
      completedAt: new Date('2024-01-14T14:23:15'),
      fileSize: 8912345,
      downloadUrl: '#download-2',
      duration: 75
    },
    {
      id: '3',
      fileName: 'readme.md',
      originalFormat: 'MD',
      targetFormat: 'PDF',
      status: 'completed',
      createdAt: new Date('2024-01-14T09:15:00'),
      completedAt: new Date('2024-01-14T09:15:12'),
      fileSize: 123456,
      downloadUrl: '#download-3',
      duration: 12
    },
    {
      id: '4',
      fileName: 'corrupted-file.docx',
      originalFormat: 'DOCX',
      targetFormat: 'PDF',
      status: 'failed',
      createdAt: new Date('2024-01-13T16:45:00'),
      fileSize: 5234567,
      error: 'File appears to be corrupted or password protected'
    },
    {
      id: '5',
      fileName: 'large-spreadsheet.xlsx',
      originalFormat: 'XLSX',
      targetFormat: 'PDF',
      status: 'processing',
      createdAt: new Date('2024-01-15T11:00:00'),
      fileSize: 15678901
    }
  ]);

  const [filters, setFilters] = useState<FilterOptions>({
    status: 'all',
    format: 'all',
    dateRange: 'all',
    search: ''
  });

  const [selectedRecords, setSelectedRecords] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'size' | 'duration'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Filter and sort records
  const filteredAndSortedRecords = useMemo(() => {
    let filtered = records;

    // Apply filters
    if (filters.status !== 'all') {
      filtered = filtered.filter(record => record.status === filters.status);
    }

    if (filters.format !== 'all') {
      filtered = filtered.filter(record => 
        record.originalFormat === filters.format || record.targetFormat === filters.format
      );
    }

    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filtered = filtered.filter(record =>
        record.fileName.toLowerCase().includes(searchTerm) ||
        record.originalFormat.toLowerCase().includes(searchTerm) ||
        record.targetFormat.toLowerCase().includes(searchTerm)
      );
    }

    if (filters.dateRange !== 'all') {
      const now = new Date();
      const ranges = {
        today: 1,
        week: 7,
        month: 30,
        quarter: 90
      };
      
      if (ranges[filters.dateRange as keyof typeof ranges]) {
        const daysAgo = ranges[filters.dateRange as keyof typeof ranges];
        const cutoff = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(record => record.createdAt >= cutoff);
      }
    }

    // Sort records
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'date':
          comparison = a.createdAt.getTime() - b.createdAt.getTime();
          break;
        case 'name':
          comparison = a.fileName.localeCompare(b.fileName);
          break;
        case 'size':
          comparison = a.fileSize - b.fileSize;
          break;
        case 'duration':
          comparison = (a.duration || 0) - (b.duration || 0);
          break;
      }
      
      return sortOrder === 'desc' ? -comparison : comparison;
    });

    return filtered;
  }, [records, filters, sortBy, sortOrder]);

  // Pagination
  const totalPages = Math.ceil(filteredAndSortedRecords.length / itemsPerPage);
  const paginatedRecords = filteredAndSortedRecords.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleFilterChange = (key: keyof FilterOptions, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  const handleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const handleSelectRecord = (recordId: string) => {
    setSelectedRecords(prev =>
      prev.includes(recordId)
        ? prev.filter(id => id !== recordId)
        : [...prev, recordId]
    );
  };

  const handleSelectAll = () => {
    if (selectedRecords.length === paginatedRecords.length) {
      setSelectedRecords([]);
    } else {
      setSelectedRecords(paginatedRecords.map(record => record.id));
    }
  };

  const handleBulkAction = (action: 'download' | 'delete' | 'archive') => {
    if (selectedRecords.length === 0) return;

    switch (action) {
      case 'download':
        toast.success(`Downloading ${selectedRecords.length} files`);
        break;
      case 'delete':
        toast.success(`Deleted ${selectedRecords.length} records`);
        break;
      case 'archive':
        toast.success(`Archived ${selectedRecords.length} records`);
        break;
    }
    
    setSelectedRecords([]);
  };

  const formatFileSize = (bytes: number): string => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDuration = (seconds?: number): string => {
    if (!seconds) return 'N/A';
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getStatusIcon = (status: ConversionRecord['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'processing':
        return <Clock className="h-4 w-4 text-yellow-500 animate-spin" />;
      case 'archived':
        return <Archive className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: ConversionRecord['status']) => {
    const variants = {
      completed: 'success' as const,
      failed: 'destructive' as const,
      processing: 'warning' as const,
      archived: 'secondary' as const
    };
    
    return (
      <Badge variant={variants[status]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Conversion History</h1>
            <p className="text-gray-600 mt-1">
              Track and manage your document conversion history
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              leftIcon={<Filter className="h-4 w-4" />}
            >
              Filters
            </Button>
            <Button
              variant="outline"
              size="sm"
              leftIcon={<RefreshCw className="h-4 w-4" />}
            >
              Refresh
            </Button>
          </div>
        </div>

        {/* Search and Quick Filters */}
        <Card className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search by filename, format..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                leftIcon={<Search className="h-4 w-4 text-gray-400" />}
              />
            </div>
            <div className="flex gap-2">
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="processing">Processing</option>
                <option value="archived">Archived</option>
              </select>
              <select
                value={filters.dateRange}
                onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="quarter">This Quarter</option>
              </select>
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Format
                  </label>
                  <select
                    value={filters.format}
                    onChange={(e) => handleFilterChange('format', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500"
                  >
                    <option value="all">All Formats</option>
                    <option value="PDF">PDF</option>
                    <option value="DOCX">DOCX</option>
                    <option value="XLSX">XLSX</option>
                    <option value="PPTX">PPTX</option>
                    <option value="MD">Markdown</option>
                    <option value="HTML">HTML</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sort By
                  </label>
                  <select
                    value={sortBy}
                    onChange={(e) => handleSort(e.target.value as typeof sortBy)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500"
                  >
                    <option value="date">Date</option>
                    <option value="name">Name</option>
                    <option value="size">Size</option>
                    <option value="duration">Duration</option>
                  </select>
                </div>
                <div className="flex items-end">
                  <Button
                    variant="outline"
                    onClick={() => setFilters({ status: 'all', format: 'all', dateRange: 'all', search: '' })}
                    className="w-full"
                  >
                    Clear Filters
                  </Button>
                </div>
              </div>
            </div>
          )}
        </Card>

        {/* Bulk Actions */}
        {selectedRecords.length > 0 && (
          <Card className="p-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">
                {selectedRecords.length} items selected
              </span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleBulkAction('download')}
                  leftIcon={<Download className="h-4 w-4" />}
                >
                  Download All
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleBulkAction('archive')}
                  leftIcon={<Archive className="h-4 w-4" />}
                >
                  Archive
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleBulkAction('delete')}
                  leftIcon={<Trash2 className="h-4 w-4" />}
                >
                  Delete
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Records Table */}
        <Card className="p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedRecords.length === paginatedRecords.length && paginatedRecords.length > 0}
                      onChange={handleSelectAll}
                      className="h-4 w-4 text-brand-600 focus:ring-brand-500 border-gray-300 rounded"
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <button
                      onClick={() => handleSort('name')}
                      className="flex items-center space-x-1 hover:text-gray-700"
                    >
                      <span>File</span>
                      <ChevronDown className="h-4 w-4" />
                    </button>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Format
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <button
                      onClick={() => handleSort('size')}
                      className="flex items-center space-x-1 hover:text-gray-700"
                    >
                      <span>Size</span>
                      <ChevronDown className="h-4 w-4" />
                    </button>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <button
                      onClick={() => handleSort('duration')}
                      className="flex items-center space-x-1 hover:text-gray-700"
                    >
                      <span>Duration</span>
                      <ChevronDown className="h-4 w-4" />
                    </button>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <button
                      onClick={() => handleSort('date')}
                      className="flex items-center space-x-1 hover:text-gray-700"
                    >
                      <span>Date</span>
                      <ChevronDown className="h-4 w-4" />
                    </button>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {paginatedRecords.map((record) => (
                  <tr
                    key={record.id}
                    className={cn(
                      'hover:bg-gray-50 transition-colors',
                      selectedRecords.includes(record.id) && 'bg-blue-50'
                    )}
                  >
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedRecords.includes(record.id)}
                        onChange={() => handleSelectRecord(record.id)}
                        className="h-4 w-4 text-brand-600 focus:ring-brand-500 border-gray-300 rounded"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <FileText className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                            {record.fileName}
                          </p>
                          {record.error && (
                            <p className="text-xs text-red-600 truncate max-w-xs">
                              {record.error}
                            </p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                          {record.originalFormat}
                        </span>
                        <span className="text-gray-400">→</span>
                        <span className="text-xs bg-brand-100 text-brand-700 px-2 py-1 rounded">
                          {record.targetFormat}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(record.status)}
                        {getStatusBadge(record.status)}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {formatFileSize(record.fileSize)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {formatDuration(record.duration)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div>
                        <p>{record.createdAt.toLocaleDateString()}</p>
                        <p className="text-xs text-gray-500">
                          {record.createdAt.toLocaleTimeString()}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        {record.status === 'completed' && record.downloadUrl && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toast.success('Downloading file...')}
                            className="p-1"
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toast.info('View details')}
                          className="p-1"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="p-1"
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Empty State */}
          {filteredAndSortedRecords.length === 0 && (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No conversion records found</p>
              <p className="text-gray-400 mt-1">
                {filters.search || filters.status !== 'all' || filters.format !== 'all' || filters.dateRange !== 'all'
                  ? 'Try adjusting your filters or search terms'
                  : 'Your conversion history will appear here'}
              </p>
            </div>
          )}
        </Card>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-700">
              Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, filteredAndSortedRecords.length)} of {filteredAndSortedRecords.length} results
            </p>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <Button
                  key={page}
                  variant={currentPage === page ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setCurrentPage(page)}
                  className="w-10"
                >
                  {page}
                </Button>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversionHistory;