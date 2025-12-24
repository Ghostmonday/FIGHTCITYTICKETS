"""
Test script for Schema Adapter Service (Schema 4.3.0)

Tests transformation of rich/flexible JSON into strict Schema 4.3.0 format.
Validates field normalization, default value application, validation, and
file operations.

Usage:
    python test_schema_adapter.py
"""

import json
import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import schema_adapter
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.schema_adapter import (
    SchemaAdapter,
    TransformationResult,
    adapt_city_file,
    adapt_city_schema,
    batch_adapt_directory,
)


class TestSchemaAdapter:
    """Test suite for Schema Adapter Service."""

    def test_basic_schema_adaptation(self):
        """Test basic schema adaptation with minimal valid input."""
        input_data = {
            "city_id": "test_city",
            "name": "Test City",
            "jurisdiction": "city",
            "citation_patterns": [
                {"regex": "^TEST\\d{6}$", "section_id": "test_agency"}
            ],
            "appeal_mail_address": {
                "status": "complete",
                "address1": "123 Test St",
                "city": "Test City",
                "state": "CA",
                "zip": "12345",
                "country": "USA",
            },
            "phone_confirmation_policy": {"required": False},
            "routing_rule": "direct",
            "sections": {
                "test_agency": {
                    "name": "Test Agency",
                    "routing_rule": "direct",
                    "phone_confirmation_policy": {"required": False},
                }
            },
            "verification_metadata": {
                "last_updated": "2024-01-01",
                "source": "test",
                "confidence_score": 0.9,
                "notes": "Test data",
                "verified_by": "tester",
            },
        }

        adapter = SchemaAdapter(strict_mode=True)
        result = adapter.adapt_city_schema(input_data)

        assert result.success, f"Adaptation failed: {result.errors}"
        assert result.transformed_data["city_id"] == "test_city"
        assert result.transformed_data["name"] == "Test City"
        assert len(result.transformed_data["citation_patterns"]) == 1
        assert "appeal_mail_address" in result.transformed_data
        assert "verification_metadata" in result.transformed_data
        assert result.transformed_data["jurisdiction"] == "city"
        assert result.transformed_data["timezone"] == "America/Los_Angeles"
        assert result.transformed_data["appeal_deadline_days"] == 21
        # Allow warnings for optional fields with defaults (timezone, appeal_deadline_days, etc.)
        # But require no errors
        assert len(result.errors) == 0, f"Unexpected errors: {result.errors}"

    def test_field_normalization(self):
        """Test that legacy field names are normalized correctly."""
        input_data = {
            "city": "legacy_city",  # Should normalize to city_id
            "city_name": "Legacy City",  # Should normalize to name
            "patterns": [  # Should normalize to citation_patterns
                {"citation_regex": "^LEG\\d{6}$", "agency": "legacy_agency"}
            ],
            "agencies": {  # Should normalize to sections
                "legacy_agency": {
                    "name": "Legacy Agency",
                    "appeal_address": {"status": "complete", "street": "123 Main St"},
                }
            },
            "metadata": {  # Should normalize to verification_metadata
                "last_verified": "2024-01-01",
                "source": "legacy_source",
            },
        }

        adapter = SchemaAdapter(strict_mode=False)
        result = adapter.adapt_city_schema(input_data)

        assert result.success, f"Adaptation failed: {result.errors}"
        assert result.transformed_data["city_id"] == "legacy_city"
        assert result.transformed_data["name"] == "Legacy City"
        assert "citation_patterns" in result.transformed_data
        assert "sections" in result.transformed_data
        assert "verification_metadata" in result.transformed_data
        assert len(result.warnings) > 0, "Expected warnings for normalization"

    def test_missing_required_fields(self):
        """Test that missing required fields get defaults in non-strict mode."""
        input_data = {
            # Missing city_id, name, and most required fields
            "citation_patterns": [],
        }

        # Test non-strict mode (should fix issues)
        adapter = SchemaAdapter(strict_mode=False)
        result = adapter.adapt_city_schema(input_data)

        assert result.success, f"Adaptation failed in non-strict mode: {result.errors}"
        assert result.transformed_data["city_id"] == "unknown_city"
        assert result.transformed_data["name"] == "Unknown City"
        assert len(result.transformed_data["citation_patterns"]) > 0
        assert len(result.warnings) > 0, "Expected warnings for missing fields"

        # Test strict mode (should fail)
        adapter_strict = SchemaAdapter(strict_mode=True)
        result_strict = adapter_strict.adapt_city_schema(input_data)

        assert not result_strict.success, (
            "Should fail in strict mode with missing fields"
        )
        assert len(result_strict.errors) > 0, "Expected errors in strict mode"

    def test_invalid_regex_patterns(self):
        """Test handling of invalid regex patterns."""
        input_data = {
            "city_id": "test_city",
            "name": "Test City",
            "citation_patterns": [
                {
                    "regex": "[invalid(regex",
                    "section_id": "test_agency",
                }  # Invalid regex
            ],
            "sections": {
                "test_agency": {
                    "name": "Test Agency",
                    "routing_rule": "direct",
                    "phone_confirmation_policy": {"required": False},
                }
            },
        }

        # Test non-strict mode (should fix invalid regex)
        adapter = SchemaAdapter(strict_mode=False)
        result = adapter.adapt_city_schema(input_data)

        assert result.success, f"Adaptation failed: {result.errors}"
        assert len(result.warnings) > 0, "Expected warning for invalid regex"
        # Should have been replaced with default regex
        assert "^[A-Z0-9]{6,12}$" in [
            p["regex"] for p in result.transformed_data["citation_patterns"]
        ]

    def test_address_transformations(self):
        """Test various address transformation scenarios."""
        test_cases = [
            # String address
            ("123 Main St, Anytown, CA 12345", "complete"),
            # Complete dict address
            (
                {
                    "status": "complete",
                    "address1": "456 Oak Ave",
                    "city": "Somewhere",
                    "state": "CA",
                    "zip": "90210",
                    "country": "USA",
                },
                "complete",
            ),
            # Routes elsewhere
            (
                {"status": "routes_elsewhere", "routes_to_section_id": "other_agency"},
                "routes_elsewhere",
            ),
            # Missing address
            ({"status": "missing"}, "missing"),
        ]

        for address_input, expected_status in test_cases:
            input_data = {
                "city_id": "test_city",
                "name": "Test City",
                "appeal_mail_address": address_input,
                "citation_patterns": [
                    {"regex": "^TEST\\d{6}$", "section_id": "test_agency"}
                ],
                "sections": {
                    "test_agency": {
                        "name": "Test Agency",
                        "routing_rule": "direct",
                        "phone_confirmation_policy": {"required": False},
                    }
                },
            }

            adapter = SchemaAdapter(strict_mode=False)
            result = adapter.adapt_city_schema(input_data)

            assert result.success, (
                f"Address test failed for {address_input}: {result.errors}"
            )
            transformed_address = result.transformed_data["appeal_mail_address"]
            assert transformed_address["status"] == expected_status, (
                f"Expected status {expected_status}, got {transformed_address['status']}"
            )

    def test_phone_policy_transformations(self):
        """Test phone confirmation policy transformations."""
        test_cases = [
            # Boolean true
            (True, {"required": True}),
            # Boolean false
            (False, {"required": False}),
            # Full policy dict
            (
                {
                    "required": True,
                    "phone_format_regex": "^\\+1\\d{10}$",
                    "confirmation_message": "Call us!",
                    "confirmation_deadline_hours": 48,
                    "phone_number_examples": ["+15551234567"],
                },
                {"required": True},
            ),
        ]

        for policy_input, expected_policy in test_cases:
            input_data = {
                "city_id": "test_city",
                "name": "Test City",
                "phone_confirmation_policy": policy_input,
                "citation_patterns": [
                    {"regex": "^TEST\\d{6}$", "section_id": "test_agency"}
                ],
                "sections": {
                    "test_agency": {
                        "name": "Test Agency",
                        "routing_rule": "direct",
                    }
                },
            }

            adapter = SchemaAdapter(strict_mode=False)
            result = adapter.adapt_city_schema(input_data)

            assert result.success, f"Phone policy test failed: {result.errors}"
            transformed_policy = result.transformed_data["phone_confirmation_policy"]
            assert transformed_policy["required"] == expected_policy["required"], (
                f"Expected required={expected_policy['required']}, got {transformed_policy['required']}"
            )

    def test_section_transformations(self):
        """Test section dictionary transformations."""
        input_data = {
            "city_id": "test_city",
            "name": "Test City",
            "citation_patterns": [
                {"regex": "^TEST\\d{6}$", "section_id": "agency1"},
                {"regex": "^AG2\\d{6}$", "section_id": "agency2"},
            ],
            "sections": {
                "agency1": "First Agency",  # String section
                "agency2": {  # Dict section
                    "name": "Second Agency",
                    "appeal_mail_address": {
                        "status": "complete",
                        "address1": "789 Pine St",
                    },
                    "phone_confirmation_policy": True,
                },
            },
        }

        adapter = SchemaAdapter(strict_mode=False)
        result = adapter.adapt_city_schema(input_data)

        assert result.success, f"Section test failed: {result.errors}"
        sections = result.transformed_data["sections"]

        assert "agency1" in sections
        assert sections["agency1"]["name"] == "First Agency"
        assert sections["agency1"]["section_id"] == "agency1"
        assert sections["agency1"]["routing_rule"] == "direct"

        assert "agency2" in sections
        assert sections["agency2"]["name"] == "Second Agency"
        assert sections["agency2"]["appeal_mail_address"]["status"] == "complete"
        assert sections["agency2"]["phone_confirmation_policy"]["required"] == True

        assert len(result.warnings) > 0, "Expected warnings for section transformations"

    def test_file_adaptation(self):
        """Test adaptation of JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_city.json"
            output_file = Path(tmpdir) / "adapted_city.json"

            # Create test JSON file
            test_data = {
                "city_id": "file_city",
                "name": "File City",
                "citation_patterns": [
                    {"regex": "^FILE\\d{6}$", "section_id": "file_agency"}
                ],
                "sections": {
                    "file_agency": {
                        "name": "File Agency",
                        "routing_rule": "direct",
                        "phone_confirmation_policy": {"required": False},
                    }
                },
            }

            with open(input_file, "w", encoding="utf-8") as f:
                json.dump(test_data, f, indent=2)

            # Test file adaptation
            result = adapt_city_file(input_file, output_file)

            assert result.success, f"File adaptation failed: {result.errors}"
            assert output_file.exists(), "Output file was not created"

            # Verify output file content
            with open(output_file, "r", encoding="utf-8") as f:
                output_data = json.load(f)

            assert output_data["city_id"] == "file_city"
            assert output_data["name"] == "File City"
            assert "verification_metadata" in output_data
            assert output_data["verification_metadata"]["verified_by"] == "system"

    def test_batch_directory_adaptation(self):
        """Test batch adaptation of multiple JSON files in a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "output"
            input_dir.mkdir()

            # Create multiple test JSON files
            test_files = [
                ("city1.json", {"city_id": "city1", "name": "City One"}),
                ("city2.json", {"city_id": "city2", "name": "City Two"}),
                ("city3.json", {"city_id": "city3", "name": "City Three"}),
            ]

            for filename, data in test_files:
                file_path = input_dir / filename
                # Add minimal required structure
                full_data = {
                    **data,
                    "citation_patterns": [
                        {"regex": "^TEST\\d{6}$", "section_id": "default"}
                    ],
                    "sections": {
                        "default": {"name": "Default Agency", "routing_rule": "direct"}
                    },
                }
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(full_data, f, indent=2)

            # Test batch adaptation
            results = batch_adapt_directory(input_dir, output_dir)

            assert len(results) == 3, f"Expected 3 results, got {len(results)}"

            success_count = sum(1 for r in results.values() if r.success)
            assert success_count == 3, (
                f"Expected 3 successful adaptations, got {success_count}"
            )

            # Verify output files exist
            for filename, _ in test_files:
                output_file = output_dir / filename
                assert output_file.exists(), f"Output file {filename} was not created"

    def test_transformation_result_dict(self):
        """Test TransformationResult.to_dict() method."""
        result = TransformationResult(
            success=True,
            transformed_data={"test": "data"},
            warnings=["Warning 1", "Warning 2"],
            errors=[],
        )

        result_dict = result.to_dict()

        assert result_dict["success"] == True
        assert result_dict["has_warnings"] == True
        assert result_dict["has_errors"] == False
        assert len(result_dict["warnings"]) == 2
        assert len(result_dict["errors"]) == 0
        assert result_dict["data"] == {"test": "data"}

        # Test with errors
        result_with_errors = TransformationResult(
            success=False,
            transformed_data={},
            warnings=[],
            errors=["Error 1", "Error 2"],
        )

        error_dict = result_with_errors.to_dict()
        assert error_dict["success"] == False
        assert error_dict["has_errors"] == True
        assert error_dict["data"] is None

    def test_convenience_functions(self):
        """Test the convenience functions."""
        input_data = {
            "city_id": "conv_city",
            "name": "Convenience City",
            "citation_patterns": [
                {"regex": "^CONV\\d{6}$", "section_id": "conv_agency"}
            ],
            "sections": {
                "conv_agency": {
                    "name": "Convenience Agency",
                    "routing_rule": "direct",
                    "phone_confirmation_policy": {"required": False},
                }
            },
        }

        # Test adapt_city_schema convenience function
        result = adapt_city_schema(input_data, strict_mode=True)
        assert result.success, f"Convenience function failed: {result.errors}"
        assert result.transformed_data["city_id"] == "conv_city"

        # Test with non-strict mode
        result_non_strict = adapt_city_schema({}, strict_mode=False)
        assert result_non_strict.success, "Non-strict mode should fix missing fields"
        assert len(result_non_strict.warnings) > 0


