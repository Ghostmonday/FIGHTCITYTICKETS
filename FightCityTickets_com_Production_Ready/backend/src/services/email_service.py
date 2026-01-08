"""
Email Notification Service for FightCityTickets.com

Sends transactional emails to users for:
- Payment confirmation
- Appeal mailing confirmation
- Status updates
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Handles email notifications."""

    def __init__(self):
        """Initialize email service."""
        # TODO: Integrate with email provider (SendGrid, AWS SES, etc.)
        self.is_available = False
        logger.warning("Email service not configured - emails will be logged only")

    async def send_payment_confirmation(
        self,
        email: str,
        citation_number: str,
        amount_paid: int,
        appeal_type: str,
        session_id: str,
    ) -> bool:
        """
        Send payment confirmation email.

        Args:
            email: User email address
            citation_number: Citation number
            amount_paid: Amount paid in cents
            appeal_type: Type of appeal (standard/certified)
            session_id: Stripe session ID

        Returns:
            True if sent successfully
        """
        try:
            amount = "${amount_paid / 100:.2f}"

            # TODO: Implement actual email sending
            logger.info(
                "📧 Payment confirmation email would be sent to {email}: "
                "Citation {citation_number}, Amount {amount}, Type {appeal_type}"
            )

            # For now, just log
            # In production, integrate with SendGrid/AWS SES/etc.
            return True
        except Exception as e:
            logger.error("Failed to send payment confirmation email: {e}")
            return False

    async def send_appeal_mailed(
        self,
        email: str,
        citation_number: str,
        tracking_number: str,
        expected_delivery: Optional[str] = None,
    ) -> bool:
        """
        Send appeal mailed confirmation email.

        Args:
            email: User email address
            citation_number: Citation number
            tracking_number: Lob tracking number
            expected_delivery: Expected delivery date

        Returns:
            True if sent successfully
        """
        try:
            logger.info(
                "📧 Appeal mailed email would be sent to {email}: "
                "Citation {citation_number}, Tracking {tracking_number}"
            )

            # TODO: Implement actual email sending
            return True
        except Exception as e:
            logger.error("Failed to send appeal mailed email: {e}")
            return False


def get_email_service() -> EmailService:
    """Get email service instance."""
    return EmailService()


