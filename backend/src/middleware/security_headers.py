"""
Security Headers Middleware for Fight City Tickets.com

Adds essential security headers to all responses to protect against common attacks:
- X-Content-Type-Options: nosniff (prevent MIME sniffing)
- X-Frame-Options: DENY (prevent clickjacking)
- X-XSS-Protection: 1; mode=block (enable XSS filter)
- Referrer-Policy: strict-origin-when-cross-origin (control referrer info)
- Content-Security-Policy: default-src 'none'; frame-ancestors 'none' (API restriction)
- Strict-Transport-Security: max-age=31536000; includeSubDomains (HSTS, only in prod)
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # CSP for API (assuming JSON responses mainly)
        # Prevent embedding in iframes and restrict content loading
        # Relax for documentation endpoints which need to load scripts/styles
        if request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
            # Allow scripts and styles for Swagger UI/ReDoc
            # They often load from CDN or inline
            response.headers["Content-Security-Policy"] = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "cdn.jsdelivr.net data:;"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'none'; frame-ancestors 'none'"
            )

        # HSTS (HTTP Strict Transport Security)
        # Only enable in production to avoid issues during development
        if settings.app_env in ("prod", "production"):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response
