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

export enum ConversionFormat {
  PDF = 'PDF',
  HTML = 'HTML',
  DOCX = 'DOCX',
  MARKDOWN = 'MARKDOWN',
  TEXT = 'TEXT'
}

export enum ConversionStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED'
}

// UI and application types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  subscription: SubscriptionTier;
  api_key?: string;
  created_at: string;
  last_login?: string;
}

export enum SubscriptionTier {
  FREE = 'FREE',
  PROFESSIONAL = 'PROFESSIONAL',
  ENTERPRISE = 'ENTERPRISE'
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  tier: SubscriptionTier;
  price: number;
  currency: string;
  billing_period: 'monthly' | 'yearly';
  features: string[];
  limits: {
    conversions_per_month: number;
    max_file_size: number;
    batch_processing: boolean;
    api_access: boolean;
    priority_support: boolean;
  };
}

export interface ConversionHistory {
  id: string;
  job_id: string;
  input_format: string;
  output_format: string;
  file_name: string;
  file_size: number;
  status: ConversionStatus;
  created_at: string;
  completed_at?: string;
  processing_time?: number;
  download_url?: string;
  error_message?: string;
}

export interface UsageStats {
  total_conversions: number;
  successful_conversions: number;
  failed_conversions: number;
  total_file_size: number;
  conversions_this_month: number;
  most_used_format: string;
  average_processing_time: number;
}

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

export interface FileUpload {
  file: File;
  id: string;
  name: string;
  size: number;
  type: string;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
}

export interface ConversionOptions {
  // Markdown to PDF options
  title?: string;
  include_toc?: boolean;
  custom_css?: string;
  
  // HTML to PDF options
  engine?: 'playwright' | 'selenium';
  page_size?: string;
  page_width?: number;
  page_height?: number;
  margins?: {
    top?: number;
    bottom?: number;
    left?: number;
    right?: number;
  };
  landscape?: boolean;
  print_background?: boolean;
  scale?: number;
  header_template?: string;
  footer_template?: string;
  javascript?: string;
  wait_time?: number;
  viewport?: {
    width: number;
    height: number;
  };
  
  // DOCX to PDF options
  method?: 'auto' | 'docx2pdf' | 'word_com' | 'libreoffice';
  password?: string;
  bookmarks?: boolean;
  
  // Office to PDF options
  input_format?: string;
  orientation?: 'portrait' | 'landscape';
  fit_to_page?: boolean;
  print_area?: string;
  worksheets?: string[];
  export_filter?: string;
}

export interface NotificationMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  action?: {
    label: string;
    url: string;
  };
}