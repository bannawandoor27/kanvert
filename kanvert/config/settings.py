"""
Configuration management for the Kanvert application.
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings
from enum import Enum


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = Field(default="Kanvert", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    
    # API settings
    api_prefix: str = Field(default="/api/v1", description="API route prefix")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    max_request_size: int = Field(default=10 * 1024 * 1024, description="Maximum request size in bytes (10MB)")
    
    # Security settings
    secret_key: str = Field(default="your-secret-key-change-in-production", description="Secret key for signing")
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="JWT secret key")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration in minutes")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    
    # Database settings (SQLite)
    DATABASE_PATH: Optional[str] = Field(default=None, description="SQLite database file path")
    DATABASE_URL: str = Field(default="sqlite:///data/kanvert.db", description="Database connection URL")
    
    # Email settings
    EMAIL_BACKEND: str = Field(default="console", description="Email backend: smtp or console")
    EMAIL_FROM: str = Field(default="noreply@kanvert.com", description="From email address")
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_TLS: bool = Field(default=True, description="Use TLS for SMTP")
    
    # Frontend settings
    FRONTEND_URL: str = Field(default="http://localhost:5173", description="Frontend application URL")
    
    # Logging settings
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # Conversion settings
    max_content_size: int = Field(default=5 * 1024 * 1024, description="Maximum content size for conversion (5MB)")
    conversion_timeout: int = Field(default=300, description="Conversion timeout in seconds")
    temp_dir: str = Field(default="/tmp/kanvert", description="Temporary directory for processing")
    
    # MCP settings
    mcp_enabled: bool = Field(default=True, description="Enable MCP protocol support")
    mcp_server_name: str = Field(default="kanvert", description="MCP server name")
    mcp_version: str = Field(default="1.0.0", description="MCP protocol version")
    
    # Health check settings
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    
    # PDF conversion specific settings
    pdf_page_size: str = Field(default="A4", description="Default PDF page size")
    pdf_margins: str = Field(default="2cm", description="Default PDF margins")
    pdf_font_family: str = Field(default="Times New Roman", description="Default PDF font family")
    pdf_font_size: str = Field(default="11pt", description="Default PDF font size")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    def get_cors_config(self) -> dict:
        """Get CORS configuration."""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
        }
    
    def get_uvicorn_config(self) -> dict:
        """Get Uvicorn server configuration."""
        return {
            "host": self.host,
            "port": self.port,
            "reload": self.reload and self.is_development(),
            "workers": 1 if self.is_development() else self.workers,
            "log_level": self.log_level.lower(),
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings