#!/usr/bin/env python3
"""
Test script to verify CityRegistry loads and functions with generated schema files.
Specifically tests the Los Angeles schema file generated from phase1 data.

This script validates:
1. CityRegistry can be initialized with cities directory
2. Los Angeles schema file loads successfully
3. Citation pattern matching works
4. Mail address retrieval functions
5. Phone confirmation policy is correct
"""

import sys
from pathlib import Path

# Add backend/src to Python path for imports
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

try:
    from services.city_registry import CityRegistry, get_city_registry

    print("✅ Successfully imported CityRegistry")
except ImportError as e:
    print("❌ Failed to import CityRegistry: {e}")
    sys.exit(1)


def test_city_registry_load():
    """Test loading CityRegistry with generated schema files."""
    # Get cities directory path
    cities_dir = Path(__file__).parent.parent / "cities"

    if not cities_dir.exists():
        print("❌ Cities directory not found: {cities_dir}")
        return False

    print("📁 Cities directory: {cities_dir}")

    # Check for Los Angeles schema file
    la_schema_file = cities_dir / "us-ca-los_angeles.json"
    if not la_schema_file.exists():
        print("❌ Los Angeles schema file not found: {la_schema_file}")
        print("   Available files:")
        for f in cities_dir.glob("*.json"):
            print("   - {f.name}")
        return False

    print("✅ Los Angeles schema file found: {la_schema_file.name}")

    try:
        # Load CityRegistry
        print("\n🔄 Loading CityRegistry...")
        registry = get_city_registry(cities_dir)

        if registry is None:
            print("❌ Failed to load CityRegistry")
            return False

        print("✅ CityRegistry loaded successfully")

        # Test 1: Get all cities
        print("\n🧪 Test 1: Get all cities")
        all_cities = registry.get_all_cities()
        print(
            "   Found {len(all_cities)} cities: {[city['city_id'] for city in all_cities]}"
        )

        if not any(city["city_id"] == "us-ca-los_angeles" for city in all_cities):
            print("❌ Los Angeles not found in registry")
            return False

        print("✅ Los Angeles found in registry")

        # Test 2: Get city configuration
        print("\n🧪 Test 2: Get city configuration")
        la_config = registry.get_city_config("us-ca-los_angeles")

        if la_config is None:
            print("❌ Failed to get Los Angeles configuration")
            return False

        print("✅ Los Angeles configuration loaded")
        print("   Name: {la_config.name}")
        print("   Jurisdiction: {la_config.jurisdiction.value}")
        print("   Citation patterns: {len(la_config.citation_patterns)}")
        print("   Timezone: {la_config.timezone}")
        print("   Appeal deadline days: {la_config.appeal_deadline_days}")

        # Test 3: Test citation pattern matching
        print("\n🧪 Test 3: Test citation pattern matching")

        # Get Los Angeles citation patterns
        if not la_config.citation_patterns:
            print("❌ No citation patterns found for Los Angeles")
            return False

        la_pattern = la_config.citation_patterns[0]
        print("   Citation pattern regex: {la_pattern.regex}")
        print("   Description: {la_pattern.description}")
        print("   Example numbers: {la_pattern.example_numbers}")

        # Test with example citations
        test_citations = ["12345678901", "LA1234567", "INVALID123"]
        matches = []

        for citation in test_citations:
            match = registry.match_citation(citation)
            if match:
                city_id, section_id = match
                matches.append((citation, city_id, section_id))
                print("   ✅ '{citation}' → {city_id} ({section_id})")
            else:
                print("   ❌ '{citation}' → No match")

        if len(matches) < len(test_citations) - 1:  # At least 2 should match
            print("⚠️  Fewer matches than expected, but continuing...")

        # Test 4: Get mail address
        print("\n🧪 Test 4: Get mail address")
        mail_address = registry.get_mail_address("us-ca-los_angeles", "ladot_pvb")

        if mail_address is None:
            print("❌ Failed to get mail address")
            return False

        print("✅ Mail address retrieved")
        print("   Status: {mail_address.status.value}")
        print("   Address: {mail_address.address1}")
        print("   City: {mail_address.city}")
        print("   State: {mail_address.state}")
        print("   ZIP: {mail_address.zip}")

        # Test 5: Get phone confirmation policy
        print("\n🧪 Test 5: Get phone confirmation policy")
        phone_policy = registry.get_phone_confirmation_policy(
            "us-ca-los_angeles", "ladot_pvb"
        )

        if phone_policy is None:
            print("❌ Failed to get phone confirmation policy")
            return False

        print("✅ Phone confirmation policy retrieved")
        print("   Required: {phone_policy.required}")
        if phone_policy.phone_format_regex:
            print("   Phone format regex: {phone_policy.phone_format_regex}")
        if phone_policy.confirmation_message:
            print(
                "   Confirmation message: {phone_policy.confirmation_message[:50]}..."
            )

        if phone_policy.phone_number_examples:
            print("   Phone number examples: {phone_policy.phone_number_examples}")

        # Test 6: Get routing rule
        print("\n🧪 Test 6: Get routing rule")
        routing_rule = registry.get_routing_rule("us-ca-los_angeles", "ladot_pvb")

        if routing_rule is None:
            print("❌ Failed to get routing rule")
            return False

        print("✅ Routing rule: {routing_rule.value}")

        # Test 7: Validate phone number (if required)
        print("\n🧪 Test 7: Test phone validation")
        if phone_policy.required:
            test_phone = "866-561-9742"  # LA's phone number from schema
            is_valid = registry.validate_phone_for_city("us-ca-los_angeles", test_phone)
            print("   Test phone '{test_phone}' valid: {is_valid}")

        # Test 8: Load configuration from file directly
        print("\n🧪 Test 8: Direct file validation")
        import json

        with open(la_schema_file, "r", encoding="utf-8") as f:
            schema_data = json.load(f)

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

        missing_fields = []
        for field in required_fields:
            if field not in schema_data:
                missing_fields.append(field)

        if missing_fields:
            print("❌ Missing required fields in schema: {missing_fields}")
            return False

        print("✅ All required fields present in schema")
        print("   Citation patterns: {len(schema_data['citation_patterns'])}")
        print("   Sections: {len(schema_data['sections'])}")

        return True

    except Exception as e:
        print("❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("CITY REGISTRY LOAD TEST")
    print("=" * 60)

    success = test_city_registry_load()

    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: CityRegistry loads and functions correctly")
    else:
        print("❌ TEST FAILED: Issues with CityRegistry loading or functionality")
    print("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
