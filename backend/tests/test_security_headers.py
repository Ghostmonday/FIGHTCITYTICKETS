"""
Test for Security Headers Middleware.
"""

from fastapi.testclient import TestClient
from src.app import app
from src.config import settings

client = TestClient(app)

def test_security_headers_present():
    """Test that security headers are present in the response."""
    response = client.get("/")
    assert response.status_code == 200

    headers = response.headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-XSS-Protection"] == "1; mode=block"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    # Root endpoint is NOT docs, so strict CSP
    assert headers["Content-Security-Policy"] == "default-src 'none'; frame-ancestors 'none'"

def test_hsts_header_in_production(monkeypatch):
    """Test that HSTS header is present only in production."""
    monkeypatch.setattr(settings, "app_env", "prod")

    response = client.get("/")
    assert response.status_code == 200
    assert "Strict-Transport-Security" in response.headers
    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains; preload"

def test_hsts_header_absent_in_dev(monkeypatch):
    """Test that HSTS header is absent in dev."""
    monkeypatch.setattr(settings, "app_env", "dev")

    response = client.get("/")
    assert response.status_code == 200
    assert "Strict-Transport-Security" not in response.headers

def test_docs_csp_relaxed():
    """Test that CSP is relaxed for documentation endpoints."""
    # /docs endpoint
    response = client.get("/docs")
    # Note: If docs are disabled, this might be 404, but middleware runs anyway.
    assert response.headers["Content-Security-Policy"] == "default-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net data:;"

    # /redoc endpoint
    response = client.get("/redoc")
    assert response.headers["Content-Security-Policy"] == "default-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net data:;"

    # /openapi.json endpoint
    response = client.get("/openapi.json")
    assert response.headers["Content-Security-Policy"] == "default-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net data:;"
