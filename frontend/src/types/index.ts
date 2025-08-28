// Core conversion types
export interface ConversionRequest {
  content: string;
  output_format: ConversionFormat;
  options?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface ConversionResponse {
  job_id: string;
  status: ConversionStatus;
  message?: string;
  download_url?: string;
  metadata?: Record<string, any>;
  output_data?: Uint8Array;
  output_filename?: string;
  created_at?: string;
  completed_at?: string;
  processing_time?: number;
}

export interface ComparisonRequest {
  document_1: string;
  document_2: string;
  comparison_type: 'content' | 'formatting' | 'both';
  options?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface ComparisonResponse {
  job_id: string;
  status: ConversionStatus;
  differences_found: boolean;
  similarity_score: number;
  summary: string;
  content_differences: any[];
  formatting_differences: any[];
  detailed_report: string;
  metadata?: Record<string, any>;
  processing_time?: number;
}

export interface OfficeConversionRequest {
  content: string;
  input_format: string;
  output_format: ConversionFormat;
  options?: Record<string, any>;
  metadata?: Record<string, any>;
}

export enum ConversionFormat {\n  PDF = 'PDF',\n  HTML = 'HTML',\n  DOCX = 'DOCX',\n  MARKDOWN = 'MARKDOWN',\n  TEXT = 'TEXT'\n}\n\nexport enum ConversionStatus {\n  PENDING = 'PENDING',\n  IN_PROGRESS = 'IN_PROGRESS',\n  COMPLETED = 'COMPLETED',\n  FAILED = 'FAILED',\n  CANCELLED = 'CANCELLED'\n}\n\n// UI and application types\nexport interface User {\n  id: string;\n  email: string;\n  name: string;\n  avatar?: string;\n  subscription: SubscriptionTier;\n  api_key?: string;\n  created_at: string;\n  last_login?: string;\n}\n\nexport enum SubscriptionTier {\n  FREE = 'FREE',\n  PROFESSIONAL = 'PROFESSIONAL',\n  ENTERPRISE = 'ENTERPRISE'\n}\n\nexport interface SubscriptionPlan {\n  id: string;\n  name: string;\n  tier: SubscriptionTier;\n  price: number;\n  currency: string;\n  billing_period: 'monthly' | 'yearly';\n  features: string[];\n  limits: {\n    conversions_per_month: number;\n    max_file_size: number;\n    batch_processing: boolean;\n    api_access: boolean;\n    priority_support: boolean;\n  };\n}\n\nexport interface ConversionHistory {\n  id: string;\n  job_id: string;\n  input_format: string;\n  output_format: string;\n  file_name: string;\n  file_size: number;\n  status: ConversionStatus;\n  created_at: string;\n  completed_at?: string;\n  processing_time?: number;\n  download_url?: string;\n  error_message?: string;\n}\n\nexport interface UsageStats {\n  total_conversions: number;\n  successful_conversions: number;\n  failed_conversions: number;\n  total_file_size: number;\n  conversions_this_month: number;\n  most_used_format: string;\n  average_processing_time: number;\n}\n\nexport interface ApiResponse<T = any> {\n  data?: T;\n  error?: string;\n  message?: string;\n  status: number;\n}\n\nexport interface FileUpload {\n  file: File;\n  id: string;\n  name: string;\n  size: number;\n  type: string;\n  progress: number;\n  status: 'uploading' | 'completed' | 'error';\n  error?: string;\n}\n\nexport interface ConversionOptions {\n  // Markdown to PDF options\n  title?: string;\n  include_toc?: boolean;\n  custom_css?: string;\n  \n  // HTML to PDF options\n  engine?: 'playwright' | 'selenium';\n  page_size?: string;\n  page_width?: number;\n  page_height?: number;\n  margins?: {\n    top?: number;\n    bottom?: number;\n    left?: number;\n    right?: number;\n  };\n  landscape?: boolean;\n  print_background?: boolean;\n  scale?: number;\n  header_template?: string;\n  footer_template?: string;\n  javascript?: string;\n  wait_time?: number;\n  viewport?: {\n    width: number;\n    height: number;\n  };\n  \n  // DOCX to PDF options\n  method?: 'auto' | 'docx2pdf' | 'word_com' | 'libreoffice';\n  password?: string;\n  bookmarks?: boolean;\n  \n  // Office to PDF options\n  input_format?: string;\n  orientation?: 'portrait' | 'landscape';\n  fit_to_page?: boolean;\n  print_area?: string;\n  worksheets?: string[];\n  export_filter?: string;\n}\n\nexport interface NotificationMessage {\n  id: string;\n  type: 'success' | 'error' | 'warning' | 'info';\n  title: string;\n  message: string;\n  timestamp: string;\n  read: boolean;\n  action?: {\n    label: string;\n    url: string;\n  };\n}