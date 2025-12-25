#!/usr/bin/env python3
"""
Extract simplified city data from phase1 JSON files.
Focuses ONLY on city_parking_authority sections, ignoring campuses/police departments.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SimplifiedCitationPattern:
    """Simplified citation pattern information."""

    regex: str
    description: str
    example_numbers: Optional[List[str]] = None
    confidence: str = "low"  # low, medium, high
    visual_markers: Optional[List[str]] = None
    notes: Optional[str] = None


@dataclass
class SimplifiedAppealAddress:
    """Simplified appeal address with explicit status."""

    status: str  # complete, incomplete, missing, routes_elsewhere, not_applicable
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


@dataclass
class SimplifiedSubmissionMethods:
    """Simplified submission method information."""

    mail_allowed: bool = False
    online_allowed: bool = False
    in_person_allowed: bool = False
    preferred_method: Optional[str] = None  # mail, online, in_person
    method_constraints: Optional[List[str]] = None
    notes: Optional[str] = None


@dataclass
class SimplifiedPhoneConfirmation:
    """Simplified phone confirmation policy."""

    required: bool = False
    when_required: str = (
        "if_address_incomplete"  # always, if_address_incomplete, if_status_missing
    )
    phone_numbers: Optional[List[str]] = None
    alt_phone_numbers: Optional[List[str]] = None
    department: Optional[str] = None
    purpose: Optional[str] = None


@dataclass
class SimplifiedVerification:
    """Simplified verification metadata."""

    status: str  # verified, needs_confirmation, unverified
    verified_at: Optional[str] = None
    source_type: Optional[str] = None  # official_webpage, phone_call, inferred
    source_note: Optional[str] = None
    needs_confirmation: bool = False
    operational_ready: bool = False
    last_checked: Optional[str] = None
    last_validated_by: Optional[str] = None


@dataclass
class SimplifiedCityAuthority:
    """Simplified city authority information."""

    section_id: str
    name: str
    authority_name: str
    jurisdiction: str
    abbrev: Optional[List[str]] = None
    serves_basis: Optional[str] = None
    serves_description: Optional[str] = None


@dataclass
class SimplifiedCityData:
    """Complete simplified city data structure."""

    city_id: str
    name: str
    state: str
    country: str

    authority: SimplifiedCityAuthority
    citation_pattern: SimplifiedCitationPattern
    appeal_address: SimplifiedAppealAddress
    submission_methods: SimplifiedSubmissionMethods
    phone_confirmation: SimplifiedPhoneConfirmation
    verification: SimplifiedVerification

    # Additional info
    official_confirmation_phone: Optional[str] = None
    official_confirmation_department: Optional[str] = None
    official_confirmation_purpose: Optional[str] = None

    appeal_info: Optional[Dict[str, Any]] = None
    routing_rule: str = "direct"

    # QA info (for reference)
    qa_has_sections: Optional[bool] = None
    qa_has_city_confirmation_phone: Optional[bool] = None
    qa_all_sections_have_valid_routing: Optional[bool] = None
    qa_blocking_issues: Optional[List[str]] = None
    qa_known_gaps: Optional[List[str]] = None


def clean_json_content(content: str) -> str:
    """Clean JSON content by removing markdown backticks and fixing common issues."""
    # Remove markdown code blocks
    content = re.sub(r"```[a-z]*\n", "", content)
    content = re.sub(r"\n```", "", content)
    # Fix common JSON issues
    content = content.replace('"""', '"')
    return content


