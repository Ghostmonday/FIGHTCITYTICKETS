
"""
Email Service for FightCityTickets.com

Handles email notifications for payment confirmations and appeal status updates.
Currently logs emails; integrate with SendGrid, AWS SES, or similar for production.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Email notification service."""

    def __init__(self):
        """Initialize email service."""
        self.is_available = False
        logger.info("Email service initialized (logging mode)")

    async def send_payment_confirmation(
        self,
        email: str,
        citation_number: str,
        amount_paid: int,
        appeal_type: str,
    ) -> bool:
        """
        Send payment confirmation email.

        Args:
            email: Customer email address
            citation_number: Citation number
            amount_paid: Amount paid in cents
            appeal_type: standard or certified

        Returns:
            True if email would be sent (logged in dev mode)
        """
        amount = f"${amount_paid / 100:.2f}"
        logger.info(
            f"Payment confirmation email would be sent to {email}: "
            f"Citation {citation_number}, Amount {amount}, Type {appeal_type}"
        )
        return True

    async def send_appeal_mailed(
        self,
        email: str,
        citation_number: str,
        tracking_number: Optional[str],
    ) -> bool:
        """
        Send appeal mailed notification email.

        Args:
            email: Customer email address
            citation_number: Citation number
            tracking_number: Lob tracking number if available

        Returns:
            True if email would be sent (logged in dev mode)
        """
        logger.info(
            f"Appeal mailed email would be sent to {email}: "
            f"Citation {citation_number}, Tracking {tracking_number}"
        )
        return True

    async def send_appeal_rejected(
        self,
        email: str,
        citation_number: str,
        reason: str,
    ) -> bool:
        """
        Send appeal rejected notification email.

        Args:
            email: Customer email address
            citation_number: Citation number
            reason: Rejection reason from city

        Returns:
            True if email would be sent (logged in dev mode)
        """
        logger.info(
            f"Appeal rejected email would be sent to {email}: "
            f"Citation {citation_number}, Reason: {reason}"
        )
        return True


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
