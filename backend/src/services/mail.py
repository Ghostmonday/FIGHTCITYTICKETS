"""
Lob Mail Service for FightSFTickets.com

Handles physical mail delivery of parking ticket appeals via Lob API.
Generates PDFs and sends certified/regular mail to SFMTA.
"""

import base64
import io
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple

import httpx
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

from ..config import settings

# Import citation services for agency routing
try:
    from .citation import CitationAgency, CitationValidator
except ImportError:
    from citation import CitationAgency, CitationValidator

# Set up logger
logger = logging.getLogger(__name__)

# Lob API configuration
LOB_API_BASE = "https://api.lob.com/v1"


@dataclass
class MailingAddress:
    """Address information for mail routing."""

    address_line1: str
    name: str = "SFMTA Citation Review"
    address_line2: Optional[str] = None
    city: str = "San Francisco"
    state: str = "CA"
    zip_code: str = "94103"

    def to_lob_dict(self) -> Dict[str, str]:
        """Convert to Lob API address format."""
        addr = {
            "name": self.name,
            "address_line1": self.address_line1,
            "address_city": self.city,
            "address_state": self.state,
            "address_zip": self.zip_code,
        }
        if self.address_line2:
            addr["address_line2"] = self.address_line2
        return addr


@dataclass
class AppealLetterRequest:
    """Request to send an appeal letter."""

    citation_number: str
    appeal_type: str  # "standard" or "certified"
    user_name: str
    user_address: str
    user_city: str
    user_state: str
    user_zip: str
    letter_text: str
    selected_photos: Optional[list] = None  # Base64 image data
    signature_data: Optional[str] = None  # Base64 signature


@dataclass
class MailResult:
    """Result from mail sending operation."""

    success: bool
    letter_id: Optional[str] = None
    tracking_number: Optional[str] = None
    expected_delivery: Optional[str] = None
    cost_estimate: Optional[float] = None
    error_message: Optional[str] = None
    carrier: str = "USPS"


class LobMailService:
    """Service for sending appeal letters via Lob API."""

    def __init__(self):
        """Initialize Lob service."""
        self.api_key = settings.lob_api_key
        self.is_live_mode = settings.lob_mode.lower() == "live"
        self.is_available = bool(self.api_key and self.api_key != "change-me")

        if not self.is_available:
            logger.warning("Lob API key not configured for mail service")

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for Lob API."""
        if not self.api_key:
            raise ValueError("Lob API key not configured")

        # Lob uses Basic Auth with API key as username and empty password
        credentials = base64.b64encode(f"{self.api_key}:".encode()).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        }

    def _get_agency_address(self, citation_number: str) -> MailingAddress:
        """Get the correct mailing address based on citation agency."""
        # Identify the agency from citation number
        agency = CitationValidator.identify_agency(citation_number)

        # Map agency to correct mailing address
        agency_addresses = {
            CitationAgency.SFMTA: MailingAddress(
                name="SFMTA Citation Review",
                address_line1="1 South Van Ness Avenue",
                address_line2="Floor 7",
                city="San Francisco",
                state="CA",
                zip_code="94103",
            ),
            CitationAgency.SFPD: MailingAddress(
                name="San Francisco Police Department - Traffic Division",
                address_line1="850 Bryant Street",
                address_line2="Room 500",
                city="San Francisco",
                state="CA",
                zip_code="94103",
            ),
            CitationAgency.SFSU: MailingAddress(
                name="San Francisco State University - Parking & Transportation",
                address_line1="1600 Holloway Avenue",
                address_line2="Burk Hall 100",
                city="San Francisco",
                state="CA",
                zip_code="94132",
            ),
            CitationAgency.SFMUD: MailingAddress(
                name="San Francisco Municipal Utility District",
                address_line1="525 Golden Gate Avenue",
                address_line2="12th Floor",
                city="San Francisco",
                state="CA",
                zip_code="94102",
            ),
        }

        # Return the appropriate address or default to SFMTA
        return agency_addresses.get(agency, agency_addresses[CitationAgency.SFMTA])

    def _generate_appeal_pdf(self, request: AppealLetterRequest) -> bytes:
        """
        Generate PDF from appeal letter and photos.

        Returns PDF as bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=14,
            spaceAfter=30,
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=11,
            spaceAfter=12,
        )

        story = []

        # Header
        story.append(Paragraph("PARKING CITATION APPEAL", title_style))
        story.append(Spacer(1, 12))

        # Citation info
        story.append(
            Paragraph(f"Citation Number: {request.citation_number}", body_style)
        )
        story.append(
            Paragraph(
                f"Appeal Type: {'Certified' if request.appeal_type == 'certified' else 'Standard'}",
                body_style,
            )
        )
        story.append(
            Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", body_style)
        )
        story.append(Spacer(1, 24))

        # Appeal letter text
        for paragraph in request.letter_text.split("\n\n"):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), body_style))
                story.append(Spacer(1, 6))

        story.append(Spacer(1, 24))

        # Signature section
        if request.signature_data:
            # Note: In a real implementation, you'd embed the signature image
            story.append(
                Paragraph("Signature: ___________________________", body_style)
            )
        else:
            story.append(
                Paragraph("Signature: ___________________________", body_style)
            )

        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Name: {request.user_name}", body_style))

        # Selected photos (if any)
        if request.selected_photos:
            story.append(Spacer(1, 24))
            story.append(Paragraph("Attached Evidence:", title_style))

            for i, photo_data in enumerate(request.selected_photos):
                try:
                    # Decode base64 image
                    # Note: This is simplified - real implementation would handle various image formats
                    story.append(Paragraph(f"Evidence Photo {i + 1}", body_style))
                    story.append(Spacer(1, 12))
                except Exception as e:
                    logger.warning(f"Failed to process photo {i}: {e}")

        # Footer
        story.append(Spacer(1, 36))
        story.append(
            Paragraph(
                "This appeal is submitted pursuant to Vehicle Code Section 40215.",
                ParagraphStyle(
                    "Footer", parent=styles["Normal"], fontSize=9, textColor="gray"
                ),
            )
        )

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _get_mail_type(self, appeal_type: str) -> str:
        """Convert appeal type to Lob mail type."""
        if appeal_type == "certified":
            return "usps_certified"
        else:
            return "usps_first_class"

    async def send_appeal_letter(self, request: AppealLetterRequest) -> MailResult:
        """
        Send an appeal letter via Lob API.

        Args:
            request: Complete appeal letter request

        Returns:
            MailResult with success/failure details
        """
        try:
            if not self.is_available:
                return MailResult(
                    success=False, error_message="Lob API key not configured"
                )

            # Get agency-specific address
            agency_address = self._get_agency_address(request.citation_number)

            # User return address
            user_address = MailingAddress(
                name=request.user_name,
                address_line1=request.user_address,
                city=request.user_city,
                state=request.user_state,
                zip_code=request.user_zip,
            )

            # Generate PDF content
            pdf_data = self._generate_appeal_pdf(request)
            pdf_base64 = base64.b64encode(pdf_data).decode()

            # Prepare Lob API request
            mail_type = self._get_mail_type(request.appeal_type)

            payload = {
                "to": agency_address.to_lob_dict(),
                "from": user_address.to_lob_dict(),
                "file": pdf_base64,
                "file_type": "application/pdf",
                "mail_type": mail_type,
                "color": False,  # Black and white is sufficient and cheaper
                "double_sided": True,
            }

            # Certified mail specific settings
            if mail_type == "usps_certified":
                payload["extra_service"] = "certified"
                payload["return_envelope"] = True

            # Send via Lob API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{LOB_API_BASE}/letters",
                    headers=self._get_headers(),
                    json=payload,
                )

                if response.status_code in (200, 201):
                    data = response.json()

                    # Calculate cost estimate (rough)
                    cost_estimate = 10.50 if mail_type == "usps_certified" else 1.00

                    logger.info(
                        f"Successfully sent appeal letter for citation {request.citation_number} "
                        f"via {mail_type} (ID: {data.get('id')})"
                    )

                    return MailResult(
                        success=True,
                        letter_id=data.get("id"),
                        tracking_number=data.get("tracking_number"),
                        expected_delivery=data.get("expected_delivery_date"),
                        cost_estimate=cost_estimate,
                        carrier="USPS",
                    )

                else:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get(
                        "message", "Unknown Lob API error"
                    )

                    logger.error(
                        f"Lob API error for citation {request.citation_number}: "
                        f"{response.status_code} - {error_msg}"
                    )

                    return MailResult(
                        success=False,
                        error_message=f"Lob API error: {error_msg}",
                        carrier="USPS",
                    )

        except httpx.TimeoutException:
            logger.error(f"Lob API timeout for citation {request.citation_number}")
            return MailResult(
                success=False,
                error_message="Mail service timeout. Please try again later.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error sending appeal for citation {request.citation_number}: {str(e)}"
            )
            return MailResult(
                success=False,
                error_message=f"Mail service error: {str(e)}",
            )


