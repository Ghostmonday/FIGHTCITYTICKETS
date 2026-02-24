"""
Authentication and Authorization Utilities

Centralized logic for admin authentication, audit logging, and security checks.
"""

import hashlib
import json
import logging
import os
import secrets
from datetime import datetime
from typing import Any, Optional

from fastapi import Header, HTTPException, Request, status

logger = logging.getLogger(__name__)

# Audit logging for admin actions
ADMIN_AUDIT_LOG = "admin_audit.log"
ADMIN_SECRET_HEADER = "X-Admin-Secret"


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
    except Exception:
        pass


def verify_admin_secret(
    request: Request,
    x_admin_secret: str = Header(..., alias="X-Admin-Secret"),
) -> str:
    """
    Verify the admin secret header and check IP allowlist.
    Requires explicit ADMIN_SECRET environment variable.

    Security enhancements:
    - Timing-safe secret comparison
    - IP allowlist (ADMIN_ALLOWED_IPS env var)
    - Audit logging for both success and failure
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

    # 1. Verify Secret
    if not secrets.compare_digest(x_admin_secret.encode(), admin_secret.encode()):
        logger.warning(
            f"Failed admin access attempt - Invalid admin secret. IP: {client_ip}"
        )

        # Log failure to audit log
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

            # Log failure to audit log
            _log_auth_failure(client_ip, "ip_not_allowed")

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP not authorized for admin access",
            )

    logger.info(f"Admin access granted - IP: {client_ip}")
    return x_admin_secret
