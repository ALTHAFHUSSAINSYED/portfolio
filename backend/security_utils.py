"""
Security utilities for the portfolio application.
Includes input sanitization, HTTPS enforcement, and security headers.
"""

import bleach
import functools
from typing import Dict, Any, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# --- HTML Sanitization ---

def sanitize_html(html_content: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Args:
        html_content: The HTML content to sanitize
        
    Returns:
        Sanitized HTML content
    """
    # Define allowed tags and attributes
    allowed_tags = [
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 
        'p', 'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'br', 'hr', 
        'img', 'span', 'div', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ]
    allowed_attrs = {
        '*': ['class', 'id', 'style'],
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
    }
    
    return bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

def sanitize_input_dict(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize all string values in a dictionary.
    
    Args:
        input_data: Dictionary of input data
        
    Returns:
        Dictionary with sanitized string values
    """
    result = {}
    for key, value in input_data.items():
        if isinstance(value, str):
            result[key] = bleach.clean(value)
        elif isinstance(value, dict):
            result[key] = sanitize_input_dict(value)
        elif isinstance(value, list):
            result[key] = [
                sanitize_input_dict(item) if isinstance(item, dict)
                else bleach.clean(item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result

# --- HTTPS Enforcement Middleware ---

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to redirect HTTP requests to HTTPS.
    Only redirects in production environment.
    """
    
    def __init__(self, app: ASGIApp, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next: Callable):
        if not self.enabled:
            # Skip redirect if disabled
            return await call_next(request)
        
        # Check if request is HTTP and not localhost
        if request.url.scheme == "http" and request.headers.get("host", "").lower() not in ["localhost", "127.0.0.1"]:
            # Create HTTPS URL
            https_url = str(request.url).replace("http://", "https://", 1)
            
            # Create redirect response
            response = Response(
                status_code=301,  # Permanent redirect
                headers={"Location": https_url}
            )
            return response
        
        return await call_next(request)

# --- Security Headers Middleware ---

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Add security headers
        headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Control iframe embedding (prevent clickjacking)
            "X-Frame-Options": "SAMEORIGIN",
            
            # Enable browser XSS protection
            "X-XSS-Protection": "1; mode=block",
            
            # HTTP Strict Transport Security (HSTS) - enforce HTTPS
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            
            # Referrer Policy - control information in the Referer header
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Content Security Policy - control resource loading
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://*.cloudinary.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "img-src 'self' data: https://*.cloudinary.com https://via.placeholder.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self' https://api.sendgrid.com https://aistudio.google.com; "
                "frame-src 'self'; "
                "object-src 'none';"
            ),
            
            # Permissions Policy - control browser features
            "Permissions-Policy": (
                "camera=(), "
                "microphone=(), "
                "geolocation=(), "
                "interest-cohort=()"
            )
        }
        
        # Add headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
        
        return response