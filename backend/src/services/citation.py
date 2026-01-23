"""
Citation Validation Service for FIGHTCITYTICKETS.com

Validates parking citation numbers and calculates appeal deadlines across multiple cities.
Implements multi-city support via CityRegistry (Schema 4.3.0) with backward compatibility for SF-only implementation.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Import CityRegistry if available - try multiple import strategies
CITY_REGISTRY_AVAILABLE = False
CityRegistry = Any


def get_city_registry(cities_dir=None):
    return None


AppealMailAddress = Any
PhoneConfirmationPolicy = Any

# Define enum stubs as fallback
AppealMailStatus = Enum("AppealMailStatus", ["COMPLETE", "ROUTES_ELSEWHERE", "MISSING"])

try:
    # Strategy 1: Relative import (works when module is imported)
    from .city_registry import (  # noqa: F401
        AppealMailAddress,  # noqa: F401
        AppealMailStatus,  # noqa: F401
        CityRegistry,  # noqa: F401
        PhoneConfirmationPolicy,  # noqa: F401
        get_city_registry,
    )

    CITY_REGISTRY_AVAILABLE = True
except ImportError:
    try:
        # Strategy 2: Absolute import from src.services (works in script mode)
        import sys
        from pathlib import Path

        # Add parent directory to path
        src_dir = Path(__file__).parent.parent
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
        from services.city_registry import (  # noqa: F401
            AppealMailAddress,  # noqa: F401
            AppealMailStatus,  # noqa: F401
            CityRegistry,  # noqa: F401
            PhoneConfirmationPolicy,  # noqa: F401
            get_city_registry,
        )

        CITY_REGISTRY_AVAILABLE = True
    except ImportError:
        # Strategy 3: Use stubs (fallback)
        CITY_REGISTRY_AVAILABLE = False
        # Stubs already defined above


class CitationAgency(Enum):
    """Parking citation issuing agencies in San Francisco (backward compatibility)."""

    SFMTA = "SFMTA"  # San Francisco Municipal Transportation Agency
    SFPD = "SFPD"  # San Francisco Police Department
    SFMUD = "SFMUD"  # San Francisco Municipal Utility District
    SFSU = "SFSU"  # San Francisco State University
    UNKNOWN = "UNKNOWN"


@dataclass
class CitationValidationResult:
    """Result of citation validation with multi-city support."""

    is_valid: bool
    citation_number: str
    agency: CitationAgency  # Backward compatibility
    deadline_date: Optional[str] = None
    days_remaining: Optional[int] = None
    is_past_deadline: bool = False
    is_urgent: bool = False
    error_message: Optional[str] = None
    formatted_citation: Optional[str] = None

    # New fields for multi-city support
    city_id: Optional[str] = None
    section_id: Optional[str] = None
    appeal_deadline_days: int = 21  # Default SF deadline
    phone_confirmation_required: bool = False
    phone_confirmation_policy: Optional[Dict[str, Any]] = None

    # Clerical defect detection (not legal conclusions)
    # Indicates potential documentation issues (missing date, mismatched info, etc.)
    clerical_defect_detected: bool = False
    clerical_defect_description: Optional[str] = None


@dataclass
class CitationInfo:
    """Complete citation information for appeal processing."""

    citation_number: str
    agency: CitationAgency  # Backward compatibility
    violation_date: Optional[str]
    license_plate: Optional[str]
    vehicle_info: Optional[str]
    deadline_date: Optional[str]
    days_remaining: Optional[int]
    is_within_appeal_window: bool
    can_appeal_online: bool = False
    online_appeal_url: Optional[str] = None

    # New fields for multi-city support
    city_id: Optional[str] = None
    section_id: Optional[str] = None
    appeal_mail_address: Optional[Dict[str, Any]] = None
    routing_rule: Optional[str] = None
    phone_confirmation_required: bool = False
    phone_confirmation_policy: Optional[Dict[str, Any]] = None
    appeal_deadline_days: int = 21  # Default SF deadline


class CitationValidator:
    """Validates parking citations across multiple cities and calculates appeal deadlines."""

    # SFMTA citation number patterns (backward compatibility)
    SFMTA_PATTERN = re.compile(r"^9\d{8}$")
    SFPD_PATTERN = re.compile(r"^[A-Z0-9]{6,10}$")
    SFSU_PATTERN = re.compile(r"^(SFSU|CAMPUS|UNIV)[A-Z0-9]*$", re.IGNORECASE)

    # Minimum and maximum citation lengths (global)
    MIN_LENGTH = 6
    MAX_LENGTH = 12

    # Default appeal deadline (21 days for SF)
    DEFAULT_APPEAL_DEADLINE_DAYS = 21

    # Default cities directory relative to this file
    DEFAULT_CITIES_DIR = Path(__file__).parent.parent.parent.parent / "cities"

    # Singleton instance for class method compatibility
    _default_validator = None

    def __init__(self, cities_dir: Optional[Path] = None):
        """Initialize citation validator with optional CityRegistry."""
        self.cities_dir = cities_dir or self.DEFAULT_CITIES_DIR
        self.city_registry = None

        if CITY_REGISTRY_AVAILABLE:
            try:
                self.city_registry = get_city_registry(self.cities_dir)
            except Exception as e:
                print(f"Warning: CityRegistry initialization failed: {e}")
                print("   Falling back to SF-only validation.")

    @classmethod
    def _get_default_validator(cls) -> "CitationValidator":
        """Get or create the default validator instance."""
        if cls._default_validator is None:
            cls._default_validator = cls()
        return cls._default_validator

    @classmethod
    def validate_citation_format(
        cls, citation_number: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate citation number format (basic length and format checks).

        Args:
            citation_number: The citation number to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not citation_number:
            return False, "Citation number is required"

        # Clean the citation number
        clean_number = citation_number.strip().upper()
        clean_number = re.sub(r"[\s\-\.]", "", clean_number)

        # Check length
        if len(clean_number) < cls.MIN_LENGTH:
            return (
                False,
                f"Citation number too short (minimum {cls.MIN_LENGTH} characters)",
            )

        if len(clean_number) > cls.MAX_LENGTH:
            return (
                False,
                f"Citation number too long (maximum {cls.MAX_LENGTH} characters)",
            )

        # Check if it contains at least some alphanumeric characters
        if not re.search(r"[A-Z0-9]", clean_number):
            return False, "Invalid citation number format"

        # Check for suspicious patterns (all same character, sequential, etc.)
        if clean_number == clean_number[0] * len(clean_number):
            return False, "Invalid citation number pattern"

        return True, None

    @classmethod
    def identify_agency(cls, citation_number: str) -> CitationAgency:
        """
        Identify the issuing agency based on citation number format.
        (Backward compatibility for SF-only validation)

        Args:
            citation_number: The cleaned citation number

        Returns:
            CitationAgency enum
        """
        clean_number = re.sub(r"[\s\-\.]", "", citation_number.strip().upper())

        # SFMTA citations typically start with 9 and are 9 digits
        if cls.SFMTA_PATTERN.match(clean_number):
            return CitationAgency.SFMTA

        # SFPD citations often have letters and numbers
        if cls.SFPD_PATTERN.match(clean_number):
            # Check if it looks like SFPD format
            if any(c.isalpha() for c in clean_number):
                return CitationAgency.SFPD

        # SFSU citations may start with campus identifiers
        if cls.SFSU_PATTERN.match(clean_number):
            return CitationAgency.SFSU

        # Default to SFMTA for numeric citations (most common)
        if clean_number.isdigit():
            return CitationAgency.SFMTA

        return CitationAgency.UNKNOWN

    def _calculate_appeal_deadline(
        self, violation_date: str, appeal_deadline_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate appeal deadline with city-specific deadline days.

        Args:
            violation_date: Date string in YYYY-MM-DD format
            appeal_deadline_days: Optional override for deadline days (uses city-specific if None)

        Returns:
            Dictionary with deadline information
        """
        try:
            violation_dt = datetime.strptime(violation_date, "%Y-%m-%d")
            deadline_days = appeal_deadline_days or self.DEFAULT_APPEAL_DEADLINE_DAYS
            deadline_dt = violation_dt + timedelta(days=deadline_days)
            today = datetime.now()

            days_remaining = (deadline_dt - today).days

            return {
                "violation_date": violation_date,
                "deadline_date": deadline_dt.strftime("%Y-%m-%d"),
                "days_remaining": max(0, days_remaining),
                "is_past_deadline": days_remaining < 0,
                "is_urgent": 0 <= days_remaining <= 3,
                "deadline_timestamp": deadline_dt.isoformat(),
            }
        except ValueError as e:
            raise ValueError(
                f"Invalid date format: {violation_date}. Use YYYY-MM-DD"
            ) from e

    def _match_citation_to_city(
        self, citation_number: str, city_id: Optional[str] = None
    ) -> Optional[Tuple[str, str, Dict[str, Any]]]:
        """
        Match citation number to city and section using CityRegistry.

        Args:
            citation_number: Citation number to match

        Returns:
            Tuple of (city_id, section_id, city_config_dict) or None if no match
        """
        if not self.city_registry:
            return None

        match = self.city_registry.match_citation(citation_number, city_id_hint=city_id)
        if not match:
            return None

        city_id, section_id = match
        city_config = self.city_registry.get_city_config(city_id)
        if not city_config:
            return None

        return city_id, section_id, city_config.to_dict()

    def _validate_citation(
        self,
        citation_number: str,
        violation_date: Optional[str] = None,
        license_plate: Optional[str] = None,
        city_id: Optional[str] = None,
    ) -> CitationValidationResult:
        """
        Complete citation validation with multi-city matching.

        Args:
            citation_number: The citation number to validate
            violation_date: Optional violation date for deadline calculation
            license_plate: Optional license plate for additional validation

        Returns:
            CitationValidationResult with all validation details
        """
        # Step 1: Basic format validation
        is_valid_format, error_msg = self.validate_citation_format(citation_number)

        if not is_valid_format:
            return CitationValidationResult(
                is_valid=False,
                citation_number=citation_number,
                agency=CitationAgency.UNKNOWN,
                error_message=error_msg,
            )

        # Step 2: Clean and format citation number
        clean_number = re.sub(r"[\s\-\.]", "", citation_number.strip().upper())
        formatted_citation = clean_number

        # Add dashes for readability if it's a long number
        if len(clean_number) >= 9:
            formatted_citation = (
                f"{clean_number[:3]}-{clean_number[3:6]}-{clean_number[6:]}"
            )

        # Step 3: Try to match to city using CityRegistry
        city_match = self._match_citation_to_city(clean_number, city_id)

        # Step 4: Backward compatibility - identify SF agency if no city match
        if city_match:
            city_id, section_id, city_config = city_match
            agency = CitationAgency.UNKNOWN  # We'll map section_id to agency for SF

            # Map SF section IDs to agencies for backward compatibility
            if city_id == "s":
                if section_id == "sfmta":
                    agency = CitationAgency.SFMTA
                elif section_id == "sfpd":
                    agency = CitationAgency.SFPD
                elif section_id == "sfsu":
                    agency = CitationAgency.SFSU
                elif section_id == "sfmud":
                    agency = CitationAgency.SFMUD

            # Get city-specific configuration
            appeal_deadline_days = city_config.get(
                "appeal_deadline_days", self.DEFAULT_APPEAL_DEADLINE_DAYS
            )

            # Get phone confirmation policy
            phone_confirmation_policy = None
            phone_confirmation_required = False
            if self.city_registry:
                policy = self.city_registry.get_phone_confirmation_policy(
                    city_id, section_id
                )
                if policy:
                    phone_confirmation_policy = policy.to_dict()
                    phone_confirmation_required = policy.required

        else:
            # No city match, fall back to SF-only validation
            city_id = None
            section_id = None
            agency = self.identify_agency(clean_number)
            appeal_deadline_days = self.DEFAULT_APPEAL_DEADLINE_DAYS
            phone_confirmation_policy = None
            phone_confirmation_required = False

        # Step 5: Calculate deadline if violation date provided
        deadline_date = None
        days_remaining = None
        is_past_deadline = False
        is_urgent = False
        error_msg = None

        if violation_date:
            try:
                deadline_info = self._calculate_appeal_deadline(
                    violation_date, appeal_deadline_days
                )
                deadline_date = deadline_info["deadline_date"]
                days_remaining = deadline_info["days_remaining"]
                is_past_deadline = deadline_info["is_past_deadline"]
                is_urgent = deadline_info["is_urgent"]
            except ValueError as e:
                # Date format error - citation is still valid, just can't calculate deadline
                error_msg = str(e)

        # Step 6: Additional validation for license plate (if provided)
        if license_plate:
            # Basic license plate validation
            license_plate_clean = license_plate.strip().upper()
            if len(license_plate_clean) < 2 or len(license_plate_clean) > 8:
                error_msg = "Invalid license plate format"

        return CitationValidationResult(
            is_valid=True,
            citation_number=citation_number,
            agency=agency,
            deadline_date=deadline_date,
            days_remaining=days_remaining,
            is_past_deadline=is_past_deadline,
            is_urgent=is_urgent,
            error_message=error_msg,
            formatted_citation=formatted_citation,
            city_id=city_id,
            section_id=section_id,
            appeal_deadline_days=appeal_deadline_days,
            phone_confirmation_required=phone_confirmation_required,
            phone_confirmation_policy=phone_confirmation_policy,
        )

    def _get_citation_info(
        self,
        citation_number: str,
        violation_date: Optional[str] = None,
        license_plate: Optional[str] = None,
        vehicle_info: Optional[str] = None,
    ) -> CitationInfo:
        """
        Get complete citation information for appeal processing.

        Args:
            citation_number: The citation number
            violation_date: Violation date in YYYY-MM-DD format
            license_plate: Vehicle license plate
            vehicle_info: Additional vehicle information

        Returns:
            CitationInfo object with all details
        """
        # Validate the citation
        validation = self._validate_citation(
            citation_number, violation_date, license_plate
        )

        if not validation.is_valid:
            raise ValueError(f"Invalid citation: {validation.error_message}")

        # Check if within appeal window
        is_within_appeal_window = (
            validation.deadline_date is not None and not validation.is_past_deadline
        )

        # Determine if online appeal is available from city configuration
        can_appeal_online = False
        online_appeal_url = None
        if validation.city_id and self.city_registry:
            city_config = self.city_registry.get_city_config(validation.city_id)
            if city_config:
                can_appeal_online = city_config.online_appeal_available
                online_appeal_url = city_config.online_appeal_url

        # Get additional city-specific information if we have a match
        appeal_mail_address = None
        routing_rule = None
        phone_confirmation_policy = validation.phone_confirmation_policy
        phone_confirmation_required = validation.phone_confirmation_required

        if validation.city_id and self.city_registry:
            # Get mailing address
            mail_address = self.city_registry.get_mail_address(
                validation.city_id, validation.section_id
            )
            if mail_address:
                appeal_mail_address = mail_address.to_dict()

            # Get routing rule
            routing_rule_obj = self.city_registry.get_routing_rule(
                validation.city_id, validation.section_id
            )
            if routing_rule_obj:
                routing_rule = routing_rule_obj.value

            # Get phone confirmation policy if not already set
            if not phone_confirmation_policy:
                policy = self.city_registry.get_phone_confirmation_policy(
                    validation.city_id, validation.section_id
                )
                if policy:
                    phone_confirmation_policy = policy.to_dict()
                    phone_confirmation_required = policy.required

        return CitationInfo(
            citation_number=citation_number,
            agency=validation.agency,
            violation_date=violation_date,
            license_plate=license_plate,
            vehicle_info=vehicle_info,
            deadline_date=validation.deadline_date,
            days_remaining=validation.days_remaining,
            is_within_appeal_window=is_within_appeal_window,
            can_appeal_online=can_appeal_online,
            online_appeal_url=online_appeal_url,
            city_id=validation.city_id,
            section_id=validation.section_id,
            appeal_mail_address=appeal_mail_address,
            routing_rule=routing_rule,
            phone_confirmation_required=phone_confirmation_required,
            phone_confirmation_policy=phone_confirmation_policy,
            appeal_deadline_days=validation.appeal_deadline_days,
        )

    # Class methods for backward compatibility
    @classmethod
    def calculate_appeal_deadline(cls, violation_date: str) -> Dict[str, Any]:
        """Class method wrapper for calculate_appeal_deadline."""
        return cls._get_default_validator()._calculate_appeal_deadline(violation_date)

    @classmethod
    def validate_citation(
        cls,
        citation_number: str,
        violation_date: Optional[str] = None,
        license_plate: Optional[str] = None,
        city_id: Optional[str] = None,
    ) -> CitationValidationResult:
        """Class method wrapper for validate_citation."""
        return cls._get_default_validator()._validate_citation(
            citation_number, violation_date, license_plate, city_id
        )

    @classmethod
    def get_citation_info(
        cls,
        citation_number: str,
        violation_date: Optional[str] = None,
        license_plate: Optional[str] = None,
        vehicle_info: Optional[str] = None,
    ) -> CitationInfo:
        """Class method wrapper for get_citation_info."""
        return cls._get_default_validator()._get_citation_info(
            citation_number, violation_date, license_plate, vehicle_info
        )


