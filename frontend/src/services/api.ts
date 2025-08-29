import { apiRequest, apiClient } from '../utils';
import { API_ENDPOINTS } from '../constants';
import type {
  User,
  LoginRequest,
  RegisterRequest,
  PasswordResetRequest,
  UserUpdate,
  DashboardSummary,
  AnalyticsData,
  BatchJob,
  ConversionTemplate,
  ScheduledJob,
  UserProfile,
  NotificationSettings,
  ConversionDefaults,
  ConversionHistoryResponse,
  ConversionHistoryItem,
  APIKeyInfo,
  PasswordChangeRequest,
  BulkActionRequest,
  ConversionFilters,
} from '../types';

// Authentication API
export const authApi = {
  register: async (data: RegisterRequest) => {
    return apiRequest('POST', API_ENDPOINTS.AUTH_REGISTER, data);
  },

  login: async (data: LoginRequest) => {
    return apiRequest('POST', API_ENDPOINTS.AUTH_LOGIN, data);
  },

  requestPasswordReset: async (data: PasswordResetRequest) => {
    return apiRequest('POST', API_ENDPOINTS.AUTH_PASSWORD_RESET, data);
  },

  confirmPasswordReset: async (data: { email: string; token: string; new_password: string }) => {
    return apiRequest('POST', API_ENDPOINTS.AUTH_PASSWORD_RESET_CONFIRM, data);
  },

  getCurrentUser: async () => {
    return apiRequest<User>('GET', API_ENDPOINTS.AUTH_ME);
  },

  updateCurrentUser: async (data: UserUpdate) => {
    return apiRequest<User>('PUT', API_ENDPOINTS.AUTH_ME, data);
  },

  validateToken: async () => {
    return apiRequest('POST', API_ENDPOINTS.AUTH_VALIDATE_TOKEN);
  },

  refreshApiKey: async () => {
    return apiRequest('POST', API_ENDPOINTS.AUTH_REFRESH_API_KEY);
  },
};

// Dashboard API
export const dashboardApi = {
  getSummary: async (period: 'today' | 'week' | 'month' = 'month') => {
    return apiRequest<DashboardSummary>('GET', `${API_ENDPOINTS.DASHBOARD_SUMMARY}?period=${period}`);
  },

  getAnalytics: async (timeRange: 'today' | 'week' | 'month' | 'quarter' | 'year' = 'month') => {
    return apiRequest<AnalyticsData>('GET', `${API_ENDPOINTS.DASHBOARD_ANALYTICS}?time_range=${timeRange}`);
  },

  getSystemStatus: async () => {
    return apiRequest('GET', API_ENDPOINTS.DASHBOARD_SYSTEM_STATUS);
  },
};

