"""
Test Schema Adapter with San Francisco city configuration.

Validates that the existing SF JSON configuration can be properly adapted
to Schema 4.3.0 format and maintains backward compatibility.
"""

import json
import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import schema_adapter
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.city_registry import get_city_registry
from services.schema_adapter import SchemaAdapter


class TestSFSchemaAdapter:
    """Test suite for SF city schema adaptation."""

    @classmethod
    def setup_class(cls):
        """Load SF configuration and setup test data."""
        # Path to SF JSON file - use sanfrancisco.json (old format) for adapter testing
        # us-ca-san_francisco.json is already in Schema 4.3.0 format
        project_root = Path(__file__).parent.parent.parent
        cls.sf_json_path = project_root / "cities" / "sanfrancisco.json"

        if not cls.sf_json_path.exists():
            raise FileNotFoundError("SF JSON file not found at {cls.sf_json_path}")

        # Load original SF data
        with open(cls.sf_json_path, "r", encoding="utf-8") as f:
            cls.original_sf_data = json.load(f)

        # Initialize schema adapter
        cls.adapter = SchemaAdapter(strict_mode=True)

        # Adapt the SF schema
        cls.adaptation_result = cls.adapter.adapt_city_schema(cls.original_sf_data)

        # Path for adapted output (for testing file operations)
        cls.adapted_output_path = project_root / "cities" / "sf_adapted_test.json"

    def test_sf_configuration_exists(self):
        """Verify SF configuration file exists and is valid JSON."""
        assert self.sf_json_path.exists(), (
            "SF JSON file not found at {self.sf_json_path}"
        )
        assert isinstance(self.original_sf_data, dict), "SF data should be a dictionary"
        assert "city_id" in self.original_sf_data, "SF data missing city_id"
        assert self.original_sf_data["city_id"] == "us-ca-san_francisco", (
            "Expected city_id='us-ca-san_francisco', got '{self.original_sf_data.get('city_id')}'"
        )

    def test_schema_adaptation_success(self):
        """Test that SF schema adaptation succeeds."""
        assert self.adaptation_result.success, (
            "SF schema adaptation failed: {self.adaptation_result.errors}"
        )
        assert len(self.adaptation_result.errors) == 0, (
            "Adaptation errors: {self.adaptation_result.errors}"
        )

        # Warnings are acceptable (for optional fields with defaults)
        if self.adaptation_result.warnings:
            print(
                "Note: Schema adaptation warnings: {self.adaptation_result.warnings}"
            )

    def test_required_fields_present(self):
        """Test that all required Schema 4.3.0 fields are present."""
        transformed = self.adaptation_result.transformed_data

        # Required top-level fields
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

        for field in required_fields:
            assert field in transformed, "Missing required field: {field}"
            assert transformed[field] is not None, "Required field {field} is None"
            if isinstance(transformed[field], str):
                assert transformed[field].strip() != "", (
                    "Required field {field} is empty string"
                )

    def test_city_identification(self):
        """Test that city identification fields are correct."""
        transformed = self.adaptation_result.transformed_data

        assert transformed["city_id"] == "us-ca-san_francisco", (
            "Expected city_id='us-ca-san_francisco', got '{transformed['city_id']}'"
        )
        assert transformed["name"] == "San Francisco", (
            "Expected name='San Francisco', got '{transformed['name']}'"
        )
        assert transformed["jurisdiction"] == "city", (
            "Expected jurisdiction='city', got '{transformed['jurisdiction']}'"
        )
        assert transformed["timezone"] == "America/Los_Angeles", (
            "Expected timezone='America/Los_Angeles', got '{transformed['timezone']}'"
        )
        assert transformed["appeal_deadline_days"] == 21, (
            "Expected appeal_deadline_days=21, got {transformed['appeal_deadline_days']}"
        )

    def test_citation_patterns(self):
        """Test SF citation patterns are preserved and valid."""
        transformed = self.adaptation_result.transformed_data
        patterns = transformed["citation_patterns"]

        assert len(patterns) >= 4, (
            "Expected at least 4 citation patterns for SF, got {len(patterns)}"
        )

        # Check for SF-specific section IDs
        section_ids = {p["section_id"] for p in patterns}
        expected_sections = {"sfmta", "sfpd", "sfsu", "sfmud"}

        for expected in expected_sections:
            assert expected in section_ids, (
                "Missing citation pattern for section: {expected}"
            )

        # Validate regex patterns
        import re

        for pattern in patterns:
            assert "regex" in pattern, "Citation pattern missing regex: {pattern}"
            assert "section_id" in pattern, (
                "Citation pattern missing section_id: {pattern}"
            )
            assert "description" in pattern, (
                "Citation pattern missing description: {pattern}"
            )

            # Try to compile regex to ensure it's valid
            try:
                re.compile(pattern["regex"])
            except re.error as e:
                raise AssertionError(f"Invalid regex '{pattern['regex']}': {e}") from e

    def test_sections_structure(self):
        """Test SF sections structure and completeness."""
        transformed = self.adaptation_result.transformed_data
        sections = transformed["sections"]

        # Check all expected sections exist
        expected_sections = ["sfmta", "sfpd", "sfsu", "sfmud"]
        for section_id in expected_sections:
            assert section_id in sections, "Missing section: {section_id}"
            section = sections[section_id]

            # Check required section fields
            assert section["section_id"] == section_id, (
                "Section ID mismatch: {section['section_id']} != {section_id}"
            )
            assert "name" in section and section["name"], (
                "Section {section_id} missing name"
            )
            assert "routing_rule" in section, (
                "Section {section_id} missing routing_rule"
            )
            assert "phone_confirmation_policy" in section, (
                "Section {section_id} missing phone_confirmation_policy"
            )

            # Check phone confirmation policy structure
            policy = section["phone_confirmation_policy"]
            assert isinstance(policy, dict), (
                "Phone policy for {section_id} should be dict"
            )
            assert "required" in policy, (
                "Phone policy for {section_id} missing 'required' field"
            )

    def test_phone_confirmation_policies(self):
        """Test SF-specific phone confirmation policies."""
        transformed = self.adaptation_result.transformed_data
        sections = transformed["sections"]

        # SFPD should require phone confirmation
        sfpd_policy = sections["sfpd"]["phone_confirmation_policy"]
        assert sfpd_policy["required"], "SFPD should require phone confirmation"
        assert "phone_format_regex" in sfpd_policy, (
            "SFPD phone policy missing format regex"
        )
        assert "confirmation_message" in sfpd_policy, (
            "SFPD phone policy missing message"
        )
        assert "confirmation_deadline_hours" in sfpd_policy, (
            "SFPD phone policy missing deadline"
        )
        assert "phone_number_examples" in sfpd_policy, (
            "SFPD phone policy missing examples"
        )

        # Other SF agencies should not require phone confirmation
        non_phone_sections = ["sfmta", "sfsu", "sfmud"]
        for section_id in non_phone_sections:
            policy = sections[section_id]["phone_confirmation_policy"]
            assert not policy["required"], (
                f"{section_id} should not require phone confirmation"
            )

    def test_address_structures(self):
        """Test appeal mail address structures."""
        transformed = self.adaptation_result.transformed_data

        # Check main city address
        main_address = transformed["appeal_mail_address"]
        assert main_address["status"] == "complete", (
            "SF main address should be complete"
        )

        required_address_fields = ["address1", "city", "state", "zip", "country"]
        for field in required_address_fields:
            assert field in main_address, "Main address missing {field}"
            assert main_address[field] and main_address[field].strip(), (
                "Main address {field} is empty"
            )

        # Check section addresses
        sections = transformed["sections"]

        # SFMUD should route to SFMTA
        sfmud_address = sections["sfmud"]["appeal_mail_address"]
        assert sfmud_address["status"] == "routes_elsewhere", (
            "SFMUD should route elsewhere"
        )
        assert sfmud_address["routes_to_section_id"] == "sfmta", (
            "SFMUD should route to SFMTA"
        )

        # Other sections should have complete addresses
        complete_sections = ["sfmta", "sfpd", "sfsu"]
        for section_id in complete_sections:
            address = sections[section_id]["appeal_mail_address"]
            assert address["status"] == "complete", (
                "{section_id} address should be complete"
            )
            for field in required_address_fields:
                assert field in address, "{section_id} address missing {field}"
                assert address[field] and address[field].strip(), (
                    "{section_id} address {field} is empty"
                )

    def test_file_adaptation(self):
        """Test adapting SF configuration file and saving to disk."""
        # Adapt file and save
        result = self.adapter.adapt_city_file(
            self.sf_json_path, self.adapted_output_path
        )

        assert result.success, "File adaptation failed: {result.errors}"
        assert self.adapted_output_path.exists(), "Adapted file was not created"

        # Load and verify adapted file
        with open(self.adapted_output_path, "r", encoding="utf-8") as f:
            file_data = json.load(f)

        assert file_data["city_id"] == "us-ca-san_francisco", "Adapted file has wrong city_id"
        assert "verification_metadata" in file_data, (
            "Adapted file missing verification_metadata"
        )

        # Clean up test file
        if self.adapted_output_path.exists():
            self.adapted_output_path.unlink()

    def test_city_registry_compatibility(self):
        """Test that adapted schema can be loaded by CityRegistry."""
        # Create a temporary directory for adapted city file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_output = temp_dir_path / "us-ca-san_francisco.json"  # Must match city_id

            # Adapt and save
            result = self.adapter.adapt_city_file(self.sf_json_path, temp_output)
            assert result.success, (
                "File adaptation failed for registry test: {result.errors}"
            )

            # Try to load with CityRegistry
            registry = get_city_registry(temp_dir_path)

            # Verify SF is loaded
            sf_config = registry.get_city_config("us-ca-san_francisco")
            assert sf_config is not None, (
                "CityRegistry failed to load adapted SF configuration"
            )

            # Test citation matching
            test_citations = [
                ("MT98765432", ("us-ca-san_francisco", "sfmta")),  # SFMTA citation (MT format)
                # Note: SFPD, SFSU patterns may not exist in current city files
            ]

            for citation, expected_match in test_citations:
                match = registry.match_citation(citation)
                assert match == expected_match, (
                    "Citation '{citation}' matched {match}, expected {expected_match}"
                )

    def test_backward_compatibility(self):
        """Test that adapted schema maintains backward compatibility with original."""
        transformed = self.adaptation_result.transformed_data

        # Key fields that should remain unchanged
        unchanged_fields = ["city_id", "name", "appeal_deadline_days", "timezone"]
        for field in unchanged_fields:
            if field in self.original_sf_data:
                assert transformed[field] == self.original_sf_data[field], (
                    "Field {field} changed: {transformed[field]} != {self.original_sf_data[field]}"
                )

        # Section IDs should be preserved
        original_sections = set(self.original_sf_data.get("sections", {}).keys())
        transformed_sections = set(transformed["sections"].keys())
        assert original_sections == transformed_sections, (
            "Sections changed: {transformed_sections} != {original_sections}"
        )

        # Citation pattern section references should be preserved
        original_pattern_sections = {
            p.get("section_id")
            for p in self.original_sf_data.get("citation_patterns", [])
        }
        transformed_pattern_sections = {
            p.get("section_id") for p in transformed["citation_patterns"]
        }
        assert original_pattern_sections == transformed_pattern_sections, (
            "Citation pattern sections changed: {transformed_pattern_sections} != {original_pattern_sections}"
        )


