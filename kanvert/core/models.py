"""
Data models for the Kanvert application.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class ConversionStatus(str, Enum):
    """Conversion job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConversionFormat(str, Enum):
    """Supported conversion formats."""
    PDF = "PDF"
    HTML = "HTML"
    DOCX = "DOCX"
    MARKDOWN = "MARKDOWN"
    TEXT = "TEXT"
    XLSX = "XLSX"
    PPTX = "PPTX"


class SubscriptionTier(str, Enum):
    """User subscription tiers."""
    FREE = "FREE"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"


# Base Models
class BaseModel(BaseModel):
    """Base model with common configuration."""
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# User Models
class User(BaseModel):
    """User model."""
    id: str = Field(..., alias="_id")
    email: EmailStr
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password_hash: str
    subscription: SubscriptionTier = SubscriptionTier.FREE
    api_key: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    email_verified: bool = False
    company: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    country: str = "US"
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True


class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr
    name: str
    first_name: str
    last_name: str
    password: str
    terms_accepted: bool
    newsletter_subscription: bool = False


class UserUpdate(BaseModel):
    """User update model."""
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


# Conversion Models
class ConversionOptions(BaseModel):
    """Conversion options model."""
    # General options
    quality: Optional[str] = "high"
    compression: Optional[str] = "medium"
    
    # PDF-specific options
    page_size: Optional[str] = "A4"
    page_width: Optional[int] = None
    page_height: Optional[int] = None
    margins: Optional[Dict[str, int]] = None
    landscape: Optional[bool] = False
    
    # Markdown-specific options
    theme: Optional[str] = "github"
    include_toc: Optional[bool] = False
    custom_css: Optional[str] = None
    
    # HTML-specific options
    engine: Optional[str] = "playwright"
    print_background: Optional[bool] = True
    scale: Optional[float] = 1.0
    header_template: Optional[str] = None
    footer_template: Optional[str] = None
    javascript: Optional[str] = None
    wait_time: Optional[int] = 0
    viewport: Optional[Dict[str, int]] = None
    
    # DOCX-specific options
    method: Optional[str] = "auto"
    password: Optional[str] = None
    bookmarks: Optional[bool] = True
    
    # Office-specific options
    input_format: Optional[str] = None
    orientation: Optional[str] = "portrait"
    fit_to_page: Optional[bool] = False
    print_area: Optional[str] = None
    worksheets: Optional[List[str]] = None
    export_filter: Optional[str] = None
    
    # Watermark options
    watermark_enabled: Optional[bool] = False
    watermark_text: Optional[str] = None
    watermark_opacity: Optional[float] = 0.5


class ConversionRequest(BaseModel):
    """Conversion request model."""
    content: Optional[str] = None
    file_url: Optional[str] = None
    output_format: ConversionFormat
    options: Optional[ConversionOptions] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversionJob(BaseModel):
    """Conversion job model."""
    id: str = Field(..., alias="_id")
    user_id: str
    job_id: str
    input_format: str
    output_format: str
    input_filename: str
    output_filename: Optional[str] = None
    file_size: Optional[int] = None
    status: ConversionStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    options: Optional[ConversionOptions] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True


# API Key Models
class APIKey(BaseModel):
    """API key model."""
    id: str = Field(..., alias="_id")
    user_id: str
    name: str
    key: str
    permissions: List[str]
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True
    usage_count: int = 0

    class Config:
        allow_population_by_field_name = True


# Batch Processing Models
class BatchFile(BaseModel):
    """Batch file model."""
    id: str
    name: str
    size: int
    type: str
    status: ConversionStatus
    progress: int = 0
    file_path: str
    result_url: Optional[str] = None
    error: Optional[str] = None


class BatchJob(BaseModel):
    """Batch job model."""
    id: str = Field(..., alias="_id")
    user_id: str
    name: str
    files: List[BatchFile] = []
    status: ConversionStatus
    progress: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    options: ConversionOptions
    error_message: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


# Template Models
class ConversionTemplate(BaseModel):
    """Conversion template model."""
    id: str = Field(..., alias="_id")
    user_id: Optional[str] = None  # None for system templates
    name: str
    description: str
    input_format: str
    output_format: str
    options: ConversionOptions
    created_at: datetime
    usage_count: int = 0
    is_default: bool = False

    class Config:
        allow_population_by_field_name = True


# Scheduled Job Models
class ScheduledJob(BaseModel):
    """Scheduled job model."""
    id: str = Field(..., alias="_id")
    user_id: str
    name: str
    template_id: str
    schedule_type: str  # 'once', 'daily', 'weekly', 'monthly'
    schedule_time: datetime
    next_run: datetime
    status: str  # 'active', 'paused', 'completed'
    created_at: datetime
    last_run: Optional[datetime] = None
    run_count: int = 0
    options: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True


# Analytics Models
class UsageStats(BaseModel):
    """Usage statistics model."""
    user_id: str
    date: datetime
    conversions_count: int = 0
    successful_conversions: int = 0
    failed_conversions: int = 0
    total_file_size: int = 0
    total_processing_time: float = 0.0
    formats_used: Dict[str, int] = {}


class SystemStats(BaseModel):
    """System-wide statistics model."""
    date: datetime
    total_users: int = 0
    active_users: int = 0
    total_conversions: int = 0
    successful_conversions: int = 0
    failed_conversions: int = 0
    total_file_size: int = 0
    avg_processing_time: float = 0.0
    popular_formats: Dict[str, int] = {}


# Notification Models
class NotificationMessage(BaseModel):
    """Notification message model."""
    id: str = Field(..., alias="_id")
    user_id: str
    type: str  # 'success', 'error', 'warning', 'info'
    title: str
    message: str
    timestamp: datetime
    read: bool = False
    action: Optional[Dict[str, str]] = None  # {'label': 'View', 'url': '/conversion/123'}
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True


# System Models
class SystemHealth(BaseModel):
    """System health model."""
    status: str  # 'healthy', 'degraded', 'unhealthy'
    timestamp: datetime
    services: Dict[str, str]
    metrics: Dict[str, Any]
    uptime: float
    version: str


# Response Models
class ConversionResponse(BaseModel):
    """Conversion response model."""
    job_id: str
    status: ConversionStatus
    message: Optional[str] = None
    download_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    processing_time: Optional[float] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response model."""
    items: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


class APIResponse(BaseModel):
    """Generic API response model."""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)