def run_all_tests():
    """Run all tests and report results."""
    test_cases = [
        ("Basic Schema Adaptation", TestSchemaAdapter().test_basic_schema_adaptation),
        ("Field Normalization", TestSchemaAdapter().test_field_normalization),
        ("Missing Required Fields", TestSchemaAdapter().test_missing_required_fields),
        ("Invalid Regex Patterns", TestSchemaAdapter().test_invalid_regex_patterns),
        ("Address Transformations", TestSchemaAdapter().test_address_transformations),
        (
            "Phone Policy Transformations",
            TestSchemaAdapter().test_phone_policy_transformations,
        ),
        ("Section Transformations", TestSchemaAdapter().test_section_transformations),
        ("File Adaptation", TestSchemaAdapter().test_file_adaptation),
        (
            "Batch Directory Adaptation",
            TestSchemaAdapter().test_batch_directory_adaptation,
        ),
        (
            "Transformation Result Dict",
            TestSchemaAdapter().test_transformation_result_dict,
        ),
        ("Convenience Functions", TestSchemaAdapter().test_convenience_functions),
    ]

    print("\n" + "=" * 70)
    print("SCHEMA ADAPTER TEST SUITE")
    print("=" * 70)

    passed = 0
    failed = 0

    for test_name, test_func in test_cases:
        try:
            test_func()
            print(f"[OK] {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"[FAIL] {test_name} (Unexpected error)")
            print(f"   Error: {type(e).__name__}: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
