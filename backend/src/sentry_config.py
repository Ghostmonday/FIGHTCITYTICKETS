"""
Sentry Error Tracking Configuration for Fight City Tickets

Provides error tracking and performance monitoring via Sentry.
"""

import os
from typing import Optional

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


def init_sentry(dsn: Optional[str] = None, environment: str = "production") -> bool:
    """
    Initialize Sentry error tracking.

    Args:
        dsn: Sentry DSN (if not provided, reads from SENTRY_DSN env var)
        environment: Environment name (production, staging, development)

    Returns:
        True if Sentry was initialized, False otherwise
    """
    if not SENTRY_AVAILABLE:
        return False

    dsn = dsn or os.getenv("SENTRY_DSN")
    if not dsn:
        return False

    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
            profiles_sample_rate=0.1,  # 10% of transactions for profiling
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                LoggingIntegration(
                    level=None,  # Capture all log levels
                    event_level=None  # Send all log events as Sentry events
                ),
            ],
            # Set release version (can be set via env var)
            release=os.getenv("APP_VERSION", "unknown"),
            # Filter out health check endpoints
            ignore_errors=[
                KeyboardInterrupt,
                SystemExit,
            ],
            # Additional context
            before_send=lambda event, hint: event,  # Can add filtering here
        )
        return True
    # NOTE: Silent failure is intentional — Sentry init must never crash the app.
    # print() is used here intentionally to avoid a circular dependency if the logging
    # config itself depends on Sentry being initialized first.
    except Exception as e:
        print(f"[WARNING] Sentry initialization failed: {e}. Error tracking is disabled.")
        return False

