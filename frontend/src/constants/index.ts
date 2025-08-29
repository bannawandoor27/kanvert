// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const API_PREFIX = '/api/v1';
export const API_TIMEOUT = 30000; // 30 seconds

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication endpoints
  AUTH_REGISTER: `${API_PREFIX}/auth/register`,
  AUTH_LOGIN: `${API_PREFIX}/auth/login`,
  AUTH_PASSWORD_RESET: `${API_PREFIX}/auth/password-reset`,
  AUTH_PASSWORD_RESET_CONFIRM: `${API_PREFIX}/auth/password-reset/confirm`,
  AUTH_ME: `${API_PREFIX}/auth/me`,
  AUTH_VALIDATE_TOKEN: `${API_PREFIX}/auth/validate-token`,
  AUTH_REFRESH_API_KEY: `${API_PREFIX}/auth/refresh-api-key`,

  // Conversion endpoints
  CONVERT_MARKDOWN_TO_PDF: `${API_PREFIX}/convert/markdown-to-pdf`,
  CONVERT_HTML_TO_PDF: `${API_PREFIX}/convert/html-to-pdf`,
  CONVERT_DOCX_TO_PDF: `${API_PREFIX}/convert/docx-to-pdf`,
  CONVERT_OFFICE_TO_PDF: `${API_PREFIX}/convert/office-to-pdf`,
  CONVERT_GENERIC: `${API_PREFIX}/convert/`,
  
  // Comparison endpoints
  COMPARE_DOCX: `${API_PREFIX}/convert/docx-compare`,
  
  // Dashboard endpoints
  DASHBOARD_SUMMARY: `${API_PREFIX}/dashboard/summary`,
  DASHBOARD_ANALYTICS: `${API_PREFIX}/dashboard/analytics`,
  DASHBOARD_SYSTEM_STATUS: `${API_PREFIX}/dashboard/system-status`,

  // Advanced endpoints
  BATCH_JOBS: `${API_PREFIX}/advanced/batch-jobs`,
  BATCH_JOB_FILES: (jobId: string) => `${API_PREFIX}/advanced/batch-jobs/${jobId}/files`,
  BATCH_JOB_START: (jobId: string) => `${API_PREFIX}/advanced/batch-jobs/${jobId}/start`,
  BATCH_JOB_PAUSE: (jobId: string) => `${API_PREFIX}/advanced/batch-jobs/${jobId}/pause`,
  BATCH_JOB_CANCEL: (jobId: string) => `${API_PREFIX}/advanced/batch-jobs/${jobId}/cancel`,
  CONVERSION_TEMPLATES: `${API_PREFIX}/advanced/templates`,
  SCHEDULED_JOBS: `${API_PREFIX}/advanced/scheduled-jobs`,

  // Settings endpoints
  SETTINGS_PROFILE: `${API_PREFIX}/settings/profile`,
  SETTINGS_NOTIFICATIONS: `${API_PREFIX}/settings/notifications`,
  SETTINGS_CONVERSION_DEFAULTS: `${API_PREFIX}/settings/conversion-defaults`,
  SETTINGS_PASSWORD_CHANGE: `${API_PREFIX}/settings/password-change`,
  SETTINGS_API_KEYS: `${API_PREFIX}/settings/api-keys`,
  SETTINGS_API_KEY_REVOKE: (keyId: string) => `${API_PREFIX}/settings/api-keys/${keyId}`,
  SETTINGS_USAGE_STATS: `${API_PREFIX}/settings/usage-stats`,
  SETTINGS_ALL: `${API_PREFIX}/settings/`,

  // History endpoints
  HISTORY: `${API_PREFIX}/history/`,
  HISTORY_ITEM: (conversionId: string) => `${API_PREFIX}/history/${conversionId}`,
  HISTORY_BULK_ACTION: `${API_PREFIX}/history/bulk-action`,
  HISTORY_STATS_SUMMARY: `${API_PREFIX}/history/stats/summary`,
  HISTORY_STATS_DAILY: `${API_PREFIX}/history/stats/daily`,
  HISTORY_EXPORT: `${API_PREFIX}/history/export`,
  
  // System endpoints
  HEALTH: '/health',
  CONVERSION_HEALTH: `${API_PREFIX}/convert/health`,
  SUPPORTED_FORMATS: `${API_PREFIX}/convert/formats`,
  CONVERTERS: `${API_PREFIX}/convert/converters`,
  
  // MCP endpoints
  MCP_CALL: `${API_PREFIX}/mcp/call`,
  MCP_CAPABILITIES: `${API_PREFIX}/mcp/capabilities`,
} as const;

// File Size Limits (in bytes)
export const FILE_SIZE_LIMITS = {
  FREE: 5 * 1024 * 1024, // 5MB
  PROFESSIONAL: 50 * 1024 * 1024, // 50MB
  ENTERPRISE: 200 * 1024 * 1024, // 200MB
} as const;

// Supported File Types
export const SUPPORTED_FILE_TYPES = {
  MARKDOWN: ['.md', '.markdown', '.mdown', '.mkd'],
  HTML: ['.html', '.htm'],
  DOCX: ['.docx'],
  OFFICE: ['.xlsx', '.xls', '.xlsm', '.pptx', '.ppt', '.pptm', '.ods', '.odp', '.odt'],
  TEXT: ['.txt'],
  PDF: ['.pdf'],
} as const;