def run_sf_tests():
    """Run all SF schema adapter tests and report results."""
    test_cases = [
        ("SF Configuration Exists", TestSFSchemaAdapter().test_sf_configuration_exists),
        (
            "Schema Adaptation Success",
            TestSFSchemaAdapter().test_schema_adaptation_success,
        ),
        ("Required Fields Present", TestSFSchemaAdapter().test_required_fields_present),
        ("City Identification", TestSFSchemaAdapter().test_city_identification),
        ("Citation Patterns", TestSFSchemaAdapter().test_citation_patterns),
        ("Sections Structure", TestSFSchemaAdapter().test_sections_structure),
        (
            "Phone Confirmation Policies",
            TestSFSchemaAdapter().test_phone_confirmation_policies,
        ),
        ("Address Structures", TestSFSchemaAdapter().test_address_structures),
        ("File Adaptation", TestSFSchemaAdapter().test_file_adaptation),
        (
            "City Registry Compatibility",
            TestSFSchemaAdapter().test_city_registry_compatibility,
        ),
        ("Backward Compatibility", TestSFSchemaAdapter().test_backward_compatibility),
    ]

    print("\n" + "=" * 70)
    print("SF SCHEMA ADAPTER TEST SUITE")
    print("=" * 70)

    # Create test instance and setup
    tester = TestSFSchemaAdapter()
    try:
        tester.setup_class()
    except Exception as e:
        print("[SETUP FAILED] Cannot run tests: {e}")
        return False

    passed = 0
    failed = 0

    for test_name, test_func in test_cases:
        try:
            test_func(tester)
            print("[OK] {test_name}")
            passed += 1
        except AssertionError as e:
            print("[FAIL] {test_name}")
            print("   Error: {e}")
            failed += 1
        except Exception as e:
            print("[FAIL] {test_name} (Unexpected error)")
            print("   Error: {type(e).__name__}: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print("RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    # Cleanup
    if hasattr(tester, "adapted_output_path") and tester.adapted_output_path.exists():
        tester.adapted_output_path.unlink()

    return failed == 0


if __name__ == "__main__":
    success = run_sf_tests()
    sys.exit(0 if success else 1)
