"""
FastAPI middleware for security, logging, and request handling.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import structlog

from ..config.settings import Settings

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Start timing
        start_time = time.time()
        
        # Extract request info
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "content_type": request.headers.get("content-type"),
            "content_length": request.headers.get("content-length")
        }
        
        # Log request
        logger.info("Request started", **request_info)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            response_info = {
                **request_info,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "response_size": response.headers.get("content-length")
            }
            
            if response.status_code >= 400:
                logger.warning("Request completed with error", **response_info)
            else:
                logger.info("Request completed successfully", **response_info)
            
            # Add timing header
            response.headers["X-Process-Time"] = str(duration)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log error
            error_info = {
                **request_info,
                "duration_ms": round(duration * 1000, 2),
                "error": str(e),
                "error_type": type(e).__name__
            }
            
            logger.error("Request failed with exception", **error_info)
            raise


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers and basic protection."""
    
    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check API key if configured
        if self.settings.api_key:
            api_key = request.headers.get("X-API-Key")
            if not api_key or api_key != self.settings.api_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or missing API key"
                )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""
    
    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings
        self.requests = {}  # In production, use Redis or similar
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries (simple sliding window)
        minute_ago = current_time - 60
        self.requests = {
            ip: [req_time for req_time in times if req_time > minute_ago]
            for ip, times in self.requests.items()
        }
        
        # Check rate limit
        if client_ip in self.requests:
            if len(self.requests[client_ip]) >= self.settings.rate_limit_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
        else:
            self.requests[client_ip] = []
        
        # Record this request
        self.requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.settings.rate_limit_requests - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.settings.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response


class ContentSizeMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce content size limits."""
    
    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            size = int(content_length)
            if size > self.settings.max_request_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request size {size} exceeds maximum {self.settings.max_request_size} bytes"
                )
        
        return await call_next(request)


def setup_middleware(app, settings: Settings):
    """Setup all middleware for the FastAPI application."""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        **settings.get_cors_config()
    )
    
    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add custom middleware (order matters - last added runs first)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityMiddleware, settings=settings)
    app.add_middleware(RateLimitMiddleware, settings=settings)
    app.add_middleware(ContentSizeMiddleware, settings=settings)