// Conversion Formats
export const CONVERSION_FORMATS = {
  'markdown-to-pdf': {
    name: 'Markdown to PDF',
    description: 'Convert Markdown documents to professional PDF files',
    inputFormats: SUPPORTED_FILE_TYPES.MARKDOWN,
    outputFormat: 'PDF',
    icon: 'FileText',
    color: 'blue',
  },
  'html-to-pdf': {
    name: 'HTML to PDF',
    description: 'Convert HTML pages to PDF using Chrome browser engine',
    inputFormats: SUPPORTED_FILE_TYPES.HTML,
    outputFormat: 'PDF',
    icon: 'Globe',
    color: 'green',
  },
  'docx-to-pdf': {
    name: 'DOCX to PDF',
    description: 'Convert Word documents to PDF while preserving formatting',
    inputFormats: SUPPORTED_FILE_TYPES.DOCX,
    outputFormat: 'PDF',
    icon: 'FileText',
    color: 'purple',
  },
  'office-to-pdf': {
    name: 'Office to PDF',
    description: 'Convert Excel, PowerPoint, and other Office documents to PDF',
    inputFormats: SUPPORTED_FILE_TYPES.OFFICE,
    outputFormat: 'PDF',
    icon: 'BarChart3',
    color: 'orange',
  },
  'docx-compare': {
    name: 'DOCX Compare',
    description: 'Compare two Word documents for differences',
    inputFormats: SUPPORTED_FILE_TYPES.DOCX,
    outputFormat: 'COMPARISON',
    icon: 'GitCompare',
    color: 'red',
  },
} as const;

// Subscription Plans
export const SUBSCRIPTION_PLANS = {
  FREE: {
    id: 'free',
    name: 'Free',
    price: 0,
    currency: 'USD',
    billing_period: 'monthly' as const,
    features: [
      'Up to 10 conversions per month',
      'Maximum 5MB file size',
      'Basic conversion formats',
      'Standard processing speed',
      'Community support',
    ],
    limits: {
      conversions_per_month: 10,
      max_file_size: FILE_SIZE_LIMITS.FREE,
      batch_processing: false,
      api_access: false,
      priority_support: false,
    },
  },
  PROFESSIONAL: {
    id: 'professional',
    name: 'Professional',
    price: 19,
    currency: 'USD',
    billing_period: 'monthly' as const,
    features: [
      'Up to 1,000 conversions per month',
      'Maximum 50MB file size',
      'All conversion formats',
      'Batch processing',
      'API access',
      'Priority processing',
      'Email support',
    ],
    limits: {
      conversions_per_month: 1000,
      max_file_size: FILE_SIZE_LIMITS.PROFESSIONAL,
      batch_processing: true,
      api_access: true,
      priority_support: false,
    },
  },
  ENTERPRISE: {
    id: 'enterprise',
    name: 'Enterprise',
    price: 99,
    currency: 'USD',
    billing_period: 'monthly' as const,
    features: [
      'Unlimited conversions',
      'Maximum 200MB file size',
      'All conversion formats',
      'Advanced batch processing',
      'Full API access',
      'Highest priority processing',
      'Dedicated support',
      'Custom integrations',
      'SLA guarantee',
    ],
    limits: {
      conversions_per_month: -1, // Unlimited
      max_file_size: FILE_SIZE_LIMITS.ENTERPRISE,
      batch_processing: true,
      api_access: true,
      priority_support: true,
    },
  },
} as const;

// Navigation Links
export const NAVIGATION_LINKS = {
  PUBLIC: [
    { name: 'Home', href: '/', icon: 'Home' },
    { name: 'Features', href: '/#features', icon: 'Zap' },
    { name: 'Pricing', href: '/#pricing', icon: 'DollarSign' },
    { name: 'API Docs', href: '/docs', icon: 'Book' },
  ],
  AUTHENTICATED: [
    { name: 'Dashboard', href: '/dashboard', icon: 'LayoutDashboard' },
    { name: 'Convert', href: '/convert', icon: 'FileText' },
    { name: 'Advanced', href: '/advanced', icon: 'Zap' },
    { name: 'History', href: '/history', icon: 'Clock' },
    { name: 'Analytics', href: '/analytics', icon: 'BarChart3' },
    { name: 'Settings', href: '/settings', icon: 'Settings' },
  ],
} as const;

// Theme Configuration
export const THEME = {
  COLORS: {
    BRAND: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e',
      950: '#082f49',
    },
  },
  ANIMATIONS: {
    TRANSITION: 'all 0.2s ease-in-out',
    HOVER_SCALE: 'scale(1.02)',
    BOUNCE: 'bounce 0.6s ease-in-out',
  },
} as const;

// Local Storage Keys
export const STORAGE_KEYS = {
  USER: 'kanvert_user',
  AUTH_TOKEN: 'kanvert_auth_token',
  API_KEY: 'kanvert_api_key',
  THEME: 'kanvert_theme',
  PREFERENCES: 'kanvert_preferences',
  CONVERSION_HISTORY: 'kanvert_conversion_history',
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  FILE_TOO_LARGE: 'File size exceeds the maximum limit for your subscription plan',
  UNSUPPORTED_FORMAT: 'This file format is not supported',
  CONVERSION_FAILED: 'Conversion failed. Please try again or contact support',
  NETWORK_ERROR: 'Network error. Please check your connection and try again',
  UNAUTHORIZED: 'Authentication required. Please log in to continue',
  QUOTA_EXCEEDED: 'You have exceeded your monthly conversion quota',
  INVALID_FILE: 'Invalid file. Please select a valid file to convert',
} as const;

// Success Messages
export const SUCCESS_MESSAGES = {
  CONVERSION_STARTED: 'Conversion started successfully',
  CONVERSION_COMPLETED: 'Conversion completed successfully',
  FILE_UPLOADED: 'File uploaded successfully',
  SETTINGS_SAVED: 'Settings saved successfully',
  PASSWORD_CHANGED: 'Password changed successfully',
} as const;