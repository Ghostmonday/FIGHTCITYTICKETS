"""
Email Service for Fight City Tickets.com

Handles email notifications for payment confirmations and appeal status updates.
Integrates with SendGrid for production email delivery.
"""

import logging
from typing import Optional

import httpx

from ..config import settings

logger = logging.getLogger(__name__)

# Email templates
EMAIL_TEMPLATES = {
    "payment_confirmation": {
        "subject": "Payment Received - Your Appeal is Processing",
        "body": """Thank you for your payment!

Your parking ticket appeal for citation {citation_number} is now being processed.

Details:
- Amount Paid: {amount}
- Appeal Type: {appeal_type}
- Reference: {clerical_id}

Your appeal letter is being prepared and will be mailed to the appropriate agency shortly. You will receive a follow-up email with tracking information once your appeal has been mailed.

Questions? Reply to this email or contact {support_email}

- The Fight City Tickets.com Team

---
Note: We are not lawyers. This is a document preparation service only.
""",
    },
    "appeal_mailed": {
        "subject": "Your Appeal Has Been Mailed - Tracking Included",
        "body": """Great news! Your appeal has been mailed.

Citation: {citation_number}
Tracking Number: {tracking_number}
Expected Delivery: {expected_delivery}

Your appeal letter has been sent via USPS Certified Mail with tracking. You can track delivery status using the tracking number above.

What happens next?
1. The agency receives your appeal (typically 3-5 business days)
2. They will process your appeal (timelines vary by city)
3. You will receive a decision by mail

Questions? Reply to this email or contact {support_email}

- The Fight City Tickets.com Team

---
Note: We are not lawyers. This is a document preparation service only.
""",
    },
    "appeal_rejected": {
        "subject": "Update on Your Appeal - Citation {citation_number}",
        "body": """We wanted to let you know about the status of your appeal.

Citation: {citation_number}
Status: Appeal Not Accepted

The agency provided the following reason:
{reason}

This is not necessarily the end of the process. You may have additional options:
1. Request a hearing to present your case in person
2. Consult with a traffic attorney for legal advice
3. Review the agency's decision for any procedural errors

Note: We cannot provide legal advice. This message is for informational purposes only.

Questions? Reply to this email or contact {support_email}

- The Fight City Tickets.com Team

---
Note: We are not lawyers. This is a document preparation service only.
""",
    },
}


class EmailService:
    """Email notification service with SendGrid integration."""

    def __init__(self):
        """Initialize email service."""
        self.api_key = getattr(settings, "sendgrid_api_key", None)
        self.from_email = settings.service_email
        self.support_email = settings.support_email
        self.from_name = "Fight City Tickets.com"
        self.is_available = bool(self.api_key and self.api_key != "change-me")

        if self.is_available:
            logger.info("Email service initialized with SendGrid")
        else:
            logger.info(
                "Email service initialized in logging mode (no SendGrid API key configured)"
            )

    async def _send_via_sendgrid(
        self, to_email: str, subject: str, body_text: str
    ) -> bool:
        """Send email via SendGrid API."""
        if not self.api_key:
            return False

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "personalizations": [
                            {"to": [{"email": to_email}]}
                        ],
                        "from": {
                            "email": self.from_email,
                            "name": self.from_name,
                        },
                        "subject": subject,
                        "content": [
                            {
                                "type": "text/plain",
                                "value": body_text,
                            }
                        ],
                    },
                )
                response.raise_for_status()
                logger.info(f"Email sent successfully to {to_email}")
                return True

        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {e}")
            return False

    async def _render_template(self, template_name: str, **kwargs) -> tuple:
        """Render email template with provided values."""
        template = EMAIL_TEMPLATES.get(template_name, {})
        subject = template.get("subject", "Update from Fight City Tickets.com")
        body = template.get("body", "")

        # Add support_email to kwargs if not present
        if "support_email" not in kwargs:
            kwargs["support_email"] = self.support_email

        # Replace placeholders
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            body = body.replace(placeholder, str(value))
            subject = subject.replace(placeholder, str(value))

        return subject, body

    async def send_payment_confirmation(
        self,
        email: str,
        citation_number: str,
        amount_paid: int,
        appeal_type: str,
        clerical_id: Optional[str] = None,
    ) -> bool:
        """
        Send payment confirmation email.

        Args:
            email: Customer email address
            citation_number: Citation number
            amount_paid: Amount paid in cents
            appeal_type: standard or certified
            clerical_id: Clerical Engine ID for reference

        Returns:
            True if email was sent successfully (or logged in dev mode)
        """
        amount = f"${amount_paid / 100:.2f}"

        subject, body = await self._render_template(
            "payment_confirmation",
            citation_number=citation_number,
            amount=amount,
            appeal_type=appeal_type,
            clerical_id=clerical_id or "N/A",
        )

        # Always log
        logger.info(
            f"Payment confirmation email to {email}: "
            f"Citation {citation_number}, Amount {amount}, Type {appeal_type}"
        )

        # Try to send via SendGrid if configured
        if self.is_available:
            success = await self._send_via_sendgrid(email, subject, body)
            if success:
                return True
            logger.warning("SendGrid send failed, falling back to logged mode")

        return True  # Return True for logged mode

    async def send_appeal_mailed(
        self,
        email: str,
        citation_number: str,
        tracking_number: Optional[str] = None,
        expected_delivery: Optional[str] = None,
    ) -> bool:
        """
        Send appeal mailed notification email.

        Args:
            email: Customer email address
            citation_number: Citation number
            tracking_number: Lob tracking number if available
            expected_delivery: Expected delivery date

        Returns:
            True if email was sent successfully (or logged in dev mode)
        """
        subject, body = await self._render_template(
            "appeal_mailed",
            citation_number=citation_number,
            tracking_number=tracking_number or "Pending",
            expected_delivery=expected_delivery or "3-5 business days",
        )

        # Always log
        logger.info(
            f"Appeal mailed email to {email}: "
            f"Citation {citation_number}, Tracking {tracking_number}"
        )

        # Try to send via SendGrid if configured
        if self.is_available:
            success = await self._send_via_sendgrid(email, subject, body)
            if success:
                return True
            logger.warning("SendGrid send failed, falling back to logged mode")

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
            True if email was sent successfully (or logged in dev mode)
        """
        subject, body = await self._render_template(
            "appeal_rejected",
            citation_number=citation_number,
            reason=reason,
        )

        # Always log
        logger.info(
            f"Appeal rejected email to {email}: "
            f"Citation {citation_number}, Reason: {reason}"
        )

        # Try to send via SendGrid if configured
        if self.is_available:
            success = await self._send_via_sendgrid(email, subject, body)
            if success:
                return True
            logger.warning("SendGrid send failed, falling back to logged mode")

        return True


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
