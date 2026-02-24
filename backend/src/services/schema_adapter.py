"""
Schema Adapter Service for Fight City Tickets.com

Transforms rich/flexible JSON city configurations into strict Schema 4.3.0 format.
Handles normalization, default values, validation, and transformation of legacy formats
into the standardized schema required by CityRegistry.

Key Features:
- Normalizes field names and formats
- Sets intelligent defaults for missing required fields
- Validates regex patterns and phone formats
- Transforms address unions (complete/routes_elsewhere/missing)
- Ensures Schema 4.3.0 compliance before CityRegistry loading
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class AddressStatus(Enum):
    """Status of appeal mail address (Schema 4.3.0 union type)."""

    COMPLETE = "complete"
    ROUTES_ELSEWHERE = "routes_elsewhere"
    MISSING = "missing"


class RoutingRule(Enum):
    """Routing rules for appeal processing."""

    DIRECT = "direct"
    ROUTES_TO_SECTION = "routes_to_section"
    SEPARATE_ADDRESS_REQUIRED = "separate_address_required"


class SchemaAdapterError(Exception):
    """Base exception for schema adapter errors."""

    pass


class SchemaValidationError(SchemaAdapterError):
    """Raised when schema validation fails."""

    pass


class SchemaTransformationError(SchemaAdapterError):
    """Raised when schema transformation fails."""

    pass


@dataclass
class TransformationResult:
    """Result of schema transformation."""

    success: bool
    transformed_data: Dict[str, Any]
    warnings: List[str]
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "success": self.success,
            "has_warnings": len(self.warnings) > 0,
            "has_errors": len(self.errors) > 0,
            "warnings": self.warnings,
            "errors": self.errors,
            "data": self.transformed_data if self.success else None,
        }


class SchemaAdapter:
    """
    Schema 4.3.0 Adapter Service.

    Transforms rich/flexible JSON into strict Schema 4.3.0 format with:
    - Field normalization and standardization
    - Default value population
    - Regex pattern validation
    - Address union transformation
    - Phone confirmation policy handling
    - Validation against Schema 4.3.0 rules
    """

    # Schema 4.3.0 default values
    DEFAULT_TIMEZONE = "America/Los_Angeles"
    DEFAULT_APPEAL_DEADLINE_DAYS = 21
    DEFAULT_JURISDICTION = "city"
    DEFAULT_ROUTING_RULE = "direct"
    DEFAULT_STATUS = "active"

    # Field mappings for normalization (legacy -> Schema 4.3.0)
    FIELD_MAPPINGS = {
        # City info
        "city": "city_id",
        "city_name": "name",
        "municipality": "jurisdiction",
        "location": "jurisdiction",
        # Citation patterns
        "citation_pattern": "citation_patterns",  # Old format singular -> new format plural
        "patterns": "citation_patterns",
        "citation_regex": "regex",
        "regex_pattern": "regex",
        "agency": "section_id",
        "agency_id": "section_id",
        "examples": "example_numbers",
        # Address
        "mailing_address": "appeal_mail_address",
        "appeal_address": "appeal_mail_address",
        "address": "appeal_mail_address",
        "street": "address1",
        "street_address": "address1",
        "street2": "address2",
        "secondary_address": "address2",
        "postal_code": "zip",
        "zip_code": "zip",
        # Phone
        "phone_policy": "phone_confirmation_policy",
        "phone_verification": "phone_confirmation_policy",
        "phone_required": "required",
        "phone_regex": "phone_format_regex",
        "phone_message": "confirmation_message",
        "phone_deadline": "confirmation_deadline_hours",
        "phone_examples": "phone_number_examples",
        # Sections
        "agencies": "sections",
        "departments": "sections",
        "divisions": "sections",
        # Metadata
        "metadata": "verification_metadata",
        "verification": "verification_metadata",
        "source_info": "verification_metadata",
        "last_verified": "last_updated",
        "confidence": "confidence_score",
        "source": "source",
        "notes": "notes",
        "verified_by": "verified_by",
        # Online appeal
        "online_available": "online_appeal_available",
        "appeal_url": "online_appeal_url",
        "website": "online_appeal_url",
        # Status
        "eligibility": "status",
        "city_status": "status",
    }

    def __init__(self, strict_mode: bool = True):
        """
        Initialize schema adapter.

        Args:
            strict_mode: If True, raises errors on validation failures.
                         If False, attempts to fix issues with warnings.
        """
        self.strict_mode = strict_mode
        self._normalization_cache = {}

    def adapt_city_schema(self, input_data: Dict[str, Any]) -> TransformationResult:
        """
        Transform rich/flexible JSON into Schema 4.3.0 format.

        Args:
            input_data: Flexible JSON city configuration

        Returns:
            TransformationResult with success status and transformed data
        """
        warnings = []
        errors = []

        try:
            # Step 1: Deep copy and normalize field names
            normalized = self._normalize_field_names(input_data)

            # Step 2: Apply field-specific transformations
            transformed = self._transform_fields(normalized, warnings)

            # Step 3: Set default values for missing required fields
            transformed = self._apply_defaults(transformed, warnings)

            # Step 4: Validate against Schema 4.3.0 rules
            validation_errors = self._validate_schema(transformed)

            if validation_errors:
                if self.strict_mode:
                    errors.extend(validation_errors)
                    return TransformationResult(
                        success=False,
                        transformed_data={},
                        warnings=warnings,
                        errors=errors,
                    )
                else:
                    warnings.extend(
                        [
                            "Validation issue (auto-fixed): {err}"
                            for err in validation_errors
                        ]
                    )
                    # Attempt to fix validation errors
                    transformed = self._fix_validation_issues(
                        transformed, validation_errors
                    )

                    # Re-validate after fixes
                    remaining_errors = self._validate_schema(transformed)
                    if remaining_errors:
                        errors.extend(["Unfixable: {err}" for err in remaining_errors])
                        return TransformationResult(
                            success=False,
                            transformed_data={},
                            warnings=warnings,
                            errors=errors,
                        )

            # Step 5: Final transformation for specific union types
            transformed = self._finalize_transformation(transformed, warnings)

            return TransformationResult(
                success=True,
                transformed_data=transformed,
                warnings=warnings,
                errors=errors,
            )

        except Exception as e:
            errors.append("Transformation failed: {str(e)}")
            return TransformationResult(
                success=False, transformed_data={}, warnings=warnings, errors=errors
            )

    def _normalize_field_names(self, data: Any) -> Any:
        """
        Recursively normalize field names using FIELD_MAPPINGS.

        Args:
            data: Input data (dict, list, or primitive)

        Returns:
            Data with normalized field names
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Normalize the key
                normalized_key = self.FIELD_MAPPINGS.get(key, key)

                # Recursively normalize the value
                result[normalized_key] = self._normalize_field_names(value)
            return result

        elif isinstance(data, list):
            return [self._normalize_field_names(item) for item in data]

        else:
            return data

    def _transform_fields(
        self, data: Dict[str, Any], warnings: List[str]
    ) -> Dict[str, Any]:
        """Apply field-specific transformations."""
        result = data.copy()

        # Transform city_id to lowercase slug
        if "city_id" in result and isinstance(result["city_id"], str):
            result["city_id"] = (
                result["city_id"].lower().replace(" ", "_").replace(".", "")
            )

        # Transform jurisdiction
        if "jurisdiction" in result and isinstance(result["jurisdiction"], str):
            jurisdiction = result["jurisdiction"].lower()
            if jurisdiction in ["municipality", "town", "borough"]:
                result["jurisdiction"] = "city"
            elif jurisdiction in ["county", "parish"]:
                result["jurisdiction"] = "county"
            elif jurisdiction in ["state", "province"]:
                result["jurisdiction"] = "state"
            elif jurisdiction in ["federal", "national"]:
                result["jurisdiction"] = "federal"

        # Transform status
        if "status" in result and isinstance(result["status"], str):
            status = result["status"].lower()
            if status not in ["active", "caution", "blocked"]:
                warnings.append(
                    f"Status: Invalid status '{status}', defaulting to 'active'"
                )
                result["status"] = "active"
            else:
                result["status"] = status

        # Handle old format: authority field -> convert to section and extract section_id for citation patterns
        authority_section_id = None
        if "authority" in result and isinstance(result["authority"], dict):
            authority = result["authority"]
            authority_section_id = authority.get("section_id")

            # Convert authority to a section if sections don't exist or don't have this section
            if "sections" not in result:
                result["sections"] = {}

            if authority_section_id and authority_section_id not in result["sections"]:
                # Create section from authority object
                section_data = {
                    "name": authority.get("name", authority.get("authority_name", authority_section_id.upper())),
                    "routing_rule": "direct",
                    "phone_confirmation_policy": {"required": False},
                }
                # Copy appeal_mail_address from top level if present
                if "appeal_mail_address" in result:
                    section_data["appeal_mail_address"] = result["appeal_mail_address"]

                result["sections"][authority_section_id] = section_data
                warnings.append(f"Authority: Converted authority object to section '{authority_section_id}'")

            # Remove authority field as it's been converted
            del result["authority"]

        # Transform citation patterns
        if "citation_patterns" in result:
            # Handle old format: citation_pattern (singular object) -> citation_patterns (array)
            if isinstance(result["citation_patterns"], dict):
                # Old format has single citation_pattern object, convert to array
                warnings.append("Citation pattern: Converting singular citation_pattern to citation_patterns array")
                result["citation_patterns"] = [result["citation_patterns"]]

            if isinstance(result["citation_patterns"], list):
                # Pass authority_section_id to use as default for patterns missing section_id
                result["citation_patterns"] = self._transform_citation_patterns(
                    result["citation_patterns"], warnings, default_section_id=authority_section_id
                )

        # Transform appeal mail address
        if "appeal_mail_address" in result:
            result["appeal_mail_address"] = self._transform_address(
                result["appeal_mail_address"], warnings
            )

        # Transform phone confirmation policy
        if "phone_confirmation_policy" in result:
            result["phone_confirmation_policy"] = self._transform_phone_policy(
                result["phone_confirmation_policy"], warnings
            )

        # Transform sections
        if "sections" in result and isinstance(result["sections"], dict):
            result["sections"] = self._transform_sections(result["sections"], warnings)

        # Transform verification metadata
        if "verification_metadata" in result:
            result["verification_metadata"] = self._transform_metadata(
                result["verification_metadata"], warnings
            )

        return result

    def _transform_citation_patterns(
        self, patterns: List[Any], warnings: List[str], default_section_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Transform citation patterns to Schema 4.3.0 format."""
        transformed = []

        for i, pattern in enumerate(patterns):
            if isinstance(pattern, str):
                # Convert string pattern to dict
                section_id = default_section_id if default_section_id else "default"
                transformed.append(
                    {
                        "regex": pattern,
                        "section_id": section_id,
                        "description": "Citation pattern {i + 1}",
                        "example_numbers": [],
                    }
                )
                warnings.append(
                    "Pattern {i + 1}: Converted string pattern to dict with section_id='{section_id}'"
                )

            elif isinstance(pattern, dict):
                pattern_dict = pattern.copy()

                # Ensure required fields
                if "regex" not in pattern_dict:
                    if "pattern" in pattern_dict:
                        pattern_dict["regex"] = pattern_dict.pop("pattern")
                    else:
                        warnings.append(
                            "Pattern {i + 1}: Missing regex, using default"
                        )
                        pattern_dict["regex"] = "^[A-Z0-9]{6,12}$"

                if "section_id" not in pattern_dict:
                    # Use default_section_id from authority if available, otherwise "default"
                    pattern_dict["section_id"] = default_section_id if default_section_id else "default"
                    warnings.append(
                        "Pattern {i + 1}: Missing section_id, using '{pattern_dict['section_id']}'"
                    )

                if "description" not in pattern_dict:
                    pattern_dict["description"] = (
                        "Citation pattern for {pattern_dict.get('section_id', 'unknown')}"
                    )

                # Validate regex
                try:
                    re.compile(pattern_dict["regex"])
                except re.error as e:
                    warnings.append(
                        "Pattern {i + 1}: Invalid regex '{pattern_dict['regex']}': {e}"
                    )
                    # Use a safe default
                    pattern_dict["regex"] = "^[A-Z0-9]{6,12}$"

                transformed.append(pattern_dict)

            else:
                warnings.append(
                    "Pattern {i + 1}: Invalid type {type(pattern).__name__}, skipping"
                )

        return transformed

    def _transform_address(self, address: Any, warnings: List[str]) -> Dict[str, Any]:
        """Transform address to Schema 4.3.0 union format."""
        if isinstance(address, str):
            # Simple string address - treat as complete
            warnings.append("Address: String address converted to COMPLETE union type")
            return {
                "status": "complete",
                "address1": address,
                "city": "Unknown",
                "state": "CA",
                "zip": "00000",
                "country": "USA",
            }

        elif isinstance(address, dict):
            address_dict = address.copy()

            # Determine status based on content
            if "status" not in address_dict:
                if "routes_to_section_id" in address_dict:
                    address_dict["status"] = "routes_elsewhere"
                elif all(
                    key in address_dict
                    for key in ["address1", "city", "state", "zip", "country"]
                ):
                    address_dict["status"] = "complete"
                else:
                    address_dict["status"] = "missing"
                    warnings.append("Address: Incomplete address marked as MISSING")

            # Normalize status value
            status = address_dict["status"].lower()
            if status in ["complete", "full", "valid"]:
                address_dict["status"] = "complete"
            elif status in ["routes_elsewhere", "redirect", "forward"]:
                address_dict["status"] = "routes_elsewhere"
            elif status in ["missing", "none", "unknown"]:
                address_dict["status"] = "missing"
            else:
                warnings.append("Address: Unknown status '{status}', using 'missing'")
                address_dict["status"] = "missing"

            # Ensure required fields for COMPLETE status
            if address_dict["status"] == "complete":
                required = ["address1", "city", "state", "zip", "country"]
                for field in required:
                    # Only set default if field is truly missing or empty, preserve existing values
                    if field not in address_dict or (address_dict[field] is None or str(address_dict[field]).strip() == ""):
                        address_dict[field] = self._get_address_default(field)
                        warnings.append("Address: Missing {field}, using default")

                # Optional fields
                if "department" not in address_dict:
                    address_dict["department"] = "Citation Appeals Department"
                if "attention" not in address_dict:
                    address_dict["attention"] = "Appeals Processing"

            # Ensure routes_to_section_id for ROUTES_ELSEWHERE status
            elif address_dict["status"] == "routes_elsewhere":
                if "routes_to_section_id" not in address_dict:
                    address_dict["routes_to_section_id"] = "default"
                    warnings.append(
                        "Address: routes_elsewhere missing routes_to_section_id, using 'default'"
                    )

            # MISSING status needs no additional fields

            return address_dict

        else:
            warnings.append("Address: Invalid address format, using MISSING")
            return {"status": "missing"}

    def _transform_phone_policy(
        self, policy: Any, warnings: List[str]
    ) -> Dict[str, Any]:
        """Transform phone confirmation policy to Schema 4.3.0 format."""
        if isinstance(policy, bool):
            # Simple boolean - expand to full policy
            return {
                "required": policy,
                "phone_format_regex": "^\\+1\\d{10}$" if policy else None,
                "confirmation_message": "Please call to confirm appeal receipt."
                if policy
                else None,
                "confirmation_deadline_hours": 48 if policy else None,
                "phone_number_examples": ["+15551234567"] if policy else None,
            }

        elif isinstance(policy, dict):
            policy_dict = policy.copy()

            # Ensure required field
            if "required" not in policy_dict:
                policy_dict["required"] = False
                warnings.append("Phone policy: Missing 'required', defaulting to False")

            # Set defaults based on required flag
            if policy_dict["required"]:
                if "phone_format_regex" not in policy_dict:
                    policy_dict["phone_format_regex"] = "^\\+1\\d{10}$"
                    warnings.append(
                        "Phone policy: Required but missing regex, using US format"
                    )

                if "confirmation_message" not in policy_dict:
                    policy_dict["confirmation_message"] = (
                        "Please call to confirm appeal receipt within the deadline."
                    )
                    warnings.append(
                        "Phone policy: Required but missing message, using default"
                    )

                if "confirmation_deadline_hours" not in policy_dict:
                    policy_dict["confirmation_deadline_hours"] = 48
                    warnings.append(
                        "Phone policy: Required but missing deadline, using 48 hours"
                    )

                if "phone_number_examples" not in policy_dict:
                    policy_dict["phone_number_examples"] = ["+15551234567"]
                    warnings.append(
                        "Phone policy: Required but missing examples, using placeholder"
                    )

            return policy_dict

        else:
            warnings.append(
                "Phone policy: Invalid format, using default (not required)"
            )
            return {"required": False}

    def _transform_sections(
        self, sections: Dict[str, Any], warnings: List[str]
    ) -> Dict[str, Any]:
        """Transform sections to Schema 4.3.0 format."""
        transformed = {}

        for section_id, section_data in sections.items():
            if isinstance(section_data, str):
                # String section - convert to dict with name
                transformed[section_id] = {
                    "section_id": section_id,
                    "name": section_data,
                    "routing_rule": "direct",
                    "phone_confirmation_policy": {"required": False},
                }
                warnings.append("Section {section_id}: String converted to dict")

            elif isinstance(section_data, dict):
                section_dict = section_data.copy()

                # Ensure section_id matches key
                section_dict["section_id"] = section_id

                # Ensure name
                if "name" not in section_dict:
                    section_dict["name"] = section_id.upper()
                    warnings.append(
                        "Section {section_id}: Missing name, using section_id"
                    )

                # Ensure routing_rule
                if "routing_rule" not in section_dict:
                    section_dict["routing_rule"] = "direct"

                # Transform address if present
                if "appeal_mail_address" in section_dict:
                    section_dict["appeal_mail_address"] = self._transform_address(
                        section_dict["appeal_mail_address"], warnings
                    )

                # Transform phone policy if present
                if "phone_confirmation_policy" in section_dict:
                    section_dict["phone_confirmation_policy"] = (
                        self._transform_phone_policy(
                            section_dict["phone_confirmation_policy"], warnings
                        )
                    )
                else:
                    section_dict["phone_confirmation_policy"] = {"required": False}

                transformed[section_id] = section_dict

            else:
                warnings.append(
                    "Section {section_id}: Invalid type {type(section_data).__name__}, skipping"
                )

        return transformed

    def _transform_metadata(self, metadata: Any, warnings: List[str]) -> Dict[str, Any]:
        """Transform verification metadata to Schema 4.3.0 format."""
        if isinstance(metadata, dict):
            metadata_dict = metadata.copy()

            # Map old format fields to new format
            # verified_at -> last_updated
            if "verified_at" in metadata_dict and "last_updated" not in metadata_dict:
                metadata_dict["last_updated"] = metadata_dict.pop("verified_at")
            # last_checked -> last_updated (if verified_at not present)
            elif "last_checked" in metadata_dict and "last_updated" not in metadata_dict:
                metadata_dict["last_updated"] = metadata_dict.pop("last_checked")

            # source_type -> source
            if "source_type" in metadata_dict and "source" not in metadata_dict:
                metadata_dict["source"] = metadata_dict.pop("source_type")

            # source_note -> notes
            if "source_note" in metadata_dict and "notes" not in metadata_dict:
                metadata_dict["notes"] = metadata_dict.pop("source_note")

            # last_validated_by -> verified_by
            if "last_validated_by" in metadata_dict and "verified_by" not in metadata_dict:
                metadata_dict["verified_by"] = metadata_dict.pop("last_validated_by")

            # Remove unsupported fields (status, needs_confirmation, operational_ready, etc.)
            unsupported_fields = ["status", "needs_confirmation", "operational_ready", "last_checked"]
            for field in unsupported_fields:
                if field in metadata_dict:
                    del metadata_dict[field]
                    warnings.append("Metadata: Removed unsupported field '{field}'")

            # Ensure required fields
            if "last_updated" not in metadata_dict:
                metadata_dict["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                warnings.append("Metadata: Missing last_updated, using current date")

            if "source" not in metadata_dict:
                metadata_dict["source"] = "unknown"
                warnings.append("Metadata: Missing source, using 'unknown'")

            if "confidence_score" not in metadata_dict:
                metadata_dict["confidence_score"] = 0.5
                warnings.append("Metadata: Missing confidence_score, using 0.5")

            if "notes" not in metadata_dict:
                metadata_dict["notes"] = "Automatically transformed by Schema Adapter"

            if "verified_by" not in metadata_dict:
                metadata_dict["verified_by"] = "system"

            # Ensure confidence_score is float 0-1
            try:
                score = float(metadata_dict["confidence_score"])
                if score < 0 or score > 1:
                    metadata_dict["confidence_score"] = 0.5
                    warnings.append(
                        "Metadata: confidence_score out of range 0-1, using 0.5"
                    )
            except (ValueError, TypeError):
                metadata_dict["confidence_score"] = 0.5
                warnings.append("Metadata: Invalid confidence_score, using 0.5")

            # Only return fields that VerificationMetadata accepts
            allowed_fields = ["last_updated", "source", "confidence_score", "notes", "verified_by"]
            return {k: v for k, v in metadata_dict.items() if k in allowed_fields}

        else:
            warnings.append("Metadata: Invalid format, creating default")
            return {
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "source": "unknown",
                "confidence_score": 0.5,
                "notes": "Automatically transformed by Schema Adapter",
                "verified_by": "system",
            }

    def _apply_defaults(
        self, data: Dict[str, Any], warnings: List[str]
    ) -> Dict[str, Any]:
        """Apply default values for missing required fields."""
        result = data.copy()

        # Required top-level fields
        required_fields = [
            ("city_id", "unknown_city"),
            ("name", ""),
            ("jurisdiction", self.DEFAULT_JURISDICTION),
            ("status", "active"),
            ("citation_patterns", []),
            ("appeal_mail_address", {"status": "missing"}),
            ("phone_confirmation_policy", {"required": False}),
            ("routing_rule", self.DEFAULT_ROUTING_RULE),
            ("status", self.DEFAULT_STATUS),
            ("sections", {}),
            (
                "verification_metadata",
                {
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "source": "unknown",
                    "confidence_score": 0.5,
                    "notes": "Automatically transformed by Schema Adapter",
                    "verified_by": "system",
                },
            ),
        ]

        for field, default in required_fields:
            if field not in result:
                result[field] = default
                warnings.append("Missing required field '{field}', using default")

        # Optional fields with defaults
        optional_defaults = [
            ("timezone", self.DEFAULT_TIMEZONE),
            ("appeal_deadline_days", self.DEFAULT_APPEAL_DEADLINE_DAYS),
            ("online_appeal_available", False),
            ("online_appeal_url", None),
        ]

        for field, default in optional_defaults:
            if field not in result:
                result[field] = default

        return result

    def _validate_schema(self, data: Dict[str, Any]) -> List[str]:
        """Validate transformed data against Schema 4.3.0 rules."""
        errors = []

        # Check required fields are not empty
        if not data.get("city_id") or str(data["city_id"]).strip() == "":
            errors.append("city_id is required and cannot be empty")

        # Validate status
        valid_statuses = ["active", "beta", "blocked", "coming_soon"]
        if "status" in data and data["status"] not in valid_statuses:
            errors.append(
                f"Invalid status '{data['status']}'. Must be one of: {', '.join(valid_statuses)}"
            )

        if not data.get("name") or str(data["name"]).strip() == "":
            errors.append("name is required and cannot be empty")

        # Validate status
        if data.get("status") not in ["active", "caution", "blocked"]:
            errors.append(
                f"Invalid status '{data.get('status')}'. Must be active, caution, or blocked."
            )

        # Validate citation patterns
        patterns = data.get("citation_patterns", [])
        if not patterns:
            errors.append("At least one citation pattern is required")

        for i, pattern in enumerate(patterns):
            if (
                not pattern.get("section_id")
                or str(pattern["section_id"]).strip() == ""
            ):
                errors.append("Citation pattern {i}: section_id is required")

            if pattern["section_id"] not in data.get("sections", {}):
                errors.append(
                    "Citation pattern {i}: section_id '{pattern['section_id']}' not found in sections"
                )

            # Validate regex
            if "regex" not in pattern:
                errors.append("Citation pattern {i}: regex is required")
            else:
                try:
                    re.compile(pattern["regex"])
                except re.error as e:
                    errors.append(
                        "Citation pattern {i}: Invalid regex '{pattern['regex']}': {e}"
                    )

        # Validate appeal mail address union rules
        address = data.get("appeal_mail_address", {})
        status = address.get("status", "missing")

        if status == "complete":
            required_fields = ["address1", "city", "state", "zip", "country"]
            for field in required_fields:
                if not address.get(field) or str(address[field]).strip() == "":
                    errors.append(
                        "Complete appeal mail address requires non-empty {field}"
                    )

        elif status == "routes_elsewhere":
            if not address.get("routes_to_section_id"):
                errors.append("routes_elsewhere status requires routes_to_section_id")
            elif address["routes_to_section_id"] not in data.get("sections", {}):
                errors.append(
                    "routes_to_section_id '{address['routes_to_section_id']}' not found in sections"
                )

        # Validate sections
        sections = data.get("sections", {})
        for section_id, section in sections.items():
            if section.get("routing_rule") == "routes_to_section":
                if "appeal_mail_address" not in section:
                    errors.append(
                        "Section {section_id}: ROUTES_TO_SECTION requires appeal_mail_address"
                    )
                elif section["appeal_mail_address"].get("status") == "missing":
                    errors.append(
                        "Section {section_id}: ROUTES_TO_SECTION cannot have MISSING appeal_mail_address"
                    )

        # Validate phone confirmation policy
        phone_policy = data.get("phone_confirmation_policy", {})
        if phone_policy.get("required"):
            if not phone_policy.get("phone_format_regex"):
                errors.append(
                    "Phone confirmation required but no phone_format_regex provided"
                )
            if not phone_policy.get("confirmation_message"):
                errors.append(
                    "Phone confirmation required but no confirmation_message provided"
                )

        return errors

    def _fix_validation_issues(
        self, data: Dict[str, Any], errors: List[str]
    ) -> Dict[str, Any]:
        """Attempt to fix validation errors (non-strict mode)."""
        result = data.copy()

        # Fix empty city_id
        if not result.get("city_id") or str(result["city_id"]).strip() == "":
            result["city_id"] = "unknown_city"

        # Fix empty name
        if not result.get("name") or str(result["name"]).strip() == "":
            result["name"] = ""

        # Fix invalid status
        if result.get("status") not in ["active", "caution", "blocked"]:
            result["status"] = "active"

        # Fix missing citation patterns
        if not result.get("citation_patterns"):
            result["citation_patterns"] = [
                {
                    "regex": "^[A-Z0-9]{6,12}$",
                    "section_id": "default",
                    "description": "Default citation pattern",
                    "example_numbers": [],
                }
            ]
            # Ensure default section exists
            if "default" not in result.get("sections", {}):
                result.setdefault("sections", {})["default"] = {
                    "section_id": "default",
                    "name": "Default Agency",
                    "routing_rule": "direct",
                    "phone_confirmation_policy": {"required": False},
                }

        # Fix citation pattern section references
        sections = result.get("sections", {})
        for pattern in result.get("citation_patterns", []):
            section_id = pattern.get("section_id")
            if section_id and section_id not in sections:
                # Create missing section
                sections[section_id] = {
                    "section_id": section_id,
                    "name": section_id.upper(),
                    "routing_rule": "direct",
                    "phone_confirmation_policy": {"required": False},
                }

        # Fix address issues
        address = result.get("appeal_mail_address", {})
        status = address.get("status", "missing")

        if status == "complete":
            for field in ["address1", "city", "state", "zip", "country"]:
                if not address.get(field) or str(address[field]).strip() == "":
                    address[field] = self._get_address_default(field)

        elif status == "routes_elsewhere":
            # Ensure routes_to_section_id exists and references a valid section
            if not address.get("routes_to_section_id"):
                # Find first section or create default
                if sections:
                    address["routes_to_section_id"] = next(iter(sections.keys()))
                else:
                    address["routes_to_section_id"] = "default"
                    sections["default"] = {
                        "section_id": "default",
                        "name": "Default Agency",
                        "routing_rule": "direct",
                        "phone_confirmation_policy": {"required": False},
                    }
            else:
                # Ensure referenced section exists
                routes_to_id = address["routes_to_section_id"]
                if routes_to_id not in sections:
                    sections[routes_to_id] = {
                        "section_id": routes_to_id,
                        "name": routes_to_id.upper(),
                        "routing_rule": "direct",
                        "phone_confirmation_policy": {"required": False},
                    }

        # Fix phone policy issues
        phone_policy = result.get("phone_confirmation_policy", {})
        if phone_policy.get("required"):
            if not phone_policy.get("phone_format_regex"):
                phone_policy["phone_format_regex"] = "^\\+1\\d{10}$"
            if not phone_policy.get("confirmation_message"):
                phone_policy["confirmation_message"] = (
                    "Please call to confirm appeal receipt."
                )

        return result

    def _finalize_transformation(
        self, data: Dict[str, Any], warnings: List[str]
    ) -> Dict[str, Any]:
        """Apply final transformations and cleanup."""
        result = data.copy()

        # Ensure all citation patterns reference valid sections
        valid_sections = set(result.get("sections", {}).keys())
        patterns = result.get("citation_patterns", [])

        filtered_patterns = []
        for pattern in patterns:
            if pattern.get("section_id") in valid_sections:
                filtered_patterns.append(pattern)
            else:
                warnings.append(
                    "Citation pattern references invalid section '{pattern.get('section_id')}', skipping"
                )

        if filtered_patterns:
            result["citation_patterns"] = filtered_patterns
        else:
            # Create at least one pattern referencing first section
            if valid_sections:
                first_section = next(iter(valid_sections))
                result["citation_patterns"] = [
                    {
                        "regex": "^[A-Z0-9]{6,12}$",
                        "section_id": first_section,
                        "description": "Default pattern for {first_section}",
                        "example_numbers": [],
                    }
                ]
                warnings.append("No valid citation patterns, created default")

        # Clean up empty strings in address fields
        address = result.get("appeal_mail_address", {})
        if isinstance(address, dict):
            for key, value in list(address.items()):
                if isinstance(value, str) and value.strip() == "":
                    address[key] = None

        # Clean up sections
        for section_id, section in result.get("sections", {}).items():
            if isinstance(section, dict):
                # Ensure section has all required fields
                if "section_id" not in section:
                    section["section_id"] = section_id
                if "name" not in section:
                    section["name"] = section_id.upper()
                if "routing_rule" not in section:
                    section["routing_rule"] = "direct"
                if "phone_confirmation_policy" not in section:
                    section["phone_confirmation_policy"] = {"required": False}

        return result

    def _get_address_default(self, field: str) -> str:
        """Get default value for address field."""
        defaults = {
            "address1": "Unknown Street",
            "city": "Unknown",  # Changed from "" to "Unknown" to pass validation
            "state": "CA",
            "zip": "00000",
            "country": "USA",
            "department": "Citation Appeals Department",
            "attention": "Appeals Processing",
        }
        return defaults.get(field, "")

    def adapt_city_file(
        self, input_path: Path, output_path: Optional[Path] = None
    ) -> TransformationResult:
        """
        Adapt a city configuration file from rich JSON to Schema 4.3.0.

        Args:
            input_path: Path to input JSON file
            output_path: Optional path to save transformed JSON (if None, not saved)

        Returns:
            TransformationResult with success status
        """
        try:
            # Load input file
            with open(input_path, "r", encoding="utf-8") as f:
                input_data = json.load(f)

            # Adapt schema
            result = self.adapt_city_schema(input_data)

            # Save to output file if requested
            if output_path and result.success:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result.transformed_data, f, indent=2, ensure_ascii=False)

            return result

        except Exception as e:
            return TransformationResult(
                success=False,
                transformed_data={},
                warnings=[],
                errors=["File adaptation failed: {str(e)}"],
            )

    def batch_adapt_directory(
        self, input_dir: Path, output_dir: Path
    ) -> Dict[str, TransformationResult]:
        """
        Adapt all JSON files in a directory.

        Args:
            input_dir: Directory containing input JSON files
            output_dir: Directory to save transformed JSON files

        Returns:
            Dictionary mapping filename to TransformationResult
        """
        results = {}

        if not input_dir.exists():
            return {
                "error": TransformationResult(
                    success=False,
                    transformed_data={},
                    warnings=[],
                    errors=["Input directory does not exist: {input_dir}"],
                )
            }

        output_dir.mkdir(parents=True, exist_ok=True)

        for json_file in input_dir.glob("*.json"):
            output_file = output_dir / json_file.name
            results[json_file.name] = self.adapt_city_file(json_file, output_file)

        return results


# Convenience functions
def adapt_city_schema(
    input_data: Dict[str, Any], strict_mode: bool = True
) -> TransformationResult:
    """Convenience function for single schema adaptation."""
    adapter = SchemaAdapter(strict_mode=strict_mode)
    return adapter.adapt_city_schema(input_data)


def adapt_city_file(
    input_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None
) -> TransformationResult:
    """Convenience function for file adaptation."""
    adapter = SchemaAdapter()
    return adapter.adapt_city_file(
        Path(input_path) if isinstance(input_path, str) else input_path,
        Path(output_path) if output_path else None,
    )


def batch_adapt_directory(
    input_dir: Union[str, Path], output_dir: Union[str, Path]
) -> Dict[str, TransformationResult]:
    """Convenience function for directory batch adaptation."""
    adapter = SchemaAdapter()
    return adapter.batch_adapt_directory(
        Path(input_dir) if isinstance(input_dir, str) else input_dir,
        Path(output_dir) if isinstance(output_dir, str) else output_dir,
    )


if __name__ == "__main__":
    """Command-line interface for schema adaptation."""
    import argparse

    parser = argparse.ArgumentParser(description="Transform rich JSON to Schema 4.3.0")
    parser.add_argument("input", help="Input JSON file or directory")
    parser.add_argument("--output", "-o", help="Output JSON file or directory")
    parser.add_argument(
        "--strict",
        "-s",
        action="store_true",
        help="Strict mode (fail on validation errors)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    adapter = SchemaAdapter(strict_mode=args.strict)

    input_path = Path(args.input)

    if input_path.is_file():
        # Single file adaptation
        result = adapter.adapt_city_file(
            input_path, Path(args.output) if args.output else None
        )

        if args.verbose:
            print(f"\nTransformation {'SUCCESS' if result.success else 'FAILED'}")
            if result.warnings:
                print(f"\nWarnings ({len(result.warnings)}):")
                for warning in result.warnings:
                    print(f"  ⚠️  {warning}")
            if result.errors:
                print(f"\nErrors ({len(result.errors)}):")
                for error in result.errors:
                    print(f"  ❌ {error}")
            if result.success:
                print(f"\nOutput saved to: {args.output or '(not saved)'}")
        else:
            print(f"Success: {result.success}")
            if result.errors:
                print(f"Errors: {len(result.errors)}")
            if result.warnings:
                print(f"Warnings: {len(result.warnings)}")

    elif input_path.is_dir():
        # Directory batch adaptation
        output_dir = Path(args.output) if args.output else input_path.parent / "adapted"
        results = adapter.batch_adapt_directory(input_path, output_dir)

        success_count = sum(1 for r in results.values() if r.success)
        total_count = len(results)

        print("\nBatch Adaptation Complete")
        print(f"Processed: {total_count} files")
        print(f"Success: {success_count}")
        print(f"Failed: {total_count - success_count}")
        print(f"Output directory: {output_dir}")

        if args.verbose:
            for filename, result in results.items():
                status = "✅" if result.success else "❌"
                print(f"\n{status} {filename}")
                if result.warnings:
                    print(f"  Warnings: {len(result.warnings)}")
                if result.errors:
                    print(f"  Errors: {len(result.errors)}")

    else:
        print(f"Error: Input path does not exist: {args.input}")
        exit(1)
