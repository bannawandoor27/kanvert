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
    
    # Configure standard library logging
    logging_config = _get_logging_config(settings)
    logging.config.dictConfig(logging_config)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.JSONRenderer() if settings.log_format == "json" 
            else structlog.dev.ConsoleRenderer(colors=True)
        ],
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
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s"
        }
    }
    
    # Base handlers
    handlers = {
        "console": {
            "class": "rich.logging.RichHandler" if settings.is_development() else "logging.StreamHandler",
            "level": settings.log_level.value,
            "formatter": "default" if settings.log_format == "text" else "json",
            "stream": sys.stdout
        }
    }
    
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
            "handlers": list(handlers.keys()),
            "propagate": False
        },
        "uvicorn": {
            "level": "INFO" if settings.log_level == LogLevel.DEBUG else "WARNING",
            "handlers": ["console"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO" if settings.is_development() else "WARNING",
            "handlers": ["console"],
            "propagate": False
        },
        "fastapi": {
            "level": settings.log_level.value,
            "handlers": list(handlers.keys()),
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
            "level": settings.log_level.value,
            "handlers": list(handlers.keys())
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


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)