"""
Email Service for Fight City Tickets.com

Handles email notifications for payment confirmations and appeal status updates.
Integrates with SendGrid for production email delivery.
Includes circuit breaker protection for resilience.
"""

import logging
import time
from typing import Any, Optional

import httpx

from ..config import settings
from ..middleware.resilience import CircuitBreaker, CircuitOpenError, CircuitState, create_email_circuit

logger = logging.getLogger(__name__)

# Email templates
EMAIL_TEMPLATES = {
    "payment_confirmation": {
        "subject": "Due Process Delivered - Citation {citation_number}",
        "body": """We aren't lawyers. We're paperwork experts.
        
Thank you for using our procedural compliance service.

Your articulated statement for citation {citation_number} is being processed through the Clerical Engine™. 

Details:
- Service Level: {appeal_type}
- Reference ID: {clerical_id}
- Amount: {amount}

Your appeal is being formatted, printed, and mailed exactly how the municipality requires it. We act as your scribe, ensuring your own reasons for appealing are presented with procedural perfection.

Questions? Reply to this email or contact {support_email}

- The FIGHTCITYTICKETS.com Team

---
Legal Disclosure: FIGHTCITYTICKETS.com is a procedural compliance service. We are not a law firm and do not provide legal advice.
""",
    },
    "appeal_mailed": {
        "subject": "Procedural Filing Complete - Citation {citation_number}",
        "body": """Your appeal has been professionally formatted and mailed.

Citation: {citation_number}
Tracking Number: {tracking_number}
Status: Filed with Municipality

FIGHTCITYTICKETS.com has delivered your articulated statement to the appropriate agency. We have ensured your filing meets the clerical standards required for administrative review.

Your Appeal Journey:
1. Filing Received: The agency typically receives the document within 3-5 business days.
2. Administrative Review: The municipality will review the procedural and factual points you provided.
3. Decision Mailed: You will receive their decision directly at your provided address.

Questions? Reply to this email or contact {support_email}

- The FIGHTCITYTICKETS.com Team

---
Legal Disclosure: We aren't lawyers. We're paperwork experts. We do not guarantee outcomes.
""",
    },
    "appeal_rejected": {
        "subject": "Agency Response Received - Citation {citation_number}",
        "body": """The municipality has issued a response to your filing.

Citation: {citation_number}
Agency Determination: Appeal Not Accepted

Reason Provided:
{reason}

FIGHTCITYTICKETS.com provided procedural compliance services for your initial filing. The administrative review has reached a determination based on the facts you provided.

Next Steps:
- You may have the right to request a formal hearing.
- You may wish to consult with a licensed attorney for legal advice.
- You should review the agency's decision notice for further instructions.

Questions? Reply to this email or contact {support_email}

- The FIGHTCITYTICKETS.com Team

---
Legal Disclosure: We are not lawyers. We've helped you fulfill the procedural requirements of your appeal.
""",
    },
    "email_verification": {
        "subject": "Verify your email for Fight City Tickets",
        "body": """Please verify your email address.

Click the link below to verify your email address:
{verification_link}

If you didn't request this, please ignore this email.

Questions? Reply to this email or contact {support_email}

- The FIGHTCITYTICKETS.com Team
""",
    },
}


class EmailService:
    """Email notification service with SendGrid integration and circuit breaker protection."""

    # Circuit breaker configuration
    CIRCUIT_FAILURE_THRESHOLD = 5
    CIRCUIT_TIMEOUT = 300  # 5 minutes

    def __init__(self):
        """Initialize email service."""
        self.api_key = getattr(settings, "sendgrid_api_key", None)
        self.from_email = settings.service_email
        self.support_email = settings.support_email
        self.from_name = "Fight City Tickets.com"
        self.is_available = bool(self.api_key and self.api_key != "change-me")

        # Circuit breaker for SendGrid API resilience
        self._circuit_breaker = create_email_circuit(fallback=self._email_fallback)

        # Track daily email count for rate limiting
        self._daily_count = 0
        self._last_reset = time.time()

        if self.is_available:
            logger.info("Email service initialized with SendGrid")
        else:
            logger.info(
                "Email service initialized in logging mode (no SendGrid API key configured)"
            )

    def _email_fallback(self) -> dict[str, Any]:
        """Fallback response when email circuit is open."""
        return {
            "status": "unavailable",
            "message": "Email service temporarily unavailable. Notifications will be retried.",
            "retry_after": 30,
        }

    def is_healthy(self) -> bool:
        """Check if email service is healthy (respects circuit breaker)."""
        if self._circuit_breaker.metrics.state == CircuitState.OPEN:
            return False
        return self.is_available

    def get_status(self) -> dict[str, Any]:
        """Get email service status including circuit breaker state."""
        return {
            "healthy": self.is_healthy(),
            "circuit_state": self._circuit_breaker.metrics.state.value,
            "circuit_failures": self._circuit_breaker.metrics.failure_count,
            "total_calls": self._circuit_breaker.metrics.total_calls,
            "daily_count": self._daily_count,
        }

    async def send_admin_alert(self, subject: str, message: str) -> bool:
        """
        Send an alert email to the admin/support email.

        Args:
            subject: The alert subject
            message: The alert message body

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.support_email:
            logger.error("No support_email configured for admin alerts")
            return False

        full_subject = f"[ALERT] {subject}"
        logger.warning(f"Sending admin alert: {full_subject}")

        if self.is_available:
            return await self._send_via_sendgrid(self.support_email, full_subject, message)

        # If not available, just logging (which we already did) is sufficient
        return True

    async def _send_via_sendgrid(
        self, to_email: str, subject: str, body_text: str
    ) -> bool:
        """Send email via SendGrid API with circuit breaker protection."""
        if not self.api_key:
            return False

        # Reset daily count if needed
        now = time.time()
        if now - self._last_reset > 86400:  # 24 hours
            self._daily_count = 0
            self._last_reset = now

        try:
            async with self._circuit_breaker:
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
                    self._daily_count += 1
                    logger.info(f"Email sent successfully to {to_email}")
                    return True
            return False  # Fallback was called, circuit is open

        except CircuitOpenError:
            logger.warning("Email circuit is open, skipping send")
            return False
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

    async def send_verification_email(
        self,
        email: str,
        verification_link: str,
    ) -> bool:
        """
        Send email verification link.

        Args:
            email: User email address
            verification_link: The full verification URL

        Returns:
            True if email was sent successfully (or logged in dev mode)
        """
        subject, body = await self._render_template(
            "email_verification",
            verification_link=verification_link,
        )

        # Always log
        logger.info(
            f"Verification email to {email}: Link {verification_link}"
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

    async def send_admin_alert(self, subject: str, message: str) -> bool:
        """
        Send an admin alert email.

        Args:
            subject: Email subject
            message: Email body

        Returns:
            True if sent successfully or logged in fallback
        """
        if not self.support_email:
            logger.warning("No support email configured for admin alerts")
            return False

        full_subject = f"[ADMIN ALERT] {subject}"

        # Always log critical alerts
        logger.error(f"ADMIN ALERT: {subject} - {message}")

        if self.is_available:
            success = await self._send_via_sendgrid(self.support_email, full_subject, message)
            if success:
                return True
            logger.warning("Failed to send admin alert via SendGrid")

        return True


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
