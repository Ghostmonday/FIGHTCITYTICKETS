"""
Authentication and Authorization Utilities

Centralized logic for admin authentication, audit logging, and security checks.
"""

import hashlib
import json
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional

import jwt
from fastapi import Cookie, Header, HTTPException, Request, status

logger = logging.getLogger(__name__)

# Audit logging for admin actions
ADMIN_AUDIT_LOG = "admin_audit.log"
ADMIN_SECRET_HEADER = "X-Admin-Secret"
ADMIN_COOKIE_NAME = "admin_session"
ALGORITHM = "HS256"


def log_admin_action(
    action: str,
    admin_id: str,
    request: Request,
    details: Optional[dict[str, Any]] = None
) -> None:
    """
    Log admin actions for security auditing.

    Args:
        action: The admin action being performed
        admin_id: Identifier for the admin (secret or IP)
        request: The original request
        details: Additional details to log
    """
    # Securely hash the admin_id so we don't log secrets
    hashed_id = hashlib.sha256(admin_id.encode()).hexdigest()[:8]

    # Get client IP safely
    client_ip = "unknown"
    if request.client and request.client.host:
        client_ip = request.client.host

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "admin_id": f"admin-{hashed_id}",
        "ip": client_ip,
        "path": request.url.path,
        "method": request.method,
        "details": details or {},
    }

    try:
        with open(ADMIN_AUDIT_LOG, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.warning(f"Failed to write admin audit log: {e}")


def _log_auth_failure(ip: str, reason: str) -> None:
    """Helper to log authentication failures to the audit log."""
    try:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": "auth_failure",
            "ip": ip,
            "status": "failed",
            "reason": reason
        }
        with open(ADMIN_AUDIT_LOG, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    # TODO: CODE_REVIEW - Silent failure for audit logging (intentional, but should log at debug level)
    except Exception:
        pass


def create_admin_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT token for admin session."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=12)

    to_encode.update({"exp": expire})

    # Use settings.secret_key if available, else environment variable
    secret_key = os.getenv("SECRET_KEY", "dev-secret-change-in-production")

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def verify_admin_token(token: str) -> Optional[dict]:
    """Verify and decode the admin JWT token."""
    secret_key = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def _validate_admin_access(request: Request, secret_provided: Optional[str] = None) -> bool:
    """
    Common validation logic for admin access.
    Checks secret (if provided) and IP allowlist.
    """
    admin_secret = os.getenv("ADMIN_SECRET")
    client_ip = "unknown"
    if request.client and request.client.host:
        client_ip = request.client.host
    else:
        client_ip = os.getenv('REMOTE_ADDR', 'unknown')

    if not admin_secret:
        logger.error(
            "ADMIN_SECRET environment variable not set - admin routes disabled"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication not configured.",
        )

    # 1. Verify Secret if provided
    if secret_provided is not None:
        if not secrets.compare_digest(secret_provided.encode(), admin_secret.encode()):
            logger.warning(
                f"Failed admin access attempt - Invalid admin secret. IP: {client_ip}"
            )
            _log_auth_failure(client_ip, "invalid_secret")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin secret",
            )

    # 2. IP Allowlist Check
    allowed_ips = os.getenv("ADMIN_ALLOWED_IPS", "").strip()
    if allowed_ips:
        allowed_list = [ip.strip() for ip in allowed_ips.split(",")]
        if client_ip not in allowed_list:
            logger.warning(
                f"Failed admin access attempt - IP not in allowlist. "
                f"IP: {client_ip}, Allowed: {allowed_ips}"
            )
            _log_auth_failure(client_ip, "ip_not_allowed")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP not authorized for admin access",
            )

    return True


def verify_admin_secret(
    request: Request,
    x_admin_secret: str = Header(..., alias="X-Admin-Secret"),
) -> str:
    """
    Verify the admin secret header and check IP allowlist.
    Requires explicit ADMIN_SECRET environment variable.

    Legacy function used by webhooks and external scripts.
    """
    _validate_admin_access(request, secret_provided=x_admin_secret)

    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Admin access granted (header) - IP: {client_ip}")
    return x_admin_secret


def get_current_admin(
    request: Request,
    x_admin_secret: Optional[str] = Header(None, alias="X-Admin-Secret"),
) -> str:
    """
    Verify admin access via Cookie (JWT) or Header (Secret).
    Used by Admin UI and API.
    """
    # 1. Check Header first (priority for scripts)
    if x_admin_secret:
        return verify_admin_secret(request, x_admin_secret)

    # 2. Check Cookie
    token = request.cookies.get(ADMIN_COOKIE_NAME)
    if token:
        payload = verify_admin_token(token)
        if payload and payload.get("sub") == "admin":
            # Also validate IP even for session
            _validate_admin_access(request, secret_provided=None)

            client_ip = request.client.host if request.client else "unknown"
            # Return a placeholder ID for logging
            return "admin-session"

    # 3. Fail
    client_ip = request.client.host if request.client else "unknown"
    _log_auth_failure(client_ip, "missing_credentials")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
