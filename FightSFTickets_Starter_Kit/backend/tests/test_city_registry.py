#!/usr/bin/env python3
"""
Test script for City Registry Service (Schema 4.3.0)

Tests loading of city configurations, citation matching, address routing,
and phone confirmation policies.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.city_registry import (
    AppealMailAddress,
    AppealMailStatus,
    CitationPattern,
    CityConfiguration,
    CityRegistry,
    CitySection,
    Jurisdiction,
    PhoneConfirmationPolicy,
    RoutingRule,
    VerificationMetadata,
)


def test_city_registry_basic():
    """Test basic CityRegistry functionality."""
    print("🧪 Testing City Registry Service")
    print("=" * 60)

    # Initialize registry with cities directory
    cities_dir = Path(__file__).parent.parent.parent / "cities"
    registry = CityRegistry(cities_dir)

    # Load cities
    print(f"📂 Loading cities from: {cities_dir}")
    registry.load_cities()

    # List loaded cities
    cities = registry.get_all_cities()
    print(f"✅ Loaded {len(cities)} cities:")
    for city in cities:
        print(
            f"   - {city['name']} ({city['city_id']}): "
            f"{city['citation_pattern_count']} patterns, "
            f"{city['section_count']} sections"
        )

    print()


def test_citation_matching():
    """Test citation number matching."""
    print("🔍 Testing Citation Matching")
    print("-" * 40)

    cities_dir = Path(__file__).parent.parent.parent / "cities"
    registry = CityRegistry(cities_dir)
    registry.load_cities()

    # Test cases: (citation_number, expected_city, expected_section)
    test_cases = [
        ("912345678", "sf", "sfmta"),  # SFMTA 9-digit
        ("998765432", "sf", "sfmta"),  # Another SFMTA
        ("SF123456", "sf", "sfpd"),  # SFPD format
        ("SFSU12345", "sf", "sfsu"),  # SFSU format
        ("CAMPUS678", "sf", "sfsu"),  # Campus format
        ("MU123456", "sf", "sfmud"),  # SFMUD format
        ("123456", None, None),  # Too short (no match)
        ("INVALID", None, None),  # Invalid format
    ]

    passed = 0
    failed = 0

    for citation, exp_city, exp_section in test_cases:
        match = registry.match_citation(citation)

        if exp_city is None and match is None:
            print(f"✅ '{citation}': Correctly no match")
            passed += 1
        elif match and match[0] == exp_city and match[1] == exp_section:
            print(f"✅ '{citation}': Matched {match[0]}/{match[1]}")
            passed += 1
        else:
            print(f"❌ '{citation}': Expected {exp_city}/{exp_section}, got {match}")
            failed += 1

    print(f"\n📊 Citation matching: {passed} passed, {failed} failed")
    print()


def test_address_retrieval():
    """Test mailing address retrieval."""
    print("📫 Testing Address Retrieval")
    print("-" * 40)

    cities_dir = Path(__file__).parent.parent.parent / "cities"
    registry = CityRegistry(cities_dir)
    registry.load_cities()

    # Test cases: (city_id, section_id, expected_status)
    test_cases = [
        ("sf", "sfmta", AppealMailStatus.COMPLETE),
        ("sf", "sfpd", AppealMailStatus.COMPLETE),
        ("sf", "sfsu", AppealMailStatus.COMPLETE),
        ("sf", "sfmud", AppealMailStatus.ROUTES_ELSEWHERE),
        ("sf", None, AppealMailStatus.COMPLETE),  # Default city address
        ("nonexistent", None, None),  # Non-existent city
    ]

    passed = 0
    failed = 0

    for city_id, section_id, exp_status in test_cases:
        address = registry.get_mail_address(city_id, section_id)

        if exp_status is None and address is None:
            print(f"✅ {city_id}/{section_id or 'default'}: Correctly no address")
            passed += 1
        elif address and address.status == exp_status:
            print(f"✅ {city_id}/{section_id or 'default'}: {address.status.value}")
            if address.status == AppealMailStatus.COMPLETE:
                print(
                    f"     📍 {address.address1}, {address.city}, "
                    f"{address.state} {address.zip}"
                )
            elif address.status == AppealMailStatus.ROUTES_ELSEWHERE:
                print(f"     ➡️  Routes to: {address.routes_to_section_id}")
            passed += 1
        else:
            actual = address.status.value if address else "None"
            expected = exp_status.value if exp_status else "None"
            print(
                f"❌ {city_id}/{section_id or 'default'}: "
                f"Expected {expected}, got {actual}"
            )
            failed += 1

    print(f"\n📊 Address retrieval: {passed} passed, {failed} failed")
    print()


def test_phone_validation():
    """Test phone confirmation policies."""
    print("📞 Testing Phone Validation")
    print("-" * 40)

    cities_dir = Path(__file__).parent.parent.parent / "cities"
    registry = CityRegistry(cities_dir)
    registry.load_cities()

    # Test cases: (city_id, section_id, phone_number, expected_valid)
    test_cases = [
        ("sf", "sfmta", "+14155551212", True),  # SFMTA (no requirement)
        ("sf", "sfmta", "invalid", True),  # SFMTA accepts invalid (no policy)
        ("sf", "sfpd", "+14155531651", True),  # SFPD valid format
        ("sf", "sfpd", "4155531651", False),  # SFPD missing +1
        ("sf", "sfpd", "+141555", False),  # SFPD too short
        ("sf", "sfsu", "+14155551212", True),  # SFSU (no requirement)
        ("sf", None, "+14155551212", True),  # Default city (no requirement)
    ]

    passed = 0
    failed = 0

    for city_id, section_id, phone, exp_valid in test_cases:
        is_valid, error = registry.validate_phone_for_city(city_id, phone, section_id)

        if is_valid == exp_valid:
            print(
                f"✅ {city_id}/{section_id or 'default'}: "
                f"'{phone}' -> {'Valid' if is_valid else 'Invalid'}"
            )
            if error:
                print(f"     💬 {error}")
            passed += 1
        else:
            print(
                f"❌ {city_id}/{section_id or 'default'}: "
                f"'{phone}' -> Expected {'valid' if exp_valid else 'invalid'}, "
                f"got {'valid' if is_valid else 'invalid'}"
            )
            if error:
                print(f"     💬 {error}")
            failed += 1

    print(f"\n📊 Phone validation: {passed} passed, {failed} failed")
    print()


def test_routing_rules():
    """Test routing rule retrieval."""
    print("🔄 Testing Routing Rules")
    print("-" * 40)

    cities_dir = Path(__file__).parent.parent.parent / "cities"
    registry = CityRegistry(cities_dir)
    registry.load_cities()

    # Test cases: (city_id, section_id, expected_rule)
    test_cases = [
        ("sf", "sfmta", RoutingRule.DIRECT),
        ("sf", "sfpd", RoutingRule.DIRECT),
        ("sf", "sfmud", RoutingRule.ROUTES_TO_SECTION),
        ("sf", None, RoutingRule.DIRECT),  # Default city rule
    ]

    passed = 0
    failed = 0

    for city_id, section_id, exp_rule in test_cases:
        rule = registry.get_routing_rule(city_id, section_id)

        if rule == exp_rule:
            print(f"✅ {city_id}/{section_id or 'default'}: {rule.value}")
            passed += 1
        else:
            actual = rule.value if rule else "None"
            expected = exp_rule.value
            print(
                f"❌ {city_id}/{section_id or 'default'}: "
                f"Expected {expected}, got {actual}"
            )
            failed += 1

    print(f"\n📊 Routing rules: {passed} passed, {failed} failed")
    print()


def test_config_validation():
    """Test city configuration validation."""
    print("✅ Testing Configuration Validation")
    print("-" * 40)

    # Test a valid configuration
    valid_config = CityConfiguration(
        city_id="test",
        name="Test City",
        jurisdiction=Jurisdiction.CITY,
        citation_patterns=[
            CitationPattern(
                regex=r"^TEST\d{3}$",
                section_id="test_section",
                description="Test citation",
            )
        ],
        appeal_mail_address=AppealMailAddress(
            status=AppealMailStatus.COMPLETE,
            department="Test Department",
            address1="123 Test St",
            city="Test City",
            state="TS",
            zip="12345",
            country="USA",
        ),
        phone_confirmation_policy=PhoneConfirmationPolicy(required=False),
        routing_rule=RoutingRule.DIRECT,
        sections={
            "test_section": CitySection(
                section_id="test_section",
                name="Test Section",
                routing_rule=RoutingRule.DIRECT,
            )
        },
        verification_metadata=VerificationMetadata(
            last_updated="2024-01-01",
            source="test",
            confidence_score=0.9,
        ),
    )

    # Test an invalid configuration (missing required fields)
    invalid_config = CityConfiguration(
        city_id="",
        name="",
        jurisdiction=Jurisdiction.CITY,
        citation_patterns=[],
        appeal_mail_address=AppealMailAddress(
            status=AppealMailStatus.COMPLETE,
            department="",  # Empty required field
            address1="",
            city="",
            state="",
            zip="",
            country="",
        ),
        phone_confirmation_policy=PhoneConfirmationPolicy(required=True),
        routing_rule=RoutingRule.DIRECT,
        sections={},
        verification_metadata=VerificationMetadata(
            last_updated="2024-01-01",
            source="test",
            confidence_score=0.9,
        ),
    )

    # Create registry for validation
    registry = CityRegistry()

    # Test validation
    valid_errors = registry._validate_city_config(valid_config)
    invalid_errors = registry._validate_city_config(invalid_config)

    if not valid_errors:
        print("✅ Valid configuration passes validation")
    else:
        print(f"❌ Valid configuration failed validation: {valid_errors}")

    if invalid_errors:
        print("✅ Invalid configuration correctly fails validation:")
        for error in invalid_errors[:3]:  # Show first 3 errors
            print(f"   • {error}")
        if len(invalid_errors) > 3:
            print(f"   ... and {len(invalid_errors) - 3} more errors")
    else:
        print("❌ Invalid configuration should have validation errors")

    print()


def test_json_loading():
    """Test loading and parsing of JSON configuration."""
    print("📄 Testing JSON Configuration Loading")
    print("-" * 40)

    cities_dir = Path(__file__).parent.parent.parent / "cities"
    sf_json_path = cities_dir / "sf.json"

    if not sf_json_path.exists():
        print(f"❌ SF JSON file not found: {sf_json_path}")
        return

    try:
        with open(sf_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check required fields
        required_fields = [
            "city_id",
            "name",
            "jurisdiction",
            "citation_patterns",
            "appeal_mail_address",
            "phone_confirmation_policy",
            "routing_rule",
            "sections",
            "verification_metadata",
        ]

        missing = [field for field in required_fields if field not in data]
        if missing:
            print(f"❌ Missing required fields: {missing}")
        else:
            print(f"✅ All required fields present")

        # Check citation patterns
        patterns = data.get("citation_patterns", [])
        print(f"✅ Citation patterns: {len(patterns)} found")

        # Check sections
        sections = data.get("sections", {})
        print(f"✅ Sections: {len(sections)} found")

        # Check appeal mail address status
        appeal_addr = data.get("appeal_mail_address", {})
        status = appeal_addr.get("status")
        print(f"✅ Appeal mail address status: {status}")

        # Test that the JSON can be loaded by registry
        registry = CityRegistry(cities_dir)
        registry.load_cities()

        if "sf" in registry.city_configs:
            sf_config = registry.city_configs["sf"]
            print(f"✅ SF configuration loaded successfully")
            print(f"   • Name: {sf_config.name}")
            print(f"   • Jurisdiction: {sf_config.jurisdiction.value}")
            print(f"   • Citation patterns: {len(sf_config.citation_patterns)}")
        else:
            print(f"❌ SF configuration not loaded")

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")

    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🏙️  CITY REGISTRY TEST SUITE (Schema 4.3.0)")
    print("=" * 60 + "\n")

    try:
        test_city_registry_basic()
        test_json_loading()
        test_citation_matching()
        test_address_retrieval()
        test_phone_validation()
        test_routing_rules()
        test_config_validation()

        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
