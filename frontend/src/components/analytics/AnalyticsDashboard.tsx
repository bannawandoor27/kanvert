import React, { useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  TrendingUp,
  TrendingDown,
  Users,
  FileText,
  Clock,
  Download,
  DollarSign,
  Activity,
  BarChart3,
  PieChart,
  Target,
  Zap,
  AlertCircle,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, Button, Badge } from '../common';
import { format, subDays, subMonths } from 'date-fns';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface AnalyticsData {
  conversions: {
    total: number;
    completed: number;
    failed: number;
    inProgress: number;
  };
  usage: {
    totalFileSize: number;
    avgConversionTime: number;
    totalUsers: number;
    activeUsers: number;
  };
  revenue: {
    currentMonth: number;
    previousMonth: number;
    growth: number;
  };
  topFormats: Array<{
    format: string;
    count: number;
    percentage: number;
  }>;
  dailyStats: Array<{
    date: string;
    conversions: number;
    users: number;
    revenue: number;
  }>;
  weeklyStats: Array<{
    week: string;
    conversions: number;
    successRate: number;
  }>;
  monthlyStats: Array<{
    month: string;
    conversions: number;
    revenue: number;
    users: number;
  }>;
}

// Mock analytics data
const mockAnalyticsData: AnalyticsData = {
  conversions: {
    total: 15847,
    completed: 14523,
    failed: 892,
    inProgress: 432,
  },
  usage: {
    totalFileSize: 2.4 * 1024 * 1024 * 1024, // 2.4GB
    avgConversionTime: 3.2,
    totalUsers: 1247,
    activeUsers: 847,
  },
  revenue: {
    currentMonth: 24560,
    previousMonth: 21340,
    growth: 15.1,
  },
  topFormats: [
    { format: 'PDF to DOCX', count: 4521, percentage: 28.5 },
    { format: 'DOCX to PDF', count: 3847, percentage: 24.3 },
    { format: 'HTML to PDF', count: 2314, percentage: 14.6 },
    { format: 'Excel to PDF', count: 1892, percentage: 11.9 },
    { format: 'PowerPoint to PDF', count: 1456, percentage: 9.2 },
    { format: 'Markdown to PDF', count: 1817, percentage: 11.5 },
  ],
  dailyStats: Array.from({ length: 30 }, (_, i) => ({
    date: format(subDays(new Date(), 29 - i), 'MMM dd'),
    conversions: Math.floor(Math.random() * 200) + 100,
    users: Math.floor(Math.random() * 50) + 25,
    revenue: Math.floor(Math.random() * 1000) + 500,
  })),
  weeklyStats: Array.from({ length: 12 }, (_, i) => ({
    week: `Week ${i + 1}`,
    conversions: Math.floor(Math.random() * 1000) + 500,
    successRate: Math.floor(Math.random() * 20) + 80,
  })),
  monthlyStats: Array.from({ length: 12 }, (_, i) => ({
    month: format(subMonths(new Date(), 11 - i), 'MMM yyyy'),
    conversions: Math.floor(Math.random() * 3000) + 1000,
    revenue: Math.floor(Math.random() * 10000) + 5000,
    users: Math.floor(Math.random() * 200) + 100,
  })),
};

type TimeRange = 'today' | 'week' | 'month' | 'quarter' | 'year';

const AnalyticsDashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState<TimeRange>('month');
  const [activeTab, setActiveTab] = useState<'overview' | 'conversions' | 'users' | 'revenue'>('overview');

  const analyticsData = mockAnalyticsData;

  // Chart configurations
  const lineChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right' as const,
      },
    },
  };

  // Line chart data for conversions over time
  const conversionsLineData = {
    labels: analyticsData.dailyStats.map(stat => stat.date),
    datasets: [
      {
        label: 'Conversions',
        data: analyticsData.dailyStats.map(stat => stat.conversions),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.3,
      },
      {
        label: 'Active Users',
        data: analyticsData.dailyStats.map(stat => stat.users),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.3,
      },
    ],
  };

  // Bar chart data for revenue
  const revenueBarData = {
    labels: analyticsData.monthlyStats.map(stat => stat.month),
    datasets: [
      {
        label: 'Revenue ($)',
        data: analyticsData.monthlyStats.map(stat => stat.revenue),
        backgroundColor: 'rgba(139, 92, 246, 0.8)',
        borderColor: 'rgb(139, 92, 246)',
        borderWidth: 1,
      },
    ],
  };

  // Doughnut chart data for top formats
  const formatDistributionData = {
    labels: analyticsData.topFormats.map(format => format.format),
    datasets: [
      {
        data: analyticsData.topFormats.map(format => format.count),
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(139, 92, 246, 0.8)',
          'rgba(236, 72, 153, 0.8)',
        ],
        borderColor: [
          'rgb(239, 68, 68)',
          'rgb(245, 158, 11)',
          'rgb(34, 197, 94)',
          'rgb(59, 130, 246)',
          'rgb(139, 92, 246)',
          'rgb(236, 72, 153)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const StatCard = ({ 
    title, 
    value, 
    change, 
    icon: Icon, 
    color = 'blue' 
  }: { 
    title: string; 
    value: string | number; 
    change?: { value: number; type: 'positive' | 'negative' }; 
    icon: React.ElementType; 
    color?: string; 
  }) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
            {change && (
              <div className={`flex items-center mt-2 text-sm ${
                change.type === 'positive' ? 'text-green-600' : 'text-red-600'
              }`}>
                {change.type === 'positive' ? (
                  <TrendingUp className="h-4 w-4 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 mr-1" />
                )}
                {Math.abs(change.value)}%
              </div>
            )}
          </div>
          <div className={`p-3 rounded-lg bg-${color}-100`}>
            <Icon className={`h-6 w-6 text-${color}-600`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Monitor your conversion platform performance and usage statistics</p>
        </div>
        
        <div className="flex items-center space-x-4 mt-4 sm:mt-0">
          {/* Time Range Selector */}
          <div className="flex items-center space-x-2 bg-white border border-gray-200 rounded-lg p-1">
            {(['today', 'week', 'month', 'quarter', 'year'] as TimeRange[]).map((range) => (
              <Button
                key={range}
                variant={timeRange === range ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setTimeRange(range)}
                className="capitalize"
              >
                {range}
              </Button>
            ))}
          </div>
          
          <Button variant="outline" size="sm" rightIcon={<Download className="h-4 w-4" />}>
            Export Report
          </Button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'overview', label: 'Overview', icon: BarChart3 },
          { id: 'conversions', label: 'Conversions', icon: FileText },
          { id: 'users', label: 'Users', icon: Users },
          { id: 'revenue', label: 'Revenue', icon: DollarSign },
        ].map((tab) => (
          <Button
            key={tab.id}
            variant={activeTab === tab.id ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab(tab.id as typeof activeTab)}
            rightIcon={<tab.icon className="h-4 w-4" />}
            className="flex-1 justify-center"
          >
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Conversions"
              value={analyticsData.conversions.total.toLocaleString()}
              change={{ value: 12.5, type: 'positive' }}
              icon={FileText}
              color="blue"
            />
            <StatCard
              title="Active Users"
              value={analyticsData.usage.activeUsers.toLocaleString()}
              change={{ value: 8.2, type: 'positive' }}
              icon={Users}
              color="green"
            />
            <StatCard
              title="Success Rate"
              value={`${((analyticsData.conversions.completed / analyticsData.conversions.total) * 100).toFixed(1)}%`}
              change={{ value: 2.1, type: 'positive' }}
              icon={Target}
              color="purple"
            />
            <StatCard
              title="Monthly Revenue"
              value={`$${analyticsData.revenue.currentMonth.toLocaleString()}`}
              change={{ value: analyticsData.revenue.growth, type: 'positive' }}
              icon={DollarSign}
              color="yellow"
            />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="h-5 w-5" />
                  <span>Conversion Trends</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Line options={lineChartOptions} data={conversionsLineData} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <PieChart className="h-5 w-5" />
                  <span>Popular Formats</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Doughnut options={doughnutOptions} data={formatDistributionData} />
              </CardContent>
            </Card>
          </div>

          {/* Performance Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>System Performance</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Avg. Conversion Time</span>
                  <span className="font-medium">{analyticsData.usage.avgConversionTime}s</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total File Size</span>
                  <span className="font-medium">{formatBytes(analyticsData.usage.totalFileSize)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Failed Conversions</span>
                  <Badge variant="warning">{analyticsData.conversions.failed}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">In Progress</span>
                  <Badge variant="info">{analyticsData.conversions.inProgress}</Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Conversion Types</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analyticsData.topFormats.slice(0, 5).map((format, index) => (
                    <div key={format.format} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900">
                          {index + 1}. {format.format}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-600">{format.count}</span>
                        <Badge variant="secondary">{format.percentage}%</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">1,247 conversions completed</p>
                      <p className="text-xs text-gray-500">in the last 24 hours</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">342 new users registered</p>
                      <p className="text-xs text-gray-500">this week</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">System maintenance scheduled</p>
                      <p className="text-xs text-gray-500">for tonight at 2 AM UTC</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">API rate limit increased</p>
                      <p className="text-xs text-gray-500">to 1000 req/min for Pro users</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}

      {/* Conversions Tab */}
      {activeTab === 'conversions' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatCard
              title="Successful Conversions"
              value={analyticsData.conversions.completed.toLocaleString()}
              change={{ value: 15.2, type: 'positive' }}
              icon={Zap}
              color="green"
            />
            <StatCard
              title="Failed Conversions"
              value={analyticsData.conversions.failed.toLocaleString()}
              change={{ value: 3.1, type: 'negative' }}
              icon={AlertCircle}
              color="red"
            />
            <StatCard
              title="In Progress"
              value={analyticsData.conversions.inProgress.toLocaleString()}
              icon={Clock}
              color="blue"
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Weekly Conversion Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <Bar
                options={barChartOptions}
                data={{
                  labels: analyticsData.weeklyStats.map(stat => stat.week),
                  datasets: [
                    {
                      label: 'Conversions',
                      data: analyticsData.weeklyStats.map(stat => stat.conversions),
                      backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    },
                  ],
                }}
              />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Revenue Tab */}
      {activeTab === 'revenue' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Monthly Revenue Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <Bar options={barChartOptions} data={revenueBarData} />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;