# Helper functions for common operations (backward compatibility)
def validate_citation_number(citation_number: str) -> Tuple[bool, Optional[str]]:
    """Simple wrapper for basic citation validation."""
    return CitationValidator.validate_citation_format(citation_number)


def get_appeal_deadline(violation_date: str) -> Dict[str, Any]:
    """Simple wrapper for deadline calculation."""
    return CitationValidator.calculate_appeal_deadline(violation_date)


def get_appeal_method_messaging(
    city_id: Optional[str],
    section_id: Optional[str],
    city_registry: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Get messaging about appeal methods for a given city/section.

    Returns information about online appeal availability and guidance for users.
    Even though our service only provides mail appeals, we inform users if the city
    also accepts online appeals as an alternative option.

    Args:
        city_id: City identifier (e.g., 's', 'la', 'nyc')
        section_id: Section identifier (e.g., 'sfmta', 'lapd')
        city_registry: Optional CityRegistry instance

    Returns:
        Dictionary with messaging and appeal method information
    """
    if not city_id or not city_registry:
        return {
            "online_appeal_available": False,
            "message": "Mail appeal required. Our service ensures proper formatting and delivery.",
            "recommended_method": "mail",
            "notes": "Most governing bodies require mailed appeals for accessibility.",
        }

    try:
        city_config = city_registry.get_city_config(city_id)
        if not city_config:
            return {
                "online_appeal_available": False,
                "message": "Mail appeal required. Our service ensures proper formatting and delivery.",
                "recommended_method": "mail",
                "notes": "Most governing bodies require mailed appeals for accessibility.",
            }

        online_available = city_config.online_appeal_available
        online_url = city_config.online_appeal_url

        if online_available:
            return {
                "online_appeal_available": True,
                "online_appeal_url": online_url,
                "message": "This city accepts online appeals, but our mail service provides guaranteed delivery and professional formatting.",
                "recommended_method": "mail",
                "alternative_method": "online",
                "notes": "Mail appeals are often given more consideration and have guaranteed delivery confirmation.",
            }
        else:
            return {
                "online_appeal_available": False,
                "message": "This city requires mailed appeals. Our service ensures proper formatting and timely delivery.",
                "recommended_method": "mail",
                "notes": "Mailed appeals are universally accepted and provide physical proof of submission.",
            }

    except Exception:
        return {
            "online_appeal_available": False,
            "message": "Mail appeal required. Our service ensures proper formatting and delivery.",
            "recommended_method": "mail",
            "notes": "Most governing bodies require mailed appeals for accessibility.",
        }


# Example usage and testing
if __name__ == "__main__":
    print("TESTING: Testing Citation Validation Service with CityRegistry")
    print("=" * 50)

    # Create a validator with cities directory
    validator = CitationValidator()

    # Test cases including SF citations that should match
    test_cases = [
        (
            "912345678",
            "2024-01-15",
            "ABC123",
        ),  # Valid SFMTA (should match us-ca-san_francisco.json)
        (
            "SF123456",
            "2024-01-15",
            "TEST123",
        ),  # SFPD-like (should match us-ca-san_francisco.json)
        (
            "SFSU12345",
            "2024-01-15",
            "CAMPUS",
        ),  # SFSU (should match us-ca-san_francisco.json)
        ("123456", "2024-01-15", "XYZ789"),  # Too short (no city match)
        ("ABCDEFGHIJKLMNOP", "2024-01-15", "TEST"),  # Too long (no city match)
        ("", "2024-01-15", "TEST"),  # Empty
        ("912-345-678", "2024-01-15", "CAL123"),  # With dashes (should match SFMTA)
    ]

    for citation, date, plate in test_cases:
        print(f"\nCITATION: Citation: {citation}")
        print(f"   Date: {date}, Plate: {plate}")

        try:
            result = validator._validate_citation(citation, date, plate)
            if result.is_valid:
                print(f"   OK: VALID - Agency: {result.agency.value}")
                print(f"      Formatted: {result.formatted_citation}")
                if result.city_id:
                    print(f"      City: {result.city_id}, Section: {result.section_id}")
                    print(f"      Appeal Deadline Days: {result.appeal_deadline_days}")
                    print(
                        f"      Phone Confirmation Required: {result.phone_confirmation_required}"
                    )
                if result.deadline_date:
                    print(f"      Deadline: {result.deadline_date}")
                    print(f"      Days remaining: {result.days_remaining}")
                    print(f"      Urgent: {result.is_urgent}")
            else:
                print(f"   FAIL: INVALID - {result.error_message}")
        except Exception as e:
            print(f"   WARN: ERROR - {str(e)}")

    # Test CitationInfo retrieval for a valid citation
    print("\n" + "=" * 50)
    print("TESTING: Testing CitationInfo Retrieval")
    print("=" * 50)

    try:
        info = validator._get_citation_info(
            citation_number="912345678",
            violation_date="2024-01-15",
            license_plate="ABC123",
            vehicle_info="Toyota Camry",
        )
        print(f"CITATION: Citation: {info.citation_number}")
        print(f"   Agency: {info.agency.value}")
        print(f"   City: {info.city_id}, Section: {info.section_id}")
        print(f"   Within Appeal Window: {info.is_within_appeal_window}")
        print(f"   Can Appeal Online: {info.can_appeal_online}")
        print(f"   Appeal Deadline Days: {info.appeal_deadline_days}")
        print(f"   Phone Confirmation Required: {info.phone_confirmation_required}")
        if info.appeal_mail_address:
            print(
                f"   Appeal Mail Address Status: {info.appeal_mail_address.get('status')}"
            )
        if info.routing_rule:
            print(f"   Routing Rule: {info.routing_rule}")
    except Exception as e:
        print(f"   WARN: ERROR - {str(e)}")

    print("\n" + "=" * 50)
    print("OK: Citation Validation Service Test Complete")
