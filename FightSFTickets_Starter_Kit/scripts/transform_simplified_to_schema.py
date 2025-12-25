#!/usr/bin/env python3
"""
Transform simplified city JSON (from extract_city_simple.py) to Schema 4.3.0 format.
This script bridges the gap between extracted simplified data and the full Schema 4.3.0
required by CityRegistry.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add backend/src to Python path for imports
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

# Try to import schema_adapter for final validation
try:
    from services.schema_adapter import SchemaAdapter

    SCHEMA_ADAPTER_AVAILABLE = True
except ImportError:
    SCHEMA_ADAPTER_AVAILABLE = False
    print(
        "Warning: Schema adapter not available, will generate basic Schema 4.3.0 format"
    )


def load_simplified_json(filepath: Path) -> Dict[str, Any]:
    """Load simplified city JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def transform_simplified_to_schema(simplified_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform simplified city JSON to Schema 4.3.0 format.

    Simplified format (from extract_city_simple.py):
    - city_id, name, state, country
    - authority (SimplifiedCityAuthority)
    - citation_pattern (SimplifiedCitationPattern) - singular
    - appeal_address (SimplifiedAppealAddress)
    - submission_methods (SimplifiedSubmissionMethods)
    - phone_confirmation (SimplifiedPhoneConfirmation)
    - verification (SimplifiedVerification)

    Schema 4.3.0 format (expected by CityRegistry):
    - city_id, name, jurisdiction
    - citation_patterns (list of CitationPattern)
    - appeal_mail_address (AppealMailAddress)
    - phone_confirmation_policy (PhoneConfirmationPolicy)
    - routing_rule
    - sections (dict of CitySection)
    - verification_metadata (VerificationMetadata)
    """

    # Extract basic info
    city_id = simplified_data.get("city_id", "")
    name = simplified_data.get("name", "")
    state = simplified_data.get("state", "")
    country = simplified_data.get("country", "US")

    # Extract authority section
    authority = simplified_data.get("authority", {})
    section_id = authority.get("section_id", "city_main")

    # Transform citation_pattern (singular) to citation_patterns (list)
    citation_pattern = simplified_data.get("citation_pattern", {})
    citation_patterns = []
    if citation_pattern:
        citation_patterns.append(
            {
                "regex": citation_pattern.get("regex", ""),
                "section_id": section_id,
                "description": citation_pattern.get(
                    "description", f"{name} parking citation format"
                ),
                "example_numbers": citation_pattern.get("example_numbers", []),
                "visual_markers": citation_pattern.get("visual_markers", []),
                "notes": _clean_notes(citation_pattern.get("notes", "")),
                "confidence_score": _map_confidence_to_score(
                    citation_pattern.get("confidence", "low")
                ),
            }
        )

    # Transform appeal_address to appeal_mail_address
    appeal_address = simplified_data.get("appeal_address", {})
    appeal_mail_address = {
        "status": appeal_address.get("status", "missing"),
        "department": appeal_address.get("department", ""),
        "attention": appeal_address.get("attention", ""),
        "address1": appeal_address.get("address1", ""),
        "address2": appeal_address.get("address2", ""),
        "city": appeal_address.get("city", ""),
        "state": appeal_address.get("state", state),
        "zip": appeal_address.get("zip", ""),
        "country": appeal_address.get("country", country),
        "routes_to_section_id": appeal_address.get("routes_to_section_id", ""),
        "missing_fields": appeal_address.get("missing_fields", []),
        "missing_reason": appeal_address.get("missing_reason", ""),
    }

    # Transform phone_confirmation to phone_confirmation_policy
    phone_confirmation = simplified_data.get("phone_confirmation", {})

    # Combine phone_numbers and alt_phone_numbers into phone_number_examples
    phone_numbers = phone_confirmation.get("phone_numbers", [])
    alt_phone_numbers = phone_confirmation.get("alt_phone_numbers", [])
    phone_number_examples = phone_numbers + alt_phone_numbers

    # Remove duplicates and empty strings
    if phone_number_examples:
        phone_number_examples = list(set([p for p in phone_number_examples if p]))
        if not phone_number_examples:
            phone_number_examples = None

    # Create default US phone format regex if we have phone numbers
    phone_format_regex = None
    if phone_number_examples:
        # Simple US phone regex that matches (XXX) XXX-XXXX, XXX-XXX-XXXX, etc.
        phone_format_regex = r"^\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$"

    # Create confirmation_message from department/purpose
    confirmation_message = None
    department = phone_confirmation.get("department", "")
    purpose = phone_confirmation.get("purpose", "")

    if department:
        confirmation_message = (
            f"Call {department} to confirm the correct mailing address for appeals."
        )
    elif purpose:
        # Truncate purpose if too long
        if len(purpose) > 120:
            purpose = purpose[:117] + "..."
        confirmation_message = f"Call to confirm: {purpose}"

    # Build phone_confirmation_policy with EXACTLY the fields CityRegistry expects
    phone_confirmation_policy = {
        "required": phone_confirmation.get("required", False),
    }

    # Add optional fields only if they have values
    if phone_format_regex:
        phone_confirmation_policy["phone_format_regex"] = phone_format_regex

    if confirmation_message:
        phone_confirmation_policy["confirmation_message"] = confirmation_message

    # Default confirmation deadline: 24 hours
    phone_confirmation_policy["confirmation_deadline_hours"] = 24

    if phone_number_examples:
        phone_confirmation_policy["phone_number_examples"] = phone_number_examples

    # Transform verification to verification_metadata
    verification = simplified_data.get("verification", {})
    verification_metadata = {
        "last_updated": verification.get("verified_at", datetime.now().isoformat()),
        "source": verification.get("source_type", "unknown"),
        "confidence_score": _map_verification_status_to_score(
            verification.get("status", "unverified")
        ),
        "notes": _clean_notes(verification.get("source_note", "")),
        "verified_by": verification.get("last_validated_by", ""),
    }

    # Create sections from authority (Schema 4.3.0 requires minimal section structure)
    sections = {
        section_id: {
            "name": authority.get("name", name),
            # Optional overrides (same structure as top-level):
            "appeal_mail_address": appeal_mail_address,
            "phone_confirmation_policy": phone_confirmation_policy,
            "routing_rule": simplified_data.get("routing_rule", "direct"),
        }
    }

    # Get routing rule (default to direct)
    routing_rule = simplified_data.get("routing_rule", "direct")

    # Get submission methods info
    submission_methods = simplified_data.get("submission_methods", {})
    online_appeal_available = submission_methods.get("online_allowed", False)
    online_appeal_url = None  # Would need additional research

    # Official confirmation info (for reference)
    official_confirmation_phone = simplified_data.get("official_confirmation_phone", "")
    official_confirmation_department = simplified_data.get(
        "official_confirmation_department", ""
    )
    official_confirmation_purpose = simplified_data.get(
        "official_confirmation_purpose", ""
    )

    # Appeal info
    appeal_info = simplified_data.get("appeal_info", {})
    timezone = _get_city_timezone(state, city_id, appeal_info.get("timezone"))
    appeal_deadline_days = appeal_info.get("appeal_deadline_days", 21)

    # Build Schema 4.3.0 structure
    schema_4_3_0 = {
        "city_id": city_id,
        "name": name,
        "jurisdiction": "city",
        "citation_patterns": citation_patterns,
        "appeal_mail_address": appeal_mail_address,
        "phone_confirmation_policy": phone_confirmation_policy,
        "routing_rule": routing_rule,
        "sections": sections,
        "verification_metadata": verification_metadata,
        "timezone": timezone,
        "appeal_deadline_days": appeal_deadline_days,
        "online_appeal_available": online_appeal_available,
        "online_appeal_url": online_appeal_url,
        # Include original simplified data fields for reference
        "_original_state": state,
        "_original_country": country,
        "_original_official_confirmation": {
            "phone": official_confirmation_phone,
            "department": official_confirmation_department,
            "purpose": official_confirmation_purpose,
        },
        "_metadata": {
            "transformed_at": datetime.now().isoformat(),
            "transformed_by": "transform_simplified_to_schema.py",
            "source_format": "simplified_city_json",
            "schema_version": "4.3.0",
        },
    }

    # Remove empty fields that would cause validation issues
    schema_4_3_0 = _clean_empty_fields(schema_4_3_0)

    return schema_4_3_0


def _map_confidence_to_score(confidence: str) -> float:
    """Map confidence string to numeric score (0.0-1.0)."""
    confidence_map = {
        "high": 0.9,
        "medium": 0.7,
        "low": 0.5,
        "very_low": 0.3,
        "unknown": 0.1,
    }
    return confidence_map.get(confidence.lower(), 0.5)


def _map_verification_status_to_score(status: str) -> float:
    """Map verification status to confidence score."""
    status_map = {
        "verified": 0.9,
        "needs_confirmation": 0.6,
        "unverified": 0.3,
        "incomplete": 0.3,
        "invalid": 0.1,
    }
    return status_map.get(status.lower(), 0.5)


def _clean_notes(notes: str) -> str:
    """Clean notes by removing special characters and markdown artifacts."""
    if not notes:
        return ""

    import re

    # Remove markdown-style references like 【830560214250021†L190-L210】
    notes = re.sub(r"【[^】]*†L\d+-L\d+】", "", notes)
    # Remove other special characters that aren't valid in plain text
    notes = re.sub(r"[【】†※★☆]", "", notes)
    # Clean up multiple spaces
    notes = re.sub(r"\s+", " ", notes)
    return notes.strip()


def _get_city_timezone(
    state: str, city_id: str, default_timezone: Optional[str] = None
) -> str:
    """Get appropriate timezone for a city based on state/city."""
    # State-based timezone mapping
    state_timezone_map = {
        "CA": "America/Los_Angeles",
        "WA": "America/Los_Angeles",
        "OR": "America/Los_Angeles",
        "NV": "America/Los_Angeles",
        "AZ": "America/Phoenix",
        "CO": "America/Denver",
        "TX": "America/Chicago",
        "IL": "America/Chicago",
        "WI": "America/Chicago",
        "MN": "America/Chicago",
        "IA": "America/Chicago",
        "MO": "America/Chicago",
        "AR": "America/Chicago",
        "LA": "America/Chicago",
        "MS": "America/Chicago",
        "AL": "America/Chicago",
        "TN": "America/Chicago",
        "KY": "America/Chicago",
        "IN": "America/Indiana/Indianapolis",
        "MI": "America/Detroit",
        "OH": "America/New_York",
        "PA": "America/New_York",
        "NY": "America/New_York",
        "NJ": "America/New_York",
        "CT": "America/New_York",
        "MA": "America/New_York",
        "RI": "America/New_York",
        "VT": "America/New_York",
        "NH": "America/New_York",
        "ME": "America/New_York",
        "MD": "America/New_York",
        "DC": "America/New_York",
        "VA": "America/New_York",
        "WV": "America/New_York",
        "DE": "America/New_York",
        "NC": "America/New_York",
        "SC": "America/New_York",
        "GA": "America/New_York",
        "FL": "America/New_York",
    }

    # Special city-specific overrides
    city_timezone_map = {
        "us-az-phoenix": "America/Phoenix",
        "us-az-tucson": "America/Phoenix",
        "us-in-indianapolis": "America/Indiana/Indianapolis",
        "us-mi-detroit": "America/Detroit",
        "us-tx-el_paso": "America/Denver",  # El Paso is in Mountain Time
        "us-tx-cd_juarez": "America/Denver",  # Border area
    }

    # Check city-specific first
    if city_id in city_timezone_map:
        return city_timezone_map[city_id]

    # If default timezone is provided, check if it's reasonable for this location
    if default_timezone:
        # List of timezones that are reasonable for each state
        reasonable_timezones = {
            "CA": ["America/Los_Angeles"],
            "WA": ["America/Los_Angeles"],
            "OR": ["America/Los_Angeles"],
            "NV": ["America/Los_Angeles"],
            "AZ": ["America/Phoenix"],
            "CO": ["America/Denver"],
            "TX": [
                "America/Chicago",
                "America/Denver",
            ],  # Most of TX is Central, El Paso is Mountain
            "IL": ["America/Chicago"],
            "WI": ["America/Chicago"],
            "MN": ["America/Chicago"],
            "IA": ["America/Chicago"],
            "MO": ["America/Chicago"],
            "AR": ["America/Chicago"],
            "LA": ["America/Chicago"],
            "MS": ["America/Chicago"],
            "AL": ["America/Chicago"],
            "TN": ["America/Chicago"],
            "KY": ["America/Chicago"],
            "IN": ["America/Chicago", "America/Indiana/Indianapolis"],
            "MI": ["America/Detroit", "America/Chicago"],
            "OH": ["America/New_York", "America/Chicago"],
            "PA": ["America/New_York"],
            "NY": ["America/New_York"],
            "NJ": ["America/New_York"],
            "CT": ["America/New_York"],
            "MA": ["America/New_York"],
            "RI": ["America/New_York"],
            "VT": ["America/New_York"],
            "NH": ["America/New_York"],
            "ME": ["America/New_York"],
            "MD": ["America/New_York"],
            "DC": ["America/New_York"],
            "VA": ["America/New_York"],
            "WV": ["America/New_York", "America/Chicago"],
            "DE": ["America/New_York"],
            "NC": ["America/New_York"],
            "SC": ["America/New_York"],
            "GA": ["America/New_York"],
            "FL": [
                "America/New_York",
                "America/Chicago",
            ],  # Florida spans two timezones
        }

        # Check if the default timezone is reasonable for this state
        state_reasonable = reasonable_timezones.get(state, [])
        if default_timezone in state_reasonable:
            return default_timezone

    # Fall back to state mapping
    return state_timezone_map.get(state, "America/Los_Angeles")


def _clean_empty_fields(data: Any) -> Any:
    """Recursively remove empty fields from data."""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            cleaned_value = _clean_empty_fields(value)
            # Skip empty values (None, empty string, empty list, empty dict)
            if cleaned_value is None:
                continue
            if isinstance(cleaned_value, str) and cleaned_value == "":
                continue
            if isinstance(cleaned_value, list) and len(cleaned_value) == 0:
                continue
            if isinstance(cleaned_value, dict) and len(cleaned_value) == 0:
                continue
            result[key] = cleaned_value
        return result
    elif isinstance(data, list):
        result = [_clean_empty_fields(item) for item in data]
        # Filter out None values from lists
        return [item for item in result if item is not None]
    else:
        return data


def validate_with_schema_adapter(schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean schema data using SchemaAdapter if available.

    Returns validated schema data and prints any warnings/errors.
    """
    if not SCHEMA_ADAPTER_AVAILABLE:
        print("  [WARNING] Schema adapter not available, skipping validation")
        return schema_data

    try:
        adapter = SchemaAdapter(strict_mode=False)
        result = adapter.adapt_city_schema(schema_data)

        if result.success:
            if result.warnings:
                print(f"  [WARNING] Validation warnings ({len(result.warnings)}):")
                for warning in result.warnings[:5]:  # Show first 5 warnings
                    print(f"    - {warning}")
                if len(result.warnings) > 5:
                    print(f"    ... and {len(result.warnings) - 5} more warnings")

            if result.errors:
                print(f"  [ERROR] Validation errors ({len(result.errors)}):")
                for error in result.errors:
                    print(f"    - {error}")
                print(
                    "  [WARNING] Returning original (unvalidated) schema due to errors"
                )
                return schema_data

            print(f"  [OK] Schema validation passed")
            return result.transformed_data
        else:
            print(f"  [ERROR] Schema validation failed:")
            for error in result.errors:
                print(f"    - {error}")
            print("  [WARNING] Returning original (unvalidated) schema")
            return schema_data

    except Exception as e:
        print(f"  [ERROR] Schema adapter error: {e}")
        print("  [WARNING] Returning original schema")
        return schema_data


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Transform simplified city JSON to Schema 4.3.0 format"
    )
    parser.add_argument("input_file", help="Input simplified JSON file")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: <city_id>.json in current directory)",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate output with SchemaAdapter"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: Input file does not exist: {input_path}")
            sys.exit(1)

        if args.verbose:
            print(f"Loading simplified city data from: {input_path}")

        # Load simplified data
        simplified_data = load_simplified_json(input_path)

        # Get city info for output filename
        city_id = simplified_data.get("city_id", "unknown")
        city_name = simplified_data.get("name", "unknown")
        state = simplified_data.get("state", "")

        if args.verbose:
            print(f"Transforming: {city_name}, {state} ({city_id})")

        # Transform to Schema 4.3.0
        schema_data = transform_simplified_to_schema(simplified_data)

        # Validate with SchemaAdapter if requested
        if args.validate and SCHEMA_ADAPTER_AVAILABLE:
            if args.verbose:
                print("Validating with SchemaAdapter...")
            schema_data = validate_with_schema_adapter(schema_data)
        elif args.validate and not SCHEMA_ADAPTER_AVAILABLE:
            print("Warning: SchemaAdapter not available, skipping validation")

        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            # Generate output filename from city_id (Schema 4.3.0 format)
            output_path = Path(f"{city_id}.json")

        # Save output
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved Schema 4.3.0 data to: {output_path}")

        # Show summary
        appeal_status = schema_data.get("appeal_mail_address", {}).get(
            "status", "unknown"
        )
        citation_patterns = len(schema_data.get("citation_patterns", []))
        sections = len(schema_data.get("sections", {}))

        print(f"\nSummary:")
        print(f"  City: {city_name}, {state}")
        print(f"  City ID: {city_id}")
        print(f"  Appeal address status: {appeal_status}")
        print(f"  Citation patterns: {citation_patterns}")
        print(f"  Sections: {sections}")
        print(f"  Jurisdiction: {schema_data.get('jurisdiction', 'unknown')}")

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
