#!/usr/bin/env python3
"""
Test script for Boston City Configuration (us-ma-boston)

Tests that Boston's special requirements are correctly loaded and exposed
via the Citation Validation Service.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.citation import CitationValidator


def test_boston_configuration():
    """Test Boston city configuration loading and special requirements."""
    print("🦞 Testing Boston Configuration (us-ma-boston)")
    print("=" * 60)

    # Initialize validator
    cities_dir = Path(__file__).parent.parent / "cities"
    validator = CitationValidator(cities_dir)

    # Test Boston citation
    citation = "BO1234567"  # Boston Parking Commission format
    print(f"Validating Boston citation: {citation}")

    result = validator.validate_citation(citation)

    if not result.is_valid:
        print(f"❌ Citation should be valid, got: {result.error_message}")
        sys.exit(1)

    print("✅ Citation matched correctly")
    print(f"   City ID: {result.city_id}")
    print(f"   Section ID: {result.section_id}")

    if result.city_id != "us-ma-boston":
        print(f"❌ Expected city_id 'us-ma-boston', got '{result.city_id}'")
        sys.exit(1)

    # Check special requirements
    print("\n🔍 Checking Special Requirements")
    special_reqs = result.special_requirements

    if not special_reqs:
        print("❌ Special requirements missing from validation result")
        sys.exit(1)

    print(f"   {special_reqs}")

    # Verify specific fields from TODO requirements
    # "High-volume target, digital signatures accepted"
    if special_reqs.get("digital_signature_accepted") is True:
        print("✅ Digital signatures accepted")
    else:
        print("❌ 'digital_signature_accepted' should be True")
        sys.exit(1)

    # "Simple checkbox form for third-party appeals"
    if special_reqs.get("representative_checkbox_enabled") is True:
        print("✅ Representative checkbox enabled")
    else:
        print("❌ 'representative_checkbox_enabled' should be True")
        sys.exit(1)

    print("\n✅ Boston configuration verification passed!")


if __name__ == "__main__":
    test_boston_configuration()
