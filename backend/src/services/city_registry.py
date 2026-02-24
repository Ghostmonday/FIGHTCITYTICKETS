"""
City Registry Service for Fight City Tickets

Handles multi-city configuration management for 37 cities.
Loads, validates, and provides routing for citation patterns and mailing addresses
across multiple jurisdictions.
Implements Schema 4.3.0 with strict validation rules.

CITY EXPANSION STRATEGY (see docs/MARKET_STRATEGY.md):
======================================================

TIER 1 - HIGH PRIORITY (Easy entry, high volume):
  - NYC (us-ny-new_york) ✓ Active - simple checkbox, digital signatures
  - Boston (us-ma-boston) TODO - easy to add, digital signatures accepted

TIER 2 - CAUTION (Moderate risk):
  - San Francisco (us-ca-san_francisco) ✓ Active - UPL risk if AI drafts arguments
  - Los Angeles (us-ca-los_angeles) ✓ Active - same UPL risk

TIER 3 - BLOCKED (Do not enter):
  - Chicago (us-il-chicago) - attorney required for fleet
  - D.C. - Power of Attorney requirement
  - Any city requiring wet-ink signatures

SCRIVENER DEFENSE:
  This service is a "document preparation service" only.
  We transcribe user facts onto municipal forms - NO legal advice.

TODO: Add Boston (us-ma-boston)
TODO: Add eligibility filter to get_all_cities()
TODO: Add is_eligible_for_appeals(city_id) method
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

# Set up logger
logger = logging.getLogger(__name__)

# Cache TTL for city configs (1 hour)
CITY_CONFIG_CACHE_TTL = 3600


class AppealMailStatus(str, Enum):
    """Status of appeal mail address."""

    COMPLETE = "complete"
    ROUTES_ELSEWHERE = "routes_elsewhere"
    MISSING = "missing"


# Import SchemaAdapter for transforming non-Schema 4.3.0 files
if TYPE_CHECKING:
    from .schema_adapter import SchemaAdapter as SchemaAdapterType
    SchemaAdapter = SchemaAdapterType  # type: ignore[misc]
else:
    try:
        from .schema_adapter import SchemaAdapter
        SCHEMA_ADAPTER_AVAILABLE = True
    except ImportError:
        SCHEMA_ADAPTER_AVAILABLE = False
        logger.warning(f"SchemaAdapter not available - will only load Schema 4.3.0 files")


class RoutingRule(str, Enum):
    """Routing rule types."""

    DIRECT = "direct"
    ROUTES_TO_SECTION = "routes_to_section"
    SEPARATE_ADDRESS_REQUIRED = "separate_address_required"


class Jurisdiction(str, Enum):
    """Jurisdiction types."""

    CITY = "city"
    COUNTY = "county"
    STATE = "state"
    CAMPUS = "campus"
    REGIONAL = "regional"
    SPECIAL_DISTRICT = "special_district"
    DISTRICT = "district"


class CityStatus(str, Enum):
    """Status of city support."""

    ACTIVE = "active"
    CAUTION = "caution"
    BLOCKED = "blocked"


@dataclass
class AppealMailAddress:
    """Complete mailing address for appeal submissions."""

    status: AppealMailStatus
    department: Optional[str] = None
    attention: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    routes_to_section_id: Optional[str] = None
    missing_fields: Optional[List[str]] = None
    missing_reason: Optional[str] = None

    def is_complete(self) -> bool:
        """Check if this is a complete mailing address."""
        return self.status == AppealMailStatus.COMPLETE and all(
            [
                self.department,
                self.address1,
                self.city,
                self.state,
                self.zip,
                self.country,
            ]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result: Dict[str, Any] = {"status": self.status.value}

        if self.status == AppealMailStatus.COMPLETE:
            # Only include non-None values for complete addresses
            if self.department:
                result["department"] = self.department
            if self.attention:
                result["attention"] = self.attention
            if self.address1:
                result["address1"] = self.address1
            if self.address2:
                result["address2"] = self.address2
            if self.city:
                result["city"] = self.city
            if self.state:
                result["state"] = self.state
            if self.zip:
                result["zip"] = self.zip
            if self.country:
                result["country"] = self.country
        elif self.status == AppealMailStatus.ROUTES_ELSEWHERE:
            result["routes_to_section_id"] = self.routes_to_section_id  # type: ignore[assignment]
        elif self.status == AppealMailStatus.MISSING:
            result["missing_fields"] = self.missing_fields  # type: ignore[assignment]
            result["missing_reason"] = self.missing_reason  # type: ignore[assignment]
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppealMailAddress":
        """Create AppealMailAddress from dictionary."""
        status = AppealMailStatus(data["status"])

        if status == AppealMailStatus.COMPLETE:
            return cls(
                status=status,
                department=data.get("department"),
                attention=data.get("attention"),
                address1=data.get("address1"),
                address2=data.get("address2"),
                city=data.get("city"),
                state=data.get("state"),
                zip=data.get("zip"),
                country=data.get("country"),
            )
        elif status == AppealMailStatus.ROUTES_ELSEWHERE:
            return cls(
                status=status, routes_to_section_id=data.get("routes_to_section_id")
            )
        else:  # MISSING
            return cls(
                status=status,
                missing_fields=data.get("missing_fields"),
                missing_reason=data.get("missing_reason"),
            )


@dataclass
class PhoneConfirmationPolicy:
    """Phone confirmation policy for a city."""

    required: bool = False
    phone_format_regex: Optional[str] = None
    confirmation_message: Optional[str] = None
    confirmation_deadline_hours: Optional[int] = None
    phone_number_examples: Optional[List[str]] = None

    def validate_phone(self, phone_number: str) -> Tuple[bool, Optional[str]]:
        """Validate phone number against format regex."""
        if not self.required:
            return True, None

        if not self.phone_format_regex:
            return True, None

        try:
            pattern = re.compile(self.phone_format_regex)
            if pattern.match(phone_number):
                return True, None
            else:
                error = "Phone number does not match required format"
                if self.phone_number_examples:
                    error += f". Examples: {', '.join(self.phone_number_examples)}"
                return False, error
        except re.error:
            logger.warning(f"Invalid regex pattern: {self.phone_format_regex}")
            return True, None  # Don't fail validation due to bad regex

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result: Dict[str, Any] = {"required": self.required}
        if self.phone_format_regex:
            result["phone_format_regex"] = self.phone_format_regex  # type: ignore[assignment]
        if self.confirmation_message:
            result["confirmation_message"] = self.confirmation_message  # type: ignore[assignment]
        if self.confirmation_deadline_hours:
            result["confirmation_deadline_hours"] = self.confirmation_deadline_hours  # type: ignore[assignment]
        if self.phone_number_examples:
            result["phone_number_examples"] = self.phone_number_examples  # type: ignore[assignment]
        return result


@dataclass
class CitationPattern:
    """Citation pattern with regex matching."""

    regex: str
    section_id: str
    description: str
    compiled_regex: re.Pattern = field(init=False)
    example_numbers: Optional[List[str]] = None

    def __post_init__(self):
        """Compile regex after initialization."""
        try:
            self.compiled_regex = re.compile(self.regex)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{self.regex}': {e}") from e

    def matches(self, citation_number: str) -> bool:
        """Check if citation number matches this pattern."""
        return bool(self.compiled_regex.match(citation_number.strip()))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result: Dict[str, Any] = {
            "regex": self.regex,
            "section_id": self.section_id,
            "description": self.description,
        }
        if self.example_numbers:
            result["example_numbers"] = self.example_numbers  # type: ignore[assignment]
        return result


@dataclass
class CitySection:
    """Section within a city (e.g., SFMTA, SFPD)."""

    section_id: str
    name: str
    appeal_mail_address: Optional[AppealMailAddress] = None
    routing_rule: RoutingRule = RoutingRule.DIRECT
    phone_confirmation_policy: Optional[PhoneConfirmationPolicy] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result: Dict[str, Any] = {
            "section_id": self.section_id,
            "name": self.name,
            "routing_rule": self.routing_rule.value,
        }
        if self.appeal_mail_address:
            result["appeal_mail_address"] = self.appeal_mail_address.to_dict()  # type: ignore[assignment]
        if self.phone_confirmation_policy:
            result["phone_confirmation_policy"] = (  # type: ignore[assignment]
                self.phone_confirmation_policy.to_dict()
            )
        return result


@dataclass
class VerificationMetadata:
    """Verification metadata for city configuration."""

    last_updated: str
    source: str
    confidence_score: float = 1.0
    notes: Optional[str] = None
    verified_by: Optional[str] = None
    verification_date: Optional[str] = None
    verified_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result = {
            "last_updated": self.last_updated,
            "source": self.source,
            "confidence_score": self.confidence_score,
        }
        if self.notes:
            result["notes"] = self.notes
        if self.verified_by:
            result["verified_by"] = self.verified_by
        return result


@dataclass
class CityConfiguration:
    """Complete city configuration for Schema 4.3.0."""

    city_id: str
    name: str
    jurisdiction: Jurisdiction
    citation_patterns: List[CitationPattern]
    appeal_mail_address: AppealMailAddress
    phone_confirmation_policy: PhoneConfirmationPolicy
    routing_rule: RoutingRule
    sections: Dict[str, CitySection]
    verification_metadata: VerificationMetadata
    status: CityStatus = CityStatus.ACTIVE
    timezone: str = "America/Los_Angeles"
    appeal_deadline_days: int = 21
    online_appeal_available: bool = False
    online_appeal_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "city_id": self.city_id,
            "name": self.name,
            "jurisdiction": self.jurisdiction.value,
            "status": self.status.value,
            "citation_patterns": [p.to_dict() for p in self.citation_patterns],
            "appeal_mail_address": self.appeal_mail_address.to_dict(),
            "phone_confirmation_policy": self.phone_confirmation_policy.to_dict(),
            "routing_rule": self.routing_rule.value,
            "sections": {k: v.to_dict() for k, v in self.sections.items()},
            "verification_metadata": self.verification_metadata.to_dict(),
            "timezone": self.timezone,
            "appeal_deadline_days": self.appeal_deadline_days,
            "online_appeal_available": self.online_appeal_available,
            "online_appeal_url": self.online_appeal_url,
        }


class CityRegistry:
    """Main registry for managing multi-city configurations."""

    def __init__(self, cities_dir: Optional[Union[str, Path]] = None):
        """Initialize city registry."""
        if cities_dir is None:
            self.cities_dir = Path(__file__).parent.parent.parent / "cities"
        elif isinstance(cities_dir, str):
            self.cities_dir = Path(cities_dir)
        else:
            self.cities_dir = cities_dir
        self.city_configs: Dict[str, CityConfiguration] = {}
        self._citation_cache: Dict[
            str, Tuple[str, str]
        ] = {}  # citation -> (city_id, section_id)

    def load_cities(self) -> None:
        """Load all city configurations from JSON files."""
        if not self.cities_dir.exists():
            logger.warning(f"Cities directory not found: {self.cities_dir}")
            return

        # Load all JSON files, not just us-*.json, but skip phase1 files
        json_files = [
            f
            for f in self.cities_dir.glob("*.json")
            if not f.name.endswith("_phase1.json")
        ]
        if not json_files:
            logger.warning(f"No JSON files found in {self.cities_dir}")
            return

        logger.info(f"Found {len(json_files)} JSON files (excluding phase1 files)")

        loaded = 0
        errors = 0
        skipped = 0
        schema_adapter = None

        if SCHEMA_ADAPTER_AVAILABLE:
            schema_adapter = SchemaAdapter()
            logger.info(
                "SchemaAdapter available for transforming non-Schema 4.3.0 files"
            )
        else:
            logger.warning(
                "SchemaAdapter not available - will only load Schema 4.3.0 files"
            )

        # Track loaded city_ids to avoid duplicates
        loaded_city_ids = set()

        for json_file in json_files:
            try:
                # Check if file is already in Schema 4.3.0 format (us- prefix)
                is_schema_43 = json_file.name.startswith("us-")

                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Get city_id from data (not filename)
                city_id = data.get("city_id", json_file.stem)

                # Check for duplicates
                if city_id in loaded_city_ids:
                    logger.info(
                        "Skipping duplicate city_id: {city_id} from {json_file.name}"
                    )
                    skipped += 1
                    continue

                # Determine if file needs transformation
                needs_transformation = False
                if not is_schema_43 and (
                    "citation_patterns" not in data or "appeal_mail_address" not in data
                ):
                    # Likely not Schema 4.3.0 format
                    needs_transformation = True
                    logger.info(
                        "File {json_file.name} appears to need Schema 4.3.0 transformation"
                    )

                if needs_transformation and schema_adapter:
                    # Transform to Schema 4.3.0
                    try:
                        result = schema_adapter.adapt_city_file(
                            json_file, None
                        )  # Transform in memory
                        if result.success:
                            data = result.transformed_data
                            # Update city_id from transformed data
                            city_id = data.get("city_id", city_id)
                            logger.info(
                                "Successfully transformed {json_file.name} to Schema 4.3.0, city_id: {city_id}"
                            )
                        else:
                            error_msg = "; ".join(result.errors) if result.errors else "Unknown transformation error"
                            logger.error(
                                "Failed to transform {json_file.name}: {error_msg}"
                            )
                            errors += 1
                            continue
                    except Exception as e:
                        logger.error(
                            "Schema transformation failed for {json_file.name}: {e}"
                        )
                        errors += 1
                        continue
                elif needs_transformation and not schema_adapter:
                    logger.warning(
                        "Skipping {json_file.name} - needs Schema 4.3.0 transformation but adapter unavailable"
                    )
                    skipped += 1
                    continue

                # Load configuration from (potentially transformed) data
                config = self._load_city_config_from_data(data, json_file)
                validation_errors = self._validate_city_config(config)

                if validation_errors:
                    logger.error(
                        "Validation errors for {city_id}: {validation_errors}"
                    )
                    errors += 1
                    continue

                self.city_configs[city_id] = config
                self._build_citation_cache_for_city(city_id, config)
                loaded_city_ids.add(city_id)
                loaded += 1
                logger.info(f"Loaded city configuration: {city_id}")

            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}")
                errors += 1

        logger.info(
            "Loaded {loaded} city configurations, {errors} errors, {skipped} skipped"
        )

    def _load_city_config(self, json_file: Path) -> CityConfiguration:
        """Load a single city configuration from JSON file."""
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self._load_city_config_from_data(data, json_file)

    def _load_city_config_from_data(
        self, data: Dict[str, Any], json_file: Optional[Path] = None
    ) -> CityConfiguration:
        """Load city configuration from already parsed JSON data."""
        # Build citation patterns
        citation_patterns = []
        for pattern_data in data.get("citation_patterns", []):
            pattern = CitationPattern(
                regex=pattern_data["regex"],
                section_id=pattern_data["section_id"],
                description=pattern_data["description"],
                example_numbers=pattern_data.get("example_numbers"),
            )
            citation_patterns.append(pattern)

        # Build sections
        sections = {}
        for section_id, section_data in data.get("sections", {}).items():
            appeal_mail_address = None
            if "appeal_mail_address" in section_data:
                appeal_mail_address = AppealMailAddress.from_dict(
                    section_data["appeal_mail_address"]
                )

            phone_confirmation_policy = None
            if "phone_confirmation_policy" in section_data:
                policy_data = section_data["phone_confirmation_policy"]
                phone_confirmation_policy = PhoneConfirmationPolicy(
                    required=policy_data.get("required", False),
                    phone_format_regex=policy_data.get("phone_format_regex"),
                    confirmation_message=policy_data.get("confirmation_message"),
                    confirmation_deadline_hours=policy_data.get(
                        "confirmation_deadline_hours"
                    ),
                    phone_number_examples=policy_data.get("phone_number_examples"),
                )

            section = CitySection(
                section_id=section_id,
                name=section_data["name"],
                appeal_mail_address=appeal_mail_address,
                routing_rule=RoutingRule(section_data.get("routing_rule", "direct")),
                phone_confirmation_policy=phone_confirmation_policy,
            )
            sections[section_id] = section

        # Build main configuration
        return CityConfiguration(
            city_id=data["city_id"],
            name=data["name"],
            jurisdiction=Jurisdiction(data["jurisdiction"]),
            status=CityStatus(data.get("status", "active")),
            citation_patterns=citation_patterns,
            appeal_mail_address=AppealMailAddress.from_dict(
                data["appeal_mail_address"]
            ),
            phone_confirmation_policy=PhoneConfirmationPolicy(
                **data["phone_confirmation_policy"]
            ),
            routing_rule=RoutingRule(data["routing_rule"]),
            sections=sections,
            verification_metadata=VerificationMetadata(**data["verification_metadata"]),
            timezone=data.get("timezone", "America/Los_Angeles"),
            appeal_deadline_days=data.get("appeal_deadline_days", 21),
            online_appeal_available=data.get("online_appeal_available", False),
            online_appeal_url=data.get("online_appeal_url"),
        )

    def _validate_city_config(self, config: CityConfiguration) -> List[str]:
        """Validate city configuration against Schema 4.3.0 rules."""
        errors = []

        # Check required fields are not empty
        if not config.city_id or config.city_id.strip() == "":
            errors.append("city_id is required and cannot be empty")

        if not config.name or config.name.strip() == "":
            errors.append("name is required and cannot be empty")

        # Validate citation patterns
        if not config.citation_patterns:
            errors.append("At least one citation pattern is required")

        for i, pattern in enumerate(config.citation_patterns):
            if not pattern.section_id or pattern.section_id.strip() == "":
                errors.append("Citation pattern {i}: section_id is required")
            if pattern.section_id not in config.sections:
                errors.append(
                    "Citation pattern {i}: section_id '{pattern.section_id}' not found in sections"
                )

        # Validate appeal mail address union rules
        if config.appeal_mail_address.status == AppealMailStatus.COMPLETE:
            required_fields = [
                "department",
                "address1",
                "city",
                "state",
                "zip",
                "country",
            ]
            for field_name in required_fields:
                field_value = getattr(config.appeal_mail_address, field_name)
                if not field_value or field_value.strip() == "":
                    errors.append(
                        "Complete appeal mail address requires non-empty {field_name}"
                    )

        elif config.appeal_mail_address.status == AppealMailStatus.ROUTES_ELSEWHERE:
            if not config.appeal_mail_address.routes_to_section_id:
                errors.append("routes_elsewhere status requires routes_to_section_id")
            elif config.appeal_mail_address.routes_to_section_id not in config.sections:
                errors.append(
                    "routes_to_section_id '{config.appeal_mail_address.routes_to_section_id}' not found in sections"
                )

        # Validate sections
        for section_id, section in config.sections.items():
            if section.routing_rule == RoutingRule.ROUTES_TO_SECTION:
                if not section.appeal_mail_address:
                    errors.append(
                        "Section {section_id}: ROUTES_TO_SECTION requires appeal_mail_address"
                    )
                elif section.appeal_mail_address.status == AppealMailStatus.MISSING:
                    errors.append(
                        "Section {section_id}: ROUTES_TO_SECTION cannot have MISSING appeal_mail_address"
                    )
                elif (
                    section.appeal_mail_address.status
                    == AppealMailStatus.ROUTES_ELSEWHERE
                ):
                    if not section.appeal_mail_address.routes_to_section_id:
                        errors.append(
                            "Section {section_id}: ROUTES_ELSEWHERE status requires routes_to_section_id"
                        )
                    elif (
                        section.appeal_mail_address.routes_to_section_id
                        not in config.sections
                    ):
                        errors.append(
                            "Section {section_id}: routes_to_section_id '{section.appeal_mail_address.routes_to_section_id}' not found in sections"
                        )
                    else:
                        # Check that the target section has a valid address (not MISSING)
                        target_section = config.sections[
                            section.appeal_mail_address.routes_to_section_id
                        ]
                        if not target_section.appeal_mail_address:
                            errors.append(
                                "Section {section_id}: target section '{section.appeal_mail_address.routes_to_section_id}' has no appeal_mail_address"
                            )
                        elif (
                            target_section.appeal_mail_address.status
                            == AppealMailStatus.MISSING
                        ):
                            errors.append(
                                "Section {section_id}: target section '{section.appeal_mail_address.routes_to_section_id}' has MISSING appeal_mail_address"
                            )
                # COMPLETE status is always valid for ROUTES_TO_SECTION

        # Validate phone confirmation policy
        if config.phone_confirmation_policy.required:
            if not config.phone_confirmation_policy.phone_format_regex:
                errors.append(
                    "Phone confirmation required but no phone_format_regex provided"
                )
            if not config.phone_confirmation_policy.confirmation_message:
                errors.append(
                    "Phone confirmation required but no confirmation_message provided"
                )

        return errors

    def _build_citation_cache_for_city(
        self, city_id: str, config: CityConfiguration
    ) -> None:
        """Build citation pattern cache for fast lookups."""
        for pattern in config.citation_patterns:
            # Store example numbers in cache if provided
            if pattern.example_numbers:
                for example in pattern.example_numbers:
                    self._citation_cache[example] = (city_id, pattern.section_id)

    def match_citation(
        self, citation_number: str, city_id_hint: Optional[str] = None
    ) -> Optional[Tuple[str, str]]:
        """
        Match citation number to city and section.

        Args:
            citation_number: Citation number to match
            city_id_hint: Optional hint to check specific city first

        Returns:
            Tuple of (city_id, section_id) or None if no match
        """
        if not citation_number:
            return None

        # Check cache first
        cleaned = citation_number.strip().upper()
        if cleaned in self._citation_cache:
            return self._citation_cache[cleaned]

        # If city_id_hint is provided, check that city first
        if city_id_hint and city_id_hint in self.city_configs:
            config = self.city_configs[city_id_hint]
            for pattern in config.citation_patterns:
                if pattern.matches(cleaned):
                    # Cache for future lookups
                    self._citation_cache[cleaned] = (city_id_hint, pattern.section_id)
                    return city_id_hint, pattern.section_id

        # Search through all cities
        for city_id, config in self.city_configs.items():
            # Skip if we already checked this city with the hint
            if city_id_hint and city_id == city_id_hint:
                continue
            for pattern in config.citation_patterns:
                if pattern.matches(cleaned):
                    # Cache for future lookups
                    self._citation_cache[cleaned] = (city_id, pattern.section_id)
                    return city_id, pattern.section_id

        return None

    def get_city_config(self, city_id: str) -> Optional[CityConfiguration]:
        """Get city configuration by ID."""
        return self.city_configs.get(city_id)

    def get_mail_address(
        self, city_id: str, section_id: Optional[str] = None
    ) -> Optional[AppealMailAddress]:
        """
        Get mailing address for city/section.

        Args:
            city_id: City identifier
            section_id: Optional section identifier within city

        Returns:
            AppealMailAddress or None if not found
        """
        config = self.get_city_config(city_id)
        if not config:
            return None

        if section_id:
            section = config.sections.get(section_id)
            if section and section.appeal_mail_address:
                return section.appeal_mail_address

        return config.appeal_mail_address

    def get_phone_confirmation_policy(
        self, city_id: str, section_id: Optional[str] = None
    ) -> Optional[PhoneConfirmationPolicy]:
        """
        Get phone confirmation policy for city/section.

        Args:
            city_id: City identifier
            section_id: Optional section identifier within city

        Returns:
            PhoneConfirmationPolicy or None if not found
        """
        config = self.get_city_config(city_id)
        if not config:
            return None

        if section_id:
            section = config.sections.get(section_id)
            if section and section.phone_confirmation_policy:
                return section.phone_confirmation_policy

        return config.phone_confirmation_policy

    def get_routing_rule(
        self, city_id: str, section_id: Optional[str] = None
    ) -> Optional[RoutingRule]:
        """
        Get routing rule for city/section.

        Args:
            city_id: City identifier
            section_id: Optional section identifier within city

        Returns:
            RoutingRule or None if not found
        """
        config = self.get_city_config(city_id)
        if not config:
            return None

        if section_id:
            section = config.sections.get(section_id)
            if section:
                return section.routing_rule

        return config.routing_rule

    def get_all_cities(
        self, eligibility_filter: Optional[Union[CityStatus, List[CityStatus]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of all loaded cities with basic info.

        Args:
            eligibility_filter: Optional filter to return only cities with specific status(es).
        """
        # Normalize filter to a set of strings
        allowed_statuses = set()
        if eligibility_filter:
            if isinstance(eligibility_filter, (CityStatus, str)):
                allowed_statuses.add(
                    eligibility_filter.value
                    if isinstance(eligibility_filter, CityStatus)
                    else eligibility_filter
                )
            elif isinstance(eligibility_filter, list):
                for status in eligibility_filter:
                    allowed_statuses.add(
                        status.value if isinstance(status, CityStatus) else status
                    )

        cities = []
        for city_id, config in self.city_configs.items():
            # Apply filter if provided
            if allowed_statuses and config.status.value not in allowed_statuses:
                continue

            cities.append(
                {
                    "city_id": city_id,
                    "name": config.name,
                    "jurisdiction": config.jurisdiction.value,
                    "status": config.status.value,
                    "citation_pattern_count": len(config.citation_patterns),
                    "section_count": len(config.sections),
                    "is_eligible": self.is_eligible_for_appeals(city_id),
                }
            )
        return cities

    def is_eligible_for_appeals(self, city_id: str) -> bool:
        """
        Check if a city is eligible for appeals.

        A city is eligible if its status is ACTIVE or CAUTION.
        BLOCKED cities are not eligible.
        """
        config = self.get_city_config(city_id)
        if not config:
            return False

        return config.status in [CityStatus.ACTIVE, CityStatus.CAUTION]

    def validate_phone_for_city(
        self, city_id: str, phone_number: str, section_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate phone number for a city/section.

        Args:
            city_id: City identifier
            phone_number: Phone number to validate
            section_id: Optional section identifier

        Returns:
            Tuple of (is_valid, error_message)
        """
        policy = self.get_phone_confirmation_policy(city_id, section_id)
        if not policy:
            return True, None  # No policy means no validation required

        return policy.validate_phone(phone_number)


# Helper function for easy import
def get_city_registry(cities_dir: Optional[Path] = None) -> CityRegistry:
    """Get a configured CityRegistry instance."""
    registry = CityRegistry(cities_dir)
    registry.load_cities()
    return registry


# Example usage
if __name__ == "__main__":
    # Test the registry
    registry = CityRegistry()

    # Create test SF configuration (would normally come from JSON)
    sf_config = CityConfiguration(
        city_id="s",
        name="San Francisco",
        jurisdiction=Jurisdiction.CITY,
        citation_patterns=[
            CitationPattern(
                regex=r"^9\d{8}$",
                section_id="sfmta",
                description="SFMTA parking citation",
                example_numbers=["912345678"],
            )
        ],
        appeal_mail_address=AppealMailAddress(
            status=AppealMailStatus.COMPLETE,
            department="SFMTA Citation Review",
            address1="1 South Van Ness Avenue",
            address2="Floor 7",
            city="San Francisco",
            state="CA",
            zip="94103",
            country="USA",
        ),
        phone_confirmation_policy=PhoneConfirmationPolicy(required=False),
        routing_rule=RoutingRule.DIRECT,
        sections={
            "sfmta": CitySection(
                section_id="sfmta", name="SFMTA", routing_rule=RoutingRule.DIRECT
            )
        },
        verification_metadata=VerificationMetadata(
            last_updated="2024-01-01", source="official_website", confidence_score=0.95
        ),
    )

    # Manually add for testing
    registry.city_configs["s"] = sf_config
    registry._build_citation_cache_for_city("s", sf_config)

    # Test matching
    match = registry.match_citation("912345678")
    if match:
        city_id, section_id = match
        print("✅ Matched citation: city={city_id}, section={section_id}")

        # Test address retrieval
        address = registry.get_mail_address(city_id, section_id)
        if address:
            print("📫 Address status: {address.status.value}")

        # Test phone validation
        policy = registry.get_phone_confirmation_policy(city_id, section_id)
        if policy:
            print("📞 Phone confirmation required: {policy.required}")

    else:
        print("❌ No match found")

    print("Loaded cities: {len(registry.city_configs)}")