# Global service instance
_mail_service = None


def get_mail_service() -> LobMailService:
    """Get the global mail service instance."""
    global _mail_service
    if _mail_service is None:
        _mail_service = LobMailService()
    return _mail_service


async def send_appeal_letter(request: AppealLetterRequest) -> MailResult:
    """
    High-level function to send an appeal letter.

    This is the main entry point for the service.
    """
    service = get_mail_service()
    return await service.send_appeal_letter(request)


def create_appeal_request_from_stripe_metadata(
    metadata: Dict[str, str], letter_text: str
) -> AppealLetterRequest:
    """
    Create an AppealLetterRequest from Stripe checkout session metadata.

    Args:
        metadata: Stripe session metadata dictionary
        letter_text: The appeal letter text (from statement refinement)

    Returns:
        AppealLetterRequest ready for mail service
    """
    return AppealLetterRequest(
        citation_number=metadata.get("citation_number", ""),
        appeal_type=metadata.get("appeal_type", "standard"),
        user_name=metadata.get("user_name", ""),
        user_address=metadata.get("user_address_line1", ""),
        user_city=metadata.get("user_city", ""),
        user_state=metadata.get("user_state", ""),
        user_zip=metadata.get("user_zip", ""),
        letter_text=letter_text,
        selected_photos=None,  # Photos would need to be stored separately
        signature_data=None,  # Signature would need to be stored separately
    )


# Test function
async def test_mail_service():
    """Test the mail service (without actually sending mail)."""
    print("🧪 Testing Mail Service")
    print("=" * 50)

    service = get_mail_service()
    print(f"✅ Service initialized: available={service.is_available}")

    if service.is_available:
        print(f"   Mode: {'Live' if service.is_live_mode else 'Test'}")
        print("   ⚠️  Note: Test mode will not send real mail")
    else:
        print("   ⚠️  Lob API key not configured - will return error on send")

    print("\n⚠️  Full testing requires valid Lob API key")
    print("   and actual appeal data (not included for safety)")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_mail_service())