// Advanced Features API
export const advancedApi = {
  // Batch Jobs
  createBatchJob: async (data: { name: string; options: any }) => {
    return apiRequest<BatchJob>('POST', API_ENDPOINTS.BATCH_JOBS, data);
  },

  getBatchJobs: async (limit = 20, offset = 0) => {
    return apiRequest<BatchJob[]>('GET', `${API_ENDPOINTS.BATCH_JOBS}?limit=${limit}&offset=${offset}`);
  },

  getBatchJob: async (jobId: string) => {
    return apiRequest<BatchJob>('GET', `${API_ENDPOINTS.BATCH_JOBS}/${jobId}`);
  },

  addFilesToBatchJob: async (jobId: string, files: File[]) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    return apiClient.post(API_ENDPOINTS.BATCH_JOB_FILES(jobId), formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  startBatchJob: async (jobId: string) => {
    return apiRequest('POST', API_ENDPOINTS.BATCH_JOB_START(jobId));
  },

  pauseBatchJob: async (jobId: string) => {
    return apiRequest('POST', API_ENDPOINTS.BATCH_JOB_PAUSE(jobId));
  },

  cancelBatchJob: async (jobId: string) => {
    return apiRequest('POST', API_ENDPOINTS.BATCH_JOB_CANCEL(jobId));
  },

  // Templates
  getTemplates: async () => {
    return apiRequest<ConversionTemplate[]>('GET', API_ENDPOINTS.CONVERSION_TEMPLATES);
  },

  createTemplate: async (data: {
    name: string;
    description: string;
    input_format: string;
    output_format: string;
    options: any;
  }) => {
    return apiRequest<ConversionTemplate>('POST', API_ENDPOINTS.CONVERSION_TEMPLATES, data);
  },

  updateTemplate: async (templateId: string, data: Partial<ConversionTemplate>) => {
    return apiRequest<ConversionTemplate>('PUT', `${API_ENDPOINTS.CONVERSION_TEMPLATES}/${templateId}`, data);
  },

  deleteTemplate: async (templateId: string) => {
    return apiRequest('DELETE', `${API_ENDPOINTS.CONVERSION_TEMPLATES}/${templateId}`);
  },

  // Scheduled Jobs
  getScheduledJobs: async () => {
    return apiRequest<ScheduledJob[]>('GET', API_ENDPOINTS.SCHEDULED_JOBS);
  },

  createScheduledJob: async (data: {
    name: string;
    template_id: string;
    schedule_type: string;
    schedule_time: string;
    options: any;
  }) => {
    return apiRequest<ScheduledJob>('POST', API_ENDPOINTS.SCHEDULED_JOBS, data);
  },

  updateScheduledJob: async (jobId: string, data: Partial<ScheduledJob>) => {
    return apiRequest<ScheduledJob>('PUT', `${API_ENDPOINTS.SCHEDULED_JOBS}/${jobId}`, data);
  },

  deleteScheduledJob: async (jobId: string) => {
    return apiRequest('DELETE', `${API_ENDPOINTS.SCHEDULED_JOBS}/${jobId}`);
  },
};

// Settings API
export const settingsApi = {
  // Profile
  getProfile: async () => {
    return apiRequest<UserProfile>('GET', API_ENDPOINTS.SETTINGS_PROFILE);
  },

  updateProfile: async (data: UserProfile) => {
    return apiRequest('PUT', API_ENDPOINTS.SETTINGS_PROFILE, data);
  },

  // Notifications
  getNotificationSettings: async () => {
    return apiRequest<NotificationSettings>('GET', API_ENDPOINTS.SETTINGS_NOTIFICATIONS);
  },

  updateNotificationSettings: async (data: NotificationSettings) => {
    return apiRequest('PUT', API_ENDPOINTS.SETTINGS_NOTIFICATIONS, data);
  },

  // Conversion Defaults
  getConversionDefaults: async () => {
    return apiRequest<ConversionDefaults>('GET', API_ENDPOINTS.SETTINGS_CONVERSION_DEFAULTS);
  },

  updateConversionDefaults: async (data: ConversionDefaults) => {
    return apiRequest('PUT', API_ENDPOINTS.SETTINGS_CONVERSION_DEFAULTS, data);
  },

  // Password
  changePassword: async (data: PasswordChangeRequest) => {
    return apiRequest('POST', API_ENDPOINTS.SETTINGS_PASSWORD_CHANGE, data);
  },

  // API Keys
  getApiKeys: async () => {
    return apiRequest<APIKeyInfo[]>('GET', API_ENDPOINTS.SETTINGS_API_KEYS);
  },

  createApiKey: async (data: { name: string; permissions: string[] }) => {
    return apiRequest('POST', API_ENDPOINTS.SETTINGS_API_KEYS, data);
  },

  revokeApiKey: async (keyId: string) => {
    return apiRequest('DELETE', API_ENDPOINTS.SETTINGS_API_KEY_REVOKE(keyId));
  },

  // Usage Stats
  getUsageStats: async () => {
    return apiRequest('GET', API_ENDPOINTS.SETTINGS_USAGE_STATS);
  },

  // All Settings
  getAllSettings: async () => {
    return apiRequest('GET', API_ENDPOINTS.SETTINGS_ALL);
  },
};

// History API
export const historyApi = {
  getHistory: async (params: {
    page?: number;
    per_page?: number;
    search?: string;
    status?: string;
    format?: string;
    start_date?: string;
    end_date?: string;
    sort_field?: string;
    sort_order?: 'asc' | 'desc';
  } = {}) => {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
    
    const url = searchParams.toString() 
      ? `${API_ENDPOINTS.HISTORY}?${searchParams.toString()}`
      : API_ENDPOINTS.HISTORY;
    
    return apiRequest<ConversionHistoryResponse>('GET', url);
  },

  getConversionDetails: async (conversionId: string) => {
    return apiRequest<ConversionHistoryItem>('GET', API_ENDPOINTS.HISTORY_ITEM(conversionId));
  },

  deleteConversion: async (conversionId: string) => {
    return apiRequest('DELETE', API_ENDPOINTS.HISTORY_ITEM(conversionId));
  },

  bulkAction: async (data: BulkActionRequest) => {
    return apiRequest('POST', API_ENDPOINTS.HISTORY_BULK_ACTION, data);
  },

  getHistoryStats: async (days = 30) => {
    return apiRequest('GET', `${API_ENDPOINTS.HISTORY_STATS_SUMMARY}?days=${days}`);
  },

  getDailyStats: async (days = 30) => {
    return apiRequest('GET', `${API_ENDPOINTS.HISTORY_STATS_DAILY}?days=${days}`);
  },

  exportHistory: async (filters?: ConversionFilters, format: 'csv' | 'json' = 'csv') => {
    return apiRequest('POST', `${API_ENDPOINTS.HISTORY_EXPORT}?format=${format}`, filters);
  },
};

// System API
export const systemApi = {
  getHealth: async () => {
    return apiRequest('GET', API_ENDPOINTS.HEALTH);
  },

  getConversionHealth: async () => {
    return apiRequest('GET', API_ENDPOINTS.CONVERSION_HEALTH);
  },

  getSupportedFormats: async () => {
    return apiRequest('GET', API_ENDPOINTS.SUPPORTED_FORMATS);
  },

  getConverters: async () => {
    return apiRequest('GET', API_ENDPOINTS.CONVERTERS);
  },
};

// Export all APIs
export const api = {
  auth: authApi,
  dashboard: dashboardApi,
  advanced: advancedApi,
  settings: settingsApi,
  history: historyApi,
  system: systemApi,
};

export default api;