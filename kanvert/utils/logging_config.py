"""
Logging configuration for the Kanvert application.
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

import structlog
from rich.logging import RichHandler

from ..config.settings import Settings, LogLevel


def setup_logging(settings: Settings) -> None:
    """
    Setup structured logging for the application.
    
    Args:
        settings: Application settings containing logging configuration
    """
    
    # Configure standard library logging first
    logging_config = _get_logging_config(settings)
    logging.config.dictConfig(logging_config)
    
    # Configure structlog processors based on environment
    if settings.is_development():
        # Development: clean console output
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Production: JSON output
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.JSONRenderer()
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.value)
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def _get_logging_config(settings: Settings) -> Dict[str, Any]:
    """
    Get logging configuration dictionary.
    
    Args:
        settings: Application settings
        
    Returns:
        Logging configuration dictionary
    """
    
    # Base formatters
    formatters = {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
        },
        "simple": {
            "format": "%(levelname)s - %(name)s - %(message)s",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s"
        }
    }
    
    # Determine formatter based on environment and log format
    if settings.is_development():
        # In development, always use readable text format for console
        console_formatter = "simple"
    else:
        # In production, use specified format
        console_formatter = "json" if settings.log_format == "json" else "default"
    
    # Base handlers
    handlers = {
        "console": {
            "class": "rich.logging.RichHandler" if settings.is_development() else "logging.StreamHandler",
            "level": settings.log_level.value,
            "formatter": console_formatter,
        }
    }
    
    # Configure RichHandler specific settings
    if settings.is_development():
        handlers["console"].update({
            "rich_tracebacks": True,
            "show_time": True,
            "show_level": True,
            "show_path": True,
        })
    else:
        handlers["console"]["stream"] = sys.stdout
    
    # Add file handler if log file is specified
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.log_level.value,
            "formatter": "json" if settings.log_format == "json" else "detailed",
            "filename": str(log_path),
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8"
        }
    
    # Logger configuration
    loggers = {
        "kanvert": {
            "level": settings.log_level.value,
            "handlers": ["console"] if not settings.log_file else ["console", "file"],
            "propagate": False
        },
        # Reduce verbosity of third-party libraries
        "uvicorn": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False
        },
        "fastapi": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False
        },
        # Suppress other noisy loggers
        "asyncio": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False
        },
        "urllib3": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False
        }
    }
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": handlers,
        "loggers": loggers,
        "root": {
            "level": "WARNING",  # Suppress root logger noise
            "handlers": ["console"] if not settings.log_file else ["console", "file"]
        }
    }


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def get_module_logger(module_name: str) -> structlog.BoundLogger:
    """
    Get a logger for a specific module using structlog.
    
    This is the preferred way to get loggers in the application.
    
    Args:
        module_name: Usually __name__ from the calling module
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(module_name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)