"""
Mailing service for appeal letter generation and delivery.

This module handles PDF generation for appeal letters and integration with
Lob.com for certified and standard mail delivery.

Author: Neural Draft LLC
"""

import base64
import hashlib
import io
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MailingAddress:
    """Represents a mailing address for appeal delivery."""

    def __init__(
        self,
        name: str,
        address_line_1: str,
        address_line_2: Optional[str] = None,
        city: str = "",
        state: str = "",
        zip_code: str = "",
        country: str = "US",
    ):
        self.name = name
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

    def to_lob_dict(self) -> Dict[str, str]:
        """Convert to Lob API address format."""
        address = {
            "name": self.name,
            "address_line1": self.address_line_1,
            "country": self.country,
        }

        if self.address_line_2:
            address["address_line2"] = self.address_line_2

        if self.city:
            address["city"] = self.city

        if self.state:
            address["state"] = self.state

        if self.zip_code:
            address["zip"] = self.zip_code

        return address

    def to_string(self) -> str:
        """Format address as a string for display."""
        lines = [self.name, self.address_line_1]
        if self.address_line_2:
            lines.append(self.address_line_2)
        if self.city or self.state or self.zip_code:
            parts = []
            if self.city:
                parts.append(self.city)
            if self.state:
                parts.append(self.state)
            if self.zip_code:
                parts.append(self.zip_code)
            lines.append(" ".join(parts))
        return "\n".join(lines)


class AppealLetterRequest:
    """Request model for appeal letter generation."""

    def __init__(
        self,
        citation_number: str,
        user_name: str,
        user_address_line_1: str,
        user_address_line_2: Optional[str],
        user_city: str,
        user_state: str,
        user_zip: str,
        user_email: str,
        letter_text: str,
        agency_name: str,
        agency_address: str,
        appeal_type: str = "certified",
        violation_date: Optional[str] = None,
        vehicle_info: Optional[str] = None,
    ):
        self.citation_number = citation_number
        self.user_name = user_name
        self.user_address_line_1 = user_address_line_1
        self.user_address_line_2 = user_address_line_2
        self.user_city = user_city
        self.user_state = user_state
        self.user_zip = user_zip
        self.user_email = user_email
        self.letter_text = letter_text
        self.agency_name = agency_name
        self.agency_address = agency_address
        self.appeal_type = appeal_type
        self.violation_date = violation_date
        self.vehicle_info = vehicle_info
        # Generate unique Clerical ID for tracking
        self.clerical_id = self._generate_clerical_id()

    def _generate_clerical_id(self) -> str:
        """Generate a unique Clerical Engine™ ID for this submission."""
        unique_string = f"{self.citation_number}-{datetime.now().isoformat()}-{uuid.uuid4().hex[:8]}"
        return f"CE-{hashlib.sha256(unique_string.encode()).hexdigest()[:12].upper()}"


class MailResult:
    """Result model for mail service operations."""

    def __init__(
        self,
        success: bool,
        tracking_number: Optional[str] = None,
        lob_id: Optional[str] = None,
        error_message: Optional[str] = None,
        delivery_date: Optional[str] = None,
    ):
        self.success = success
        self.tracking_number = tracking_number
        self.lob_id = lob_id
        self.error_message = error_message
        self.delivery_date = delivery_date

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "tracking_number": self.tracking_number,
            "lob_id": self.lob_id,
            "error_message": self.error_message,
            "delivery_date": self.delivery_date,
        }


