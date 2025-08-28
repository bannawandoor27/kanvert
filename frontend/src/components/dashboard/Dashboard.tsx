import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Download,
  Upload,
  BarChart3,
  Activity,
  Calendar,
  Filter,
  RefreshCw,
  Plus,
  ArrowRight,
  Zap,
  Star
} from 'lucide-react';
import { Button, Badge, Card } from '../common';
import { useAuthStore } from '../../stores/authStore';
import { cn } from '../../utils';

interface ConversionStats {
  totalConversions: number;
  successRate: number;
  avgProcessingTime: number;
  totalSizeProcessed: string;
  monthlyConversions: number;
  weeklyConversions: number;
  todayConversions: number;
}

interface RecentActivity {
  id: string;
  type: 'conversion' | 'upload' | 'download' | 'error';
  title: string;
  description: string;
  status: 'completed' | 'processing' | 'failed' | 'pending';
  timestamp: string;
  size?: string;
  format?: string;
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  href: string;
  color: string;
  popular?: boolean;
}

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();
  const [selectedPeriod, setSelectedPeriod] = useState<'today' | 'week' | 'month'>('month');
  const [refreshing, setRefreshing] = useState(false);

  // Mock data - replace with real API calls
  const stats: ConversionStats = {
    totalConversions: 1247,
    successRate: 98.5,
    avgProcessingTime: 2.3,
    totalSizeProcessed: '15.2 GB',
    monthlyConversions: 89,
    weeklyConversions: 23,
    todayConversions: 5,
  };

  const recentActivity: RecentActivity[] = [
    {
      id: '1',
      type: 'conversion',
      title: 'Document converted successfully',
      description: 'report.docx → report.pdf',
      status: 'completed',
      timestamp: '2 minutes ago',
      size: '2.4 MB',
      format: 'PDF'
    },
    {
      id: '2',
      type: 'upload',
      title: 'File uploaded for processing',
      description: 'presentation.pptx',
      status: 'processing',
      timestamp: '5 minutes ago',
      size: '8.1 MB',
      format: 'PPTX'
    },
    {
      id: '3',
      type: 'conversion',
      title: 'Markdown to PDF conversion',
      description: 'README.md → documentation.pdf',
      status: 'completed',
      timestamp: '1 hour ago',
      size: '156 KB',
      format: 'PDF'
    },
    {
      id: '4',
      type: 'download',
      title: 'Converted file downloaded',
      description: 'invoice_march.pdf',
      status: 'completed',
      timestamp: '2 hours ago',
      size: '1.2 MB',
      format: 'PDF'
    },
    {
      id: '5',
      type: 'error',
      title: 'Conversion failed',
      description: 'corrupted-file.docx',
      status: 'failed',
      timestamp: '3 hours ago',
      size: '12.3 MB',
      format: 'DOCX'
    }
  ];

  const quickActions: QuickAction[] = [
    {
      id: 'markdown-pdf',
      title: 'Markdown to PDF',
      description: 'Convert Markdown files to professional PDFs',
      icon: <FileText className="h-6 w-6" />,
      href: '/convert/markdown-pdf',
      color: 'bg-blue-500',
      popular: true
    },
    {
      id: 'docx-pdf',
      title: 'Word to PDF',
      description: 'Convert Word documents to PDF format',
      icon: <FileText className="h-6 w-6" />,
      href: '/convert/docx-pdf',
      color: 'bg-green-500',
      popular: true
    },
    {
      id: 'html-pdf',
      title: 'HTML to PDF',
      description: 'Convert HTML pages to PDF documents',
      icon: <FileText className="h-6 w-6" />,
      href: '/convert/html-pdf',
      color: 'bg-purple-500'
    },
    {
      id: 'excel-pdf',
      title: 'Excel to PDF',
      description: 'Convert spreadsheets to PDF format',
      icon: <BarChart3 className="h-6 w-6" />,
      href: '/convert/excel-pdf',
      color: 'bg-orange-500'
    }
  ];

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const getActivityIcon = (type: string, status: string) => {
    if (status === 'failed') return <AlertCircle className="h-4 w-4 text-red-500" />;
    if (status === 'processing') return <Clock className="h-4 w-4 text-yellow-500" />;
    
    switch (type) {
      case 'conversion':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'upload':
        return <Upload className="h-4 w-4 text-blue-500" />;
      case 'download':
        return <Download className="h-4 w-4 text-indigo-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      completed: { variant: 'success' as const, label: 'Completed' },
      processing: { variant: 'warning' as const, label: 'Processing' },
      failed: { variant: 'destructive' as const, label: 'Failed' },
      pending: { variant: 'secondary' as const, label: 'Pending' }
    };

    const config = statusConfig[status as keyof typeof statusConfig];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getCurrentPeriodConversions = () => {
    switch (selectedPeriod) {
      case 'today':
        return stats.todayConversions;
      case 'week':
        return stats.weeklyConversions;
      case 'month':
        return stats.monthlyConversions;
      default:
        return stats.monthlyConversions;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {user?.name || 'User'}! 👋
            </h1>
            <p className="text-gray-600 mt-1">
              Here's what's happening with your document conversions today.
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
              leftIcon={<RefreshCw className={cn('h-4 w-4', refreshing && 'animate-spin')} />}
            >
              Refresh
            </Button>
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="h-4 w-4" />}
            >
              New Conversion
            </Button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Conversions</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalConversions.toLocaleString()}</p>
                <p className="text-xs text-green-600 mt-1">↗ 12% from last month</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-gray-900">{stats.successRate}%</p>
                <p className="text-xs text-green-600 mt-1">↗ 2% improvement</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg. Processing</p>
                <p className="text-2xl font-bold text-gray-900">{stats.avgProcessingTime}s</p>
                <p className="text-xs text-green-600 mt-1">↘ 0.5s faster</p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-full">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Data Processed</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalSizeProcessed}</p>
                <p className="text-xs text-green-600 mt-1">↗ 8% this month</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Quick Actions</h2>
                <Link to="/convert" className="text-sm text-brand-600 hover:text-brand-700 font-medium">
                  View all →
                </Link>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {quickActions.map((action) => (
                  <Link
                    key={action.id}
                    to={action.href}
                    className="group relative p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-md transition-all duration-200"
                  >
                    {action.popular && (
                      <div className="absolute -top-2 -right-2">
                        <Badge variant="warning" className="text-xs">
                          <Star className="h-3 w-3 mr-1" />
                          Popular
                        </Badge>
                      </div>
                    )}
                    <div className="flex items-start space-x-3">
                      <div className={cn('p-2 rounded-lg', action.color)}>
                        <div className="text-white">
                          {action.icon}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-gray-900 group-hover:text-brand-600 transition-colors">
                          {action.title}
                        </h3>
                        <p className="text-sm text-gray-500 mt-1">{action.description}</p>
                      </div>
                      <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-gray-600 transition-colors" />
                    </div>
                  </Link>
                ))}
              </div>
            </Card>
          </div>

          {/* Period Selector */}
          <div className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                {selectedPeriod.charAt(0).toUpperCase() + selectedPeriod.slice(1)} Overview
              </h2>
              
              <div className="flex space-x-1 mb-4">
                {(['today', 'week', 'month'] as const).map((period) => (
                  <button
                    key={period}
                    onClick={() => setSelectedPeriod(period)}
                    className={cn(
                      'px-3 py-1 text-sm font-medium rounded-md transition-colors',
                      selectedPeriod === period
                        ? 'bg-brand-100 text-brand-700'
                        : 'text-gray-500 hover:text-gray-700'
                    )}
                  >
                    {period.charAt(0).toUpperCase() + period.slice(1)}
                  </button>
                ))}
              </div>

              <div className="text-center">
                <p className="text-3xl font-bold text-gray-900 mb-2">
                  {getCurrentPeriodConversions()}
                </p>
                <p className="text-sm text-gray-600">
                  Conversions {selectedPeriod === 'today' ? 'today' : `this ${selectedPeriod}`}
                </p>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Target:</span>
                  <span className="font-medium">100/{selectedPeriod}</span>
                </div>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-brand-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min((getCurrentPeriodConversions() / 100) * 100, 100)}%` }}
                  />
                </div>
              </div>
            </Card>

            {/* Upgrade Banner */}
            <Card className="p-6 bg-gradient-to-br from-brand-50 to-brand-100 border-brand-200">
              <div className="text-center">
                <div className="p-2 bg-brand-600 rounded-full w-fit mx-auto mb-3">
                  <Zap className="h-5 w-5 text-white" />
                </div>
                <h3 className="font-semibold text-brand-900 mb-2">Upgrade to Pro</h3>
                <p className="text-sm text-brand-700 mb-4">
                  Get unlimited conversions, priority processing, and advanced features.
                </p>
                <Button size="sm" className="w-full">
                  Upgrade Now
                </Button>
              </div>
            </Card>
          </div>
        </div>

        {/* Recent Activity */}
        <Card className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
            <div className="flex items-center space-x-3">
              <Button variant="outline" size="sm" leftIcon={<Filter className="h-4 w-4" />}>
                Filter
              </Button>
              <Link to="/history" className="text-sm text-brand-600 hover:text-brand-700 font-medium">
                View all →
              </Link>
            </div>
          </div>
          
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div
                key={activity.id}
                className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <div className="flex items-center space-x-3">
                  {getActivityIcon(activity.type, activity.status)}
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-gray-900">{activity.title}</p>
                    <p className="text-sm text-gray-500">{activity.description}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4 text-right">
                  <div className="text-sm text-gray-500">
                    <div className="flex items-center space-x-2">
                      {activity.size && (
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                          {activity.size}
                        </span>
                      )}
                      {getStatusBadge(activity.status)}
                    </div>
                    <p className="mt-1">{activity.timestamp}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {recentActivity.length === 0 && (
            <div className="text-center py-12">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No recent activity</p>
              <p className="text-sm text-gray-400 mt-1">
                Your conversions will appear here once you start using Kanvert
              </p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;