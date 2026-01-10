"""
Lob Mail Service for FightCityTickets.com

Handles physical mail delivery of parking ticket appeals via Lob API.
Generates PDFs and sends certified/regular mail to citation agencies.
"""

import base64
import io
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import httpx
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from ..config import settings
from .address_validator import get_address_validator
from .citation import CitationAgency, CitationValidator
from .city_registry import AppealMailStatus, get_city_registry

# Set up logger
logger = logging.getLogger(__name__)

# Lob API configuration
LOB_API_BASE = "https://api.lob.com/v1"


@dataclass
class MailingAddress:
    """Address information for mail routing."""

    address_line1: str
    name: str = "Citation Review"
    address_line2: str | None = None
    city: str = "San Francisco"
    state: str = "CA"
    zip_code: str = "94103"
    address_country: str = "US"

    def to_lob_dict(self) -> dict[str, str]:
        """Convert to Lob API address format."""
        addr: dict[str, str] = {
            "name": self.name,
            "address_line1": self.address_line1,
            "address_city": self.city,
            "address_state": self.state,
            "address_zip": self.zip_code,
            "address_country": self.address_country,
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
    selected_photos: list[str] | None = None
    signature_data: str | None = None
    city_id: str | None = None
    section_id: str | None = None


@dataclass
class MailResult:
    """Result of a mail operation."""

    success: bool
    letter_id: str | None = None
    tracking_number: str | None = None
    expected_delivery: str | None = None
    error_message: str | None = None


class LobMailService:
    """Handles Lob API integration for physical mail delivery."""

    api_key: str
    is_live_mode: bool
    is_available: bool
    city_registry: Any

    def __init__(self) -> None:
        """Initialize the Lob mail service."""
        self.api_key = settings.lob_api_key
        self.is_live_mode = not self.api_key.startswith("test_")
        self.is_available = bool(self.api_key and self.api_key != "")
        self.city_registry = get_city_registry() if self.is_available else None

        if self.is_available:
            logger.info(
                "LobMailService initialized (mode: %s)",
                "live" if self.is_live_mode else "test",
            )
        else:
            logger.warning("LobMailService initialized but no API key configured")

    def _generate_appeal_pdf(self, request: AppealLetterRequest) -> str:
        """
        Generate a PDF for the appeal letter.

        Args:
            request: The appeal letter request

        Returns:
            Base64-encoded PDF content
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        story: list[Any] = []

        # Styles
        styles = getSampleStyleSheet()
        body_style = styles["Normal"]
        body_style.fontSize = 11
        body_style.leading = 14

        title_style = styles["Heading1"]
        title_style.fontSize = 14
        title_style.alignment = 1  # Center

        # Top spacer for return address window (2 inches = 144 points)
        story.append(Spacer(1, 144))

        # Header
        story.append(Paragraph("PARKING CITATION APPEAL", title_style))

        # Date
        story.append(Spacer(1, 24))
        story.append(
            Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", body_style)
        )

        # Recipient address (will be overlaid by Lob)
        story.append(Spacer(1, 72))

        # Letter body
        story.append(Paragraph("Dear Citation Review Board,", body_style))
        story.append(Spacer(1, 12))

        # Split letter text into paragraphs and add each
        paragraphs = request.letter_text.split("\n\n")
        for para in paragraphs:
            if para.strip():
                # Clean up the paragraph
                clean_para = para.strip().replace("\n", " ")
                story.append(Paragraph(clean_para, body_style))
                story.append(Spacer(1, 12))

        # Closing
        story.append(Spacer(1, 24))
        story.append(Paragraph("Sincerely,", body_style))
        story.append(Spacer(1, 24))

        # Signature line
        story.append(Paragraph(request.user_name, body_style))

        # Add violation info as a footer on last page
        story.append(Spacer(1, 48))
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.gray,
        )
        story.append(
            Paragraph(
                f"Citation: {request.citation_number} | {request.appeal_type.title()} Appeal",
                footer_style,
            )
        )

        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        return base64.b64encode(pdf_bytes).decode("utf-8")

    def _get_agency_address(
        self,
        citation_number: str,
        city_id: str | None = None,
        section_id: str | None = None,
    ) -> MailingAddress:
        """
        Get the appropriate mailing address for the appeal.

        Args:
            citation_number: The citation number
            city_id: City identifier
            section_id: Section/agency identifier

        Returns:
            MailingAddress for the appropriate agency
        """
        # Try city registry first if available
        if self.city_registry and city_id:
            try:
                mail_address = self.city_registry.get_mail_address(
                    city_id, section_id or ""
                )
                if mail_address and mail_address.status == AppealMailStatus.COMPLETE:
                    logger.info("Using city-specific address for city_id=%s", city_id)
                    return MailingAddress(
                        name=mail_address.department or "Citation Review",
                        address_line1=mail_address.address1,
                        address_line2=mail_address.address2,
                        city=mail_address.city,
                        state=mail_address.state,
                        zip_code=mail_address.zip,
                    )
            except Exception as e:
                logger.warning(
                    "CityRegistry address lookup failed for city_id=%s: %s", city_id, e
                )

        # Try city registry with citation matching (fallback)
        if self.city_registry:
            try:
                match = self.city_registry.match_citation(citation_number)
                if match:
                    matched_city_id, matched_section_id = match
                    mail_address = self.city_registry.get_mail_address(
                        matched_city_id, matched_section_id
                    )
                    if (
                        mail_address
                        and mail_address.status == AppealMailStatus.COMPLETE
                    ):
                        logger.info(
                            "Using citation-matched address for city_id=%s",
                            matched_city_id,
                        )
                        return MailingAddress(
                            name=mail_address.department or "Citation Review",
                            address_line1=mail_address.address1,
                            address_line2=mail_address.address2,
                            city=mail_address.city,
                            state=mail_address.state,
                            zip_code=mail_address.zip,
                        )
            except Exception as e:
                logger.warning("CityRegistry citation match failed: %s", e)

        # Fall back to legacy agency mapping
        agency = CitationValidator.identify_agency(citation_number)

        # Map agency to correct mailing address
        agency_addresses: dict[CitationAgency, MailingAddress] = {
            CitationAgency.SFMTA: MailingAddress(
                name="SFMTA Citation Review",
                address_line1="1 South Van Ness Avenue",
                address_line2="Floor 7",
                city="San Francisco",
                state="CA",
                zip_code="94103",
            ),
            CitationAgency.SFPD: MailingAddress(
                name="SFPD - Traffic Division",
                address_line1="850 Bryant Street",
                address_line2="Room 510",
                city="San Francisco",
                state="CA",
                zip_code="94103",
            ),
            CitationAgency.SFSU: MailingAddress(
                name="SFSU Parking Services",
                address_line1="1650 Holloway Avenue",
                city="San Francisco",
                state="CA",
                zip_code="94132",
            ),
            CitationAgency.LAPD: MailingAddress(
                name="LADOT Parking Violations Bureau",
                address_line1="111 S Hill St",
                city="Los Angeles",
                state="CA",
                zip_code="90012",
            ),
            CitationAgency.NYPD: MailingAddress(
                name="NYC Department of Finance",
                address_line1="66 John St",
                city="New York",
                state="NY",
                zip_code="10038",
            ),
            CitationAgency.CHICAGO: MailingAddress(
                name="Chicago Department of Finance",
                address_line1="333 S State St",
                room="115",
                city="Chicago",
                state="IL",
                zip_code="60602",
            ),
            CitationAgency.SEATTLE: MailingAddress(
                name="Seattle Department of Transportation",
                address_line1="PO Box 34996",
                city="Seattle",
                state="WA",
                zip_code="98124-4996",
            ),
            CitationAgency.DENVER: MailingAddress(
                name="Denver Public Works",
                address_line1="201 W Colfax Ave",
                department="Dept 307",
                city="Denver",
                state="CO",
                zip_code="80202",
            ),
            CitationAgency.PORTLAND: MailingAddress(
                name="Portland Bureau of Transportation",
                address_line1="1120 SW 5th Ave",
                city="Portland",
                state="OR",
                zip_code="97204",
            ),
        }

        return agency_addresses.get(agency, agency_addresses[CitationAgency.SFMTA])

    async def send_appeal_letter(self, request: AppealLetterRequest) -> MailResult:
        """
        Send an appeal letter via Lob API.

        Args:
            request: The appeal letter request

        Returns:
            MailResult with tracking information or error details
        """
        if not self.is_available:
            return MailResult(
                success=False,
                error_message="Lob API key not configured",
            )

        try:
            # Get addresses
            agency_address = self._get_agency_address(
                request.citation_number, request.city_id, request.section_id
            )
            user_address = MailingAddress(
                name=request.user_name,
                address_line1=request.user_address,
                city=request.user_city,
                state=request.user_state,
                zip_code=request.user_zip,
            )

            # Generate PDF
            pdf_base64 = self._generate_appeal_pdf(request)

            # Build Lob API payload
            payload: dict[str, Any] = {
                "description": f"Appeal letter for citation {request.citation_number}",
                "to": agency_address.to_lob_dict(),
                "from": user_address.to_lob_dict(),
                "file": pdf_base64,
                "file_type": "application/pdf",
                "mail_type": "usps_first_class",
                "color": False,
                "double_sided": True,
                "address_placement": "top_first_page",
            }

            # Make API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{LOB_API_BASE}/letters",
                    auth=(self.api_key, ""),
                    json=payload,
                )

            if response.status_code in [200, 201]:
                data = response.json()
                return MailResult(
                    success=True,
                    letter_id=data.get("id"),
                    tracking_number=data.get("tracking_number"),
                    expected_delivery=data.get("expected_delivery_date"),
                )
            else:
                error_data = response.json() if response.content else {}
                error_msg = (
                    error_data.get("error", {}).get("message")
                    if isinstance(error_data, dict)
                    else str(response.text)
                )
                logger.error("Lob API error: %s - %s", response.status_code, error_msg)
                return MailResult(
                    success=False,
                    error_message=f"API error {response.status_code}: {error_msg}",
                )

        except httpx.TimeoutException:
            logger.exception("Lob API timeout")
            return MailResult(success=False, error_message="Request timeout")
        except Exception as e:
            logger.exception("Unexpected error sending appeal letter")
            return MailResult(success=False, error_message=str(e))

    async def verify_address(
        self, address1: str, city: str, state: str, zip_code: str
    ) -> tuple[bool, str | None]:
        """
        Verify an address using Lob's US Verification API.

        Args:
            address1: Primary street address
            city: City name
            state: Two-letter state code
            zip_code: ZIP code

        Returns:
            Tuple of (is_valid, standardized_address or None)
        """
        if not self.is_available:
            return True, None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{LOB_API_BASE}/us_verifications",
                    auth=(self.api_key, ""),
                    json={
                        "primary_line": address1,
                        "city": city,
                        "state": state,
                        "zip_code": zip_code,
                    },
                )

            if response.status_code == 200:
                data = response.json()
                standardized = data.get("standardized_address", {})
                return (
                    data.get("deliverability") != "undeliverable",
                    f"{standardized.get('primary_line', '')}, {standardized.get('city', '')}, {standardized.get('state', '')} {standardized.get('zip_code', '')}".strip(
                        ","
                    ),
                )
            return True, None  # Allow through if API fails

        except Exception as e:
            logger.warning("Address verification failed: %s", e)
            return True, None


# Global service instance
_mail_service: LobMailService | None = None


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
