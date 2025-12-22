"""
Webhook Error Handling and Dead-Letter Queue Service

Handles failed webhook processing, retries, and dead-letter queue management.
"""

import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

from ..services.database import get_db_service

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Severity levels for webhook errors."""

    LOW = "low"  # Retryable, non-critical
    MEDIUM = "medium"  # Retryable, may need attention
    HIGH = "high"  # Critical, needs immediate attention
    CRITICAL = "critical"  # System failure, alert required


class WebhookError:
    """Represents a webhook processing error."""

    def __init__(
        self,
        event_id: str,
        event_type: str,
        error_message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        retry_count: int = 0,
        last_attempt: Optional[datetime] = None,
        error_data: Optional[Dict] = None,
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.error_message = error_message
        self.severity = severity
        self.retry_count = retry_count
        self.last_attempt = last_attempt or datetime.utcnow()
        self.error_data = error_data or {}
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Convert error to dictionary for storage."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "error_message": self.error_message,
            "severity": self.severity.value,
            "retry_count": self.retry_count,
            "last_attempt": self.last_attempt.isoformat(),
            "created_at": self.created_at.isoformat(),
            "error_data": self.error_data,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "WebhookError":
        """Create error from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            error_message=data["error_message"],
            severity=ErrorSeverity(data["severity"]),
            retry_count=data.get("retry_count", 0),
            last_attempt=datetime.fromisoformat(data["last_attempt"])
            if isinstance(data.get("last_attempt"), str)
            else data.get("last_attempt"),
            error_data=data.get("error_data", {}),
        )


class WebhookErrorHandler:
    """Handles webhook errors, retries, and dead-letter queue."""

    MAX_RETRIES = 3
    RETRY_DELAY_MINUTES = [5, 15, 60]  # Progressive backoff

    def __init__(self):
        self.db_service = get_db_service()
        # In-memory storage for errors (in production, use database or Redis)
        self._error_queue: Dict[str, WebhookError] = {}
        self._dead_letter_queue: List[WebhookError] = []

    def log_error(
        self,
        event_id: str,
        event_type: str,
        error_message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_data: Optional[Dict] = None,
    ) -> WebhookError:
        """
        Log a webhook processing error.

        Args:
            event_id: Stripe event ID
            event_type: Event type (e.g., "checkout.session.completed")
            error_message: Human-readable error message
            severity: Error severity level
            error_data: Additional error context

        Returns:
            WebhookError object
        """
        error = WebhookError(
            event_id=event_id,
            event_type=event_type,
            error_message=error_message,
            severity=severity,
            error_data=error_data,
        )

        # Store in error queue
        self._error_queue[event_id] = error

        # Log based on severity
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(
                f"CRITICAL webhook error: {event_type} ({event_id}): {error_message}",
                extra={"error_data": error_data},
            )
        elif severity == ErrorSeverity.HIGH:
            logger.error(
                f"HIGH severity webhook error: {event_type} ({event_id}): {error_message}",
                extra={"error_data": error_data},
            )
        else:
            logger.warning(
                f"Webhook error: {event_type} ({event_id}): {error_message}",
                extra={"error_data": error_data},
            )

        # In production, store in database for persistence
        # self._store_error_in_db(error)

        return error

    def should_retry(self, event_id: str) -> bool:
        """
        Check if an error should be retried.

        Args:
            event_id: Stripe event ID

        Returns:
            True if should retry, False if should go to dead-letter queue
        """
        if event_id not in self._error_queue:
            return False

        error = self._error_queue[event_id]

        # Don't retry if max retries exceeded
        if error.retry_count >= self.MAX_RETRIES:
            return False

        # Don't retry critical errors (they need manual intervention)
        if error.severity == ErrorSeverity.CRITICAL:
            return False

        # Check if enough time has passed since last attempt
        delay_minutes = self.RETRY_DELAY_MINUTES[
            min(error.retry_count, len(self.RETRY_DELAY_MINUTES) - 1)
        ]
        time_since_last = datetime.utcnow() - error.last_attempt

        return time_since_last >= timedelta(minutes=delay_minutes)

    def increment_retry(self, event_id: str) -> Optional[WebhookError]:
        """
        Increment retry count for an error.

        Args:
            event_id: Stripe event ID

        Returns:
            Updated WebhookError or None if not found
        """
        if event_id not in self._error_queue:
            return None

        error = self._error_queue[event_id]
        error.retry_count += 1
        error.last_attempt = datetime.utcnow()

        logger.info(
            f"Retry attempt {error.retry_count}/{self.MAX_RETRIES} "
            f"for event {event_id}"
        )

        return error

    def move_to_dead_letter_queue(self, event_id: str) -> Optional[WebhookError]:
        """
        Move an error to the dead-letter queue.

        Args:
            event_id: Stripe event ID

        Returns:
            WebhookError that was moved, or None if not found
        """
        if event_id not in self._error_queue:
            return None

        error = self._error_queue.pop(event_id)
        self._dead_letter_queue.append(error)

        logger.error(
            f"Moved event {event_id} to dead-letter queue after "
            f"{error.retry_count} failed attempts"
        )

        # In production, store in database and send alert
        # self._store_in_dead_letter_db(error)
        # self._send_alert(error)

        return error

    def get_errors_for_retry(self) -> List[WebhookError]:
        """
        Get list of errors that are ready for retry.

        Returns:
            List of WebhookError objects ready for retry
        """
        retryable = []
        for event_id, error in self._error_queue.items():
            if self.should_retry(event_id):
                retryable.append(error)

        return retryable

    def get_dead_letter_queue(self) -> List[WebhookError]:
        """
        Get all errors in dead-letter queue.

        Returns:
            List of WebhookError objects in dead-letter queue
        """
        return self._dead_letter_queue.copy()

    def clear_error(self, event_id: str) -> bool:
        """
        Clear an error from the queue (successful retry).

        Args:
            event_id: Stripe event ID

        Returns:
            True if error was found and cleared
        """
        if event_id in self._error_queue:
            error = self._error_queue.pop(event_id)
            logger.info(f"Cleared error for event {event_id} after successful retry")
            return True
        return False

    def get_error_stats(self) -> Dict:
        """
        Get statistics about webhook errors.

        Returns:
            Dictionary with error statistics
        """
        total_errors = len(self._error_queue)
        dead_letter_count = len(self._dead_letter_queue)

        errors_by_severity = {}
        for error in list(self._error_queue.values()) + self._dead_letter_queue:
            severity = error.severity.value
            errors_by_severity[severity] = errors_by_severity.get(severity, 0) + 1

        return {
            "total_errors": total_errors,
            "dead_letter_count": dead_letter_count,
            "errors_by_severity": errors_by_severity,
            "retryable_count": len(self.get_errors_for_retry()),
        }


# Global error handler instance
_error_handler: Optional[WebhookErrorHandler] = None


def get_error_handler() -> WebhookErrorHandler:
    """Get the global webhook error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = WebhookErrorHandler()
    return _error_handler