def find_city_parking_authority(
    sections: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Find the city_parking_authority section in the sections list."""
    for section in sections:
        if section.get("section_type") == "city_parking_authority":
            return section
    return None


def extract_simplified_city_data(phase1_data: Dict[str, Any]) -> SimplifiedCityData:
    """Extract simplified city data from phase1 JSON structure."""

    # Basic city info
    city_id = phase1_data.get("city_id", "")
    name = phase1_data.get("city", "")
    state = phase1_data.get("state", "")
    country = phase1_data.get("country", "")

    # Official confirmation info
    official_conf = phase1_data.get("official_confirmation", {}).get(
        "primary_phone", {}
    )
    official_phone = official_conf.get("phone")
    official_department = official_conf.get("department")
    official_purpose = official_conf.get("purpose")

    # Find city parking authority
    sections = phase1_data.get("phase1_routing", {}).get("sections", [])
    city_section = find_city_parking_authority(sections)

    if not city_section:
        raise ValueError(f"No city_parking_authority found in {city_id}")

    # Extract authority info
    authority = SimplifiedCityAuthority(
        section_id=city_section.get("section_id", ""),
        name=city_section.get("canonical_section_name", ""),
        authority_name=city_section.get("authority_name", ""),
        jurisdiction=city_section.get("jurisdiction", ""),
        abbrev=city_section.get("abbrev"),
        serves_basis=city_section.get("serves", {}).get("basis"),
        serves_description=city_section.get("serves", {}).get("description"),
    )

    # Extract citation pattern
    how_to_recognize = city_section.get("how_to_recognize", {})
    citation_pattern = SimplifiedCitationPattern(
        regex=how_to_recognize.get("citation_id_pattern", ""),
        description=f"{name} parking citation format",
        example_numbers=how_to_recognize.get("examples"),
        confidence=how_to_recognize.get("pattern_confidence", "low"),
        visual_markers=how_to_recognize.get("visual_markers"),
        notes=how_to_recognize.get("notes"),
    )

    # Extract appeal address
    appeal_mail = city_section.get("appeal_mail_to", {})
    appeal_status = appeal_mail.get("status", "missing")

    appeal_address = SimplifiedAppealAddress(
        status=appeal_status,
        department=appeal_mail.get("department"),
        attention=appeal_mail.get("attention"),
        address1=appeal_mail.get("address1"),
        address2=appeal_mail.get("address2"),
        city=appeal_mail.get("city"),
        state=appeal_mail.get("state"),
        zip=appeal_mail.get("zip"),
        country=appeal_mail.get("country"),
        routes_to_section_id=appeal_mail.get("routes_to_section_id"),
        missing_fields=appeal_mail.get("missing_fields"),
        missing_reason=appeal_mail.get("missing_reason"),
    )

    # Extract submission methods
    submission = city_section.get("submission_methods", {})
    submission_methods = SimplifiedSubmissionMethods(
        mail_allowed=submission.get("mail_allowed", False),
        online_allowed=submission.get("online_allowed", False),
        in_person_allowed=submission.get("in_person_allowed", False),
        preferred_method=submission.get("preferred_method"),
        method_constraints=submission.get("method_constraints"),
        notes=submission.get("notes"),
    )

    # Extract phone confirmation
    confirm_phone = city_section.get("confirm_by_phone", {})
    phone_numbers = []
    if confirm_phone.get("phone"):
        phone_numbers.append(confirm_phone.get("phone"))
    alt_phone_numbers = []
    if confirm_phone.get("alt_phone"):
        alt_phone_numbers.append(confirm_phone.get("alt_phone"))

    # Determine when phone confirmation is required
    when_required = "if_address_incomplete"
    if appeal_status != "complete":
        when_required = "always"
    elif confirm_phone.get("required", False):
        when_required = "always"

    phone_confirmation = SimplifiedPhoneConfirmation(
        required=confirm_phone.get("required", False),
        when_required=when_required,
        phone_numbers=phone_numbers if phone_numbers else None,
        alt_phone_numbers=alt_phone_numbers if alt_phone_numbers else None,
        department=confirm_phone.get("department"),
        purpose=confirm_phone.get("purpose"),
    )

    # Extract verification
    verification_data = city_section.get("verification", {})
    verification = SimplifiedVerification(
        status=verification_data.get("status", "unverified"),
        verified_at=verification_data.get("verified_at"),
        source_type=verification_data.get("verified_source_type"),
        source_note=verification_data.get("verified_source_note"),
        needs_confirmation=verification_data.get("needs_confirmation", False),
        operational_ready=verification_data.get("status") == "verified",
        last_checked=verification_data.get("verified_source_last_checked"),
        last_validated_by=verification_data.get("last_validated_by"),
    )

    # Extract routing rule
    routing_rule = city_section.get("routing_rule", "direct")

    # Extract QA info
    qa = phase1_data.get("qa", {})

    # Create appeal info
    appeal_info = {
        "timezone": "America/Los_Angeles",  # Default, adjust per city if known
        "appeal_deadline_days": 21,  # Default, adjust if known
        "online_appeal_available": submission_methods.online_allowed,
        "online_appeal_url": None,  # Would need to be filled from additional research
    }

    # Create simplified city data
    simplified_data = SimplifiedCityData(
        city_id=city_id,
        name=name,
        state=state,
        country=country,
        authority=authority,
        citation_pattern=citation_pattern,
        appeal_address=appeal_address,
        submission_methods=submission_methods,
        phone_confirmation=phone_confirmation,
        verification=verification,
        official_confirmation_phone=official_phone,
        official_confirmation_department=official_department,
        official_confirmation_purpose=official_purpose,
        appeal_info=appeal_info,
        routing_rule=routing_rule,
        qa_has_sections=qa.get("has_sections"),
        qa_has_city_confirmation_phone=qa.get("has_city_confirmation_phone"),
        qa_all_sections_have_valid_routing=qa.get("all_sections_have_valid_routing"),
        qa_blocking_issues=qa.get("blocking_issues"),
        qa_known_gaps=qa.get("known_gaps"),
    )

    return simplified_data


def dataclass_to_dict(obj):
    """Convert dataclass to dict, removing None values."""
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for field in obj.__dataclass_fields__:
            value = getattr(obj, field)
            if value is not None:
                if hasattr(value, "__dataclass_fields__"):
                    result[field] = dataclass_to_dict(value)
                elif isinstance(value, list):
                    result[field] = [
                        dataclass_to_dict(item)
                        if hasattr(item, "__dataclass_fields__")
                        else item
                        for item in value
                    ]
                elif isinstance(value, dict):
                    result[field] = {
                        k: dataclass_to_dict(v)
                        if hasattr(v, "__dataclass_fields__")
                        else v
                        for k, v in value.items()
                    }
                else:
                    result[field] = value
        return result
    return obj


def save_simplified_json(simplified_data: SimplifiedCityData, output_path: str):
    """Save simplified city data as JSON."""
    # Convert to dict
    data_dict = dataclass_to_dict(simplified_data)

    # Add metadata
    data_dict["_metadata"] = {
        "source_format": "phase1",
        "extracted_at": datetime.now().isoformat(),
        "extracted_by": "extract_city_simple.py",
        "schema_version": "1.0.0",
    }

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data_dict, f, indent=2, ensure_ascii=False)

    print(f"Saved simplified city data to: {output_path}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Extract simplified city data from phase1 JSON files"
    )
    parser.add_argument("input_file", help="Input phase1 JSON file")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: <cityname>.json in current directory)",
    )

    args = parser.parse_args()

    try:
        # Read and clean input file
        with open(args.input_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Clean JSON content
        content = clean_json_content(content)

        # Parse JSON
        phase1_data = json.loads(content)

        # Extract simplified data
        simplified_data = extract_simplified_city_data(phase1_data)

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            # Generate output filename from city_id
            city_id = simplified_data.city_id
            city_name = city_id.split("-")[-1].replace("_", "")
            output_path = f"{city_name}.json"

        # Save simplified data
        save_simplified_json(simplified_data, output_path)

        # Print summary
        print(f"\nExtracted city: {simplified_data.name}, {simplified_data.state}")
        print(f"Authority: {simplified_data.authority.name}")
        print(f"Appeal address status: {simplified_data.appeal_address.status}")
        print(f"Mail allowed: {simplified_data.submission_methods.mail_allowed}")
        print(f"Verification status: {simplified_data.verification.status}")

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error extracting city data: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