class LobMailService:
    """
    Service for generating appeal PDFs and sending via Lob.com.

    This service handles:
    - PDF generation with professional formatting
    - Address verification through Lob
    - Certified and standard mail delivery
    - Tracking number management
    """

    # Agency addresses for major cities
    AGENCY_ADDRESSES: Dict[str, Dict[str, str]] = {
        "sf": {
            "name": "SFMTA - Parking Citations",
            "address": "P.O. Box 7426\nSan Francisco, CA 94120",
        },
        "sfpd": {
            "name": "San Francisco Police Department",
            "address": "Attn: Traffic Section\n850 Bryant St, Room 510\nSan Francisco, CA 94103",
        },
        "sfsu": {
            "name": "San Francisco State University Police Department",
            "address": "1600 Holloway Ave\nSan Francisco, CA 94132",
        },
        "sfmud": {
            "name": "SF Municipal Transportation Agency",
            "address": "1 South Van Ness Ave, 7th Floor\nSan Francisco, CA 94103",
        },
        "la": {
            "name": "Los Angeles Department of Transportation",
            "address": "P.O. Box 30210\nLos Angeles, CA 90030",
        },
        "lapd": {
            "name": "Los Angeles Police Department",
            "address": "Attn: Parking Enforcement Division\n251 E 6th St, 9th Floor\nLos Angeles, CA 90014",
        },
        "ladot": {
            "name": "Los Angeles Department of Transportation",
            "address": "P.O. Box 30210\nLos Angeles, CA 90030",
        },
        "nyc": {
            "name": "NYC Department of Finance",
            "address": "P.O. Box 280993\nBrooklyn, NY 11228",
        },
        "nypd": {
            "name": "NYC Police Department - Traffic",
            "address": "Attn: Traffic Violations Bureau\n15-15 149th Street\nWhitestone, NY 11357",
        },
        "chicago": {
            "name": "City of Chicago Department of Finance",
            "address": "P.O. Box 88298\nChicago, IL 60680",
        },
        "seattle": {
            "name": "Seattle Department of Transportation",
            "address": "P.O. Box 34996\nSeattle, WA 98124",
        },
        "denver": {
            "name": "Denver Department of Transportation and Infrastructure",
            "address": "P.O. Box 460909\nDenver, CO 80204",
        },
        "phoenix": {
            "name": "City of Phoenix Transportation Department",
            "address": "P.O. Box 20600\nPhoenix, AZ 85036",
        },
        "portland": {
            "name": "Portland Bureau of Transportation",
            "address": "P.O. Box 4376\nPortland, OR 97208",
        },
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Lob mail service.

        Args:
            api_key: Lob.com API key. If not provided, reads from LOB_API_KEY env var.
        """
        self.api_key = api_key
        # Only initialize Lob client if API key is available
        self._lob_client = None
        self._use_lob = False

        if api_key:
            try:
                import lob

                self._lob_client = lob.ApiClient(
                    configuration=lob.Configuration(
                        api_key=api_key, api_version="2023-08-01"
                    )
                )
                self._use_lob = True
                logger.info("LobMailService initialized with Lob API")
            except ImportError:
                logger.warning("Lob library not installed, using fallback")
                self._use_lob = False
            except Exception as e:
                logger.error(f"Failed to initialize Lob client: {e}")
                self._use_lob = False
        else:
            logger.warning("LobMailService initialized but no API key configured")

    def _generate_appeal_pdf(self, request: AppealLetterRequest) -> str:
        """
        Generate a professional PDF for the procedural compliance submission.

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

        # Professional title style - serif for authority
        title_style = ParagraphStyle(
            "ProfessionalTitle",
            parent=styles["Heading1"],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.black,
            fontName="Times-Bold",
        )

        # Professional body style
        body_style = ParagraphStyle(
            "ProfessionalBody",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            spaceAfter=12,
            textColor=colors.black,
            fontName="Times-Roman",
        )

        # Date style - aligned left
        date_style = ParagraphStyle(
            "ProfessionalDate",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            spaceAfter=24,
            textColor=colors.black,
            fontName="Times-Roman",
        )

        # Salutation style
        salutation_style = ParagraphStyle(
            "ProfessionalSalutation",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            spaceAfter=12,
            textColor=colors.black,
            fontName="Times-Roman",
        )

        # Top spacer for return address window (2 inches = 144 points)
        story.append(Spacer(1, 144))

        # Professional Header - PROCEDURAL COMPLIANCE SUBMISSION
        story.append(
            Paragraph("PROCEDURAL COMPLIANCE SUBMISSION: CITATION REVIEW", title_style)
        )

        # Clerical Engine ID header
        clerical_style = ParagraphStyle(
            "ClericalID",
            parent=styles["Normal"],
            fontSize=8,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.gray,
            fontName="Times-Roman",
        )
        story.append(
            Paragraph(
                f"Processed via Clerical Engine™ | ID: {request.clerical_id}",
                clerical_style,
            )
        )

        # Date
        story.append(
            Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", date_style)
        )

        # Recipient address (will be overlaid by Lob)
        story.append(Spacer(1, 72))

        # Agency name in letter
        story.append(Paragraph(f"To: {request.agency_name}", body_style))
        story.append(Spacer(1, 12))

        # Subject line
        subject_style = ParagraphStyle(
            "Subject",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            spaceAfter=12,
            textColor=colors.black,
            fontName="Times-Bold",
        )
        story.append(
            Paragraph(f"Re: Citation Number {request.citation_number}", subject_style)
        )

        # Salutation
        story.append(Paragraph("To Whom It May Concern,", salutation_style))
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
        story.append(Paragraph("Respectfully submitted,", body_style))
        story.append(Spacer(1, 36))

        # Signature line with Clerical ID
        story.append(Paragraph(request.user_name, body_style))

        # Add violation info and metadata footer
        story.append(Spacer(1, 48))

        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.gray,
            fontName="Times-Roman",
        )

        # Submission metadata footer
        metadata_parts = [
            f"Citation: {request.citation_number}",
            f"Type: {request.appeal_type.title()} Appeal",
            f"Clerical Engine ID: {request.clerical_id}",
            f"Date: {datetime.now().strftime('%Y-%m-%d')}",
        ]
        story.append(Paragraph(" | ".join(metadata_parts), footer_style))

        # Page number indicator for multi-page letters
        story.append(Spacer(1, 12))
        page_info_style = ParagraphStyle(
            "PageInfo",
            parent=styles["Normal"],
            fontSize=7,
            alignment=TA_CENTER,
            textColor=colors.lightgrey,
            fontName="Times-Roman",
        )
        story.append(
            Paragraph(
                "Procedural Compliance Submission - Neural Draft LLC", page_info_style
            )
        )

        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        return base64.b64encode(pdf_bytes).decode("utf-8")

    def _get_agency_address(self, agency_key: str) -> Dict[str, str]:
        """
        Get the mailing address for the specified agency.

        Args:
            agency_key: The agency key (e.g., 'sf', 'la', 'nyc')

        Returns:
            Dictionary with 'name' and 'address' keys
        """
        # First check if the key contains location info
        if "-" in agency_key:
            # Extract just the city code
            parts = agency_key.split("-")
            for part in parts:
                if part in self.AGENCY_ADDRESSES:
                    return self.AGENCY_ADDRESSES[part]

        # Direct lookup
        if agency_key in self.AGENCY_ADDRESSES:
            return self.AGENCY_ADDRESSES[agency_key]

        # Fallback to generic address
        logger.warning(f"Unknown agency key: {agency_key}, using generic address")
        return {
            "name": "Citation Review Board",
            "address": "P.O. Box 1234\nAnytown, ST 12345",
        }

    async def send_appeal_letter(
        self,
        request: AppealLetterRequest,
    ) -> MailResult:
        """
        Generate and send an appeal letter via Lob.

        Args:
            request: The appeal letter request

        Returns:
            MailResult with tracking information
        """
        try:
            # Get agency address
            agency_info = self._get_agency_address(request.agency_name)
            agency_address = agency_info["address"]

            # Generate PDF
            pdf_base64 = self._generate_appeal_pdf(request)
            pdf_bytes = base64.b64decode(pdf_base64)

            if self._use_lob and self._lob_client:
                # Use Lob API for certified mail
                return await self._send_via_lob(request, pdf_bytes, agency_info)
            else:
                # Fallback: Log and return success (for development)
                logger.info(
                    f"Generated appeal PDF for citation {request.citation_number}"
                )
                logger.info(f"Clerical ID: {request.clerical_id}")
                logger.info(f"Agency: {agency_info['name']}")
                logger.info(f"Address: {agency_address}")

                # Return mock result for development
                return MailResult(
                    success=True,
                    tracking_number="DEMO123456789",
                    lob_id=f"lob_demo_{request.clerical_id}",
                    delivery_date=datetime.now().strftime("%Y-%m-%d"),
                )

        except Exception as e:
            logger.error(f"Failed to send appeal letter: {e}")
            return MailResult(success=False, error_message=str(e))

    async def _send_via_lob(
        self,
        request: AppealLetterRequest,
        pdf_bytes: bytes,
        agency_info: Dict[str, str],
    ) -> MailResult:
        """
        Send letter via Lob API.

        Args:
            request: The appeal letter request
            pdf_bytes: The PDF bytes
            agency_info: Agency address info

        Returns:
            MailResult with Lob tracking
        """
        try:
            import lob

            # Create address objects
            from_address = lob.Address.create(
                name=request.user_name,
                address_line1=request.user_address_line_1,
                address_line2=request.user_address_line_2,
                city=request.user_city,
                state=request.user_state,
                zip=request.user_zip,
                country="US",
            )

            # Parse agency address
            agency_lines = agency_info["address"].split("\n")
            to_address = lob.Address.create(
                name=agency_info["name"],
                address_line1=agency_lines[0] if len(agency_lines) > 0 else "",
                address_line2=agency_lines[1] if len(agency_lines) > 1 else None,
                city=request.user_city,
                state=request.user_state,
                zip=request.user_zip,
                country="US",
            )

            # Create the letter
            letter_obj = self._lob_client.letters.create(
                from_address=from_address.to_dict(),
                to_address=to_address.to_dict(),
                file=pdf_bytes,
                file_type="pdf",
                tracking=True if request.appeal_type == "certified" else False,
            )

            logger.info(f"Created Lob letter: {letter_obj.id}")

            return MailResult(
                success=True,
                tracking_number=letter_obj.tracking_number,
                lob_id=letter_obj.id,
                delivery_date=str(letter_obj.expected_delivery_date)
                if letter_obj.expected_delivery_date
                else None,
            )

        except Exception as e:
            logger.error(f"Lob API error: {e}")
            return MailResult(success=False, error_message=str(e))

    async def verify_address(self, address: MailingAddress) -> Dict[str, Any]:
        """
        Verify an address using Lob's address verification.

        Args:
            address: The address to verify

        Returns:
            Dictionary with verification results
        """
        if not self._use_lob:
            return {
                "verified": False,
                "message": "Address verification not configured",
                "deliverability": "UNKNOWN",
            }

        try:
            import lob

            verification = self._lob_client.us_verifications.create(
                primary_line=address.address_line_1,
                secondary_line=address.address_line_2 or "",
                city=address.city,
                state=address.state,
                zip_code=address.zip_code,
            )

            return {
                "verified": True,
                "message": "Address verified",
                "deliverability": getattr(verification, "deliverability", "UNKNOWN"),
                "components": {
                    "primary_line": getattr(
                        verification, "primary_line", address.address_line_1
                    ),
                    "city": getattr(verification, "city", address.city),
                    "state": getattr(verification, "state", address.state),
                    "zip_code": getattr(verification, "zip_code", address.zip_code),
                },
            }

        except Exception as e:
            logger.error(f"Address verification failed: {e}")
            return {
                "verified": False,
                "message": str(e),
                "deliverability": "UNKNOWN",
            }


def get_mail_service(api_key: Optional[str] = None) -> LobMailService:
    """
    Get an instance of the mail service.

    Args:
        api_key: Optional Lob API key. If not provided, reads from environment.

    Returns:
        LobMailService instance
    """
    import os

    if api_key is None:
        api_key = os.environ.get("LOB_API_KEY")

    return LobMailService(api_key)


async def send_appeal_letter(
    citation_number: str,
    user_name: str,
    user_address_line_1: str,
    user_address_line_2: Optional[str],
    user_city: str,
    user_state: str,
    user_zip: str,
    user_email: str,
    letter_text: str,
    agency_name: str,
    appeal_type: str = "certified",
    violation_date: Optional[str] = None,
    vehicle_info: Optional[str] = None,
) -> MailResult:
    """
    Convenience function to send an appeal letter.

    Args:
        citation_number: The citation number
        user_name: User's full name
        user_address_line_1: Street address
        user_address_line_2: Apartment/suite number
        user_city: City
        user_state: State (2-letter code)
        user_zip: ZIP code
        user_email: Email for notifications
        letter_text: The appeal letter content
        agency_name: Agency key for address lookup
        appeal_type: 'certified' or 'standard'
        violation_date: Optional violation date
        vehicle_info: Optional vehicle information

    Returns:
        MailResult with tracking information
    """
    mail_service = get_mail_service()

    request = AppealLetterRequest(
        citation_number=citation_number,
        user_name=user_name,
        user_address_line_1=user_address_line_1,
        user_address_line_2=user_address_line_2,
        user_city=user_city,
        user_state=user_state,
        user_zip=user_zip,
        user_email=user_email,
        letter_text=letter_text,
        agency_name=agency_name,
        agency_address="",  # Will be looked up internally
        appeal_type=appeal_type,
        violation_date=violation_date,
        vehicle_info=vehicle_info,
    )

    return await mail_service.send_appeal_letter(request)
