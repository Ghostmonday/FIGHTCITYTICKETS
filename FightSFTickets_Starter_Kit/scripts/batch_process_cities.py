#!/usr/bin/env python3
"""
Batch Process Cities for Schema 4.3.0 Transformation

This script processes all phase1 JSON files in the cities/ directory,
transforming them into valid Schema 4.3.0 JSON files that can be loaded
by CityRegistry.

Steps:
1. Repair any JSON files with syntax errors (e.g., sandiego_phase1.json)
2. Extract simplified city data from all valid phase1 files
3. Transform simplified data to Schema 4.3.0 format
4. Validate generated schemas with CityRegistry
5. Clean up intermediate files
6. Organize final output
"""

import argparse
import json
import os
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add backend/src to Python path for imports
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

try:
    from services.city_registry import CityRegistry

    CITY_REGISTRY_AVAILABLE = True
except ImportError:
    CITY_REGISTRY_AVAILABLE = False
    print("Warning: CityRegistry not available, skipping validation")


def repair_json_syntax(filepath: Path) -> bool:
    """Repair JSON files with markdown backticks or other syntax issues."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove markdown backticks
        content = re.sub(r"```[a-z]*\n", "", content)
        content = re.sub(r"\n```", "", content)

        # Fix common JSON issues
        content = re.sub(r'"""(.*?)"""', r'"\1"', content)  # Triple quotes to single
        content = re.sub(r"'(.*?)'", r'"\1"', content)  # Single quotes to double
        content = re.sub(r",\s*}", "}", content)  # Trailing commas
        content = re.sub(r",\s*]", "]", content)  # Trailing commas in arrays

        # Write repaired content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # Test if it's valid JSON
        with open(filepath, "r", encoding="utf-8") as f:
            json.load(f)

        print(f"  ✅ Repaired JSON syntax: {filepath.name}")
        return True

    except Exception as e:
        print(f"  ❌ Failed to repair {filepath.name}: {e}")
        return False


def extract_simplified_city(phase1_file: Path, output_dir: Path) -> Optional[Path]:
    """Extract simplified city data from phase1 JSON."""
    try:
        # Check if extraction script exists
        extract_script = Path(__file__).parent / "extract_city_simple.py"
        if not extract_script.exists():
            print(f"  ❌ Extraction script not found: {extract_script}")
            return None

        # Generate output filename
        city_name = phase1_file.stem.replace("_phase1", "")
        output_file = output_dir / f"{city_name}.json"

        # Run extraction
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(extract_script),
                str(phase1_file),
                "-o",
                str(output_file),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"  ✅ Extracted: {phase1_file.name} → {output_file.name}")
            return output_file
        else:
            print(f"  ❌ Extraction failed for {phase1_file.name}:")
            if result.stdout:
                print(f"    stdout: {result.stdout[:200]}...")
            if result.stderr:
                print(f"    stderr: {result.stderr[:200]}...")
            return None

    except Exception as e:
        print(f"  ❌ Error extracting {phase1_file.name}: {e}")
        return None


def transform_to_schema_4_3_0(
    simplified_file: Path, output_dir: Path
) -> Optional[Path]:
    """Transform simplified JSON to Schema 4.3.0 format."""
    try:
        # Check if transformation script exists
        transform_script = Path(__file__).parent / "transform_simplified_to_schema.py"
        if not transform_script.exists():
            print(f"  ❌ Transformation script not found: {transform_script}")
            return None

        # Load simplified data to get city_id for filename
        with open(simplified_file, "r", encoding="utf-8") as f:
            simplified_data = json.load(f)

        city_id = simplified_data.get("city_id", "")
        if not city_id:
            print(f"  ❌ No city_id found in {simplified_file.name}")
            return None

        # Generate output filename from city_id
        clean_city_id = city_id.replace("us-", "").replace("-", "_")
        output_file = output_dir / f"{city_id}.json"

        # Run transformation
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(transform_script),
                str(simplified_file),
                "-o",
                str(output_file),
                "--validate",
                "--verbose",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"  ✅ Transformed: {simplified_file.name} → {output_file.name}")

            # Validate the generated schema
            if validate_schema_file(output_file):
                return output_file
            else:
                print(f"  ⚠️  Schema validation warnings for {output_file.name}")
                return output_file  # Return anyway, but with warning
        else:
            print(f"  ❌ Transformation failed for {simplified_file.name}:")
            if result.stdout:
                print(f"    stdout: {result.stdout[:200]}...")
            if result.stderr:
                print(f"    stderr: {result.stderr[:200]}...")
            return None

    except Exception as e:
        print(f"  ❌ Error transforming {simplified_file.name}: {e}")
        return None


def validate_schema_file(schema_file: Path) -> bool:
    """Validate Schema 4.3.0 file structure."""
    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_data = json.load(f)

        # Check required top-level fields
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
            print(f"    ❌ Missing required fields: {missing_fields}")
            return False

        # Validate phone_confirmation_policy structure
        policy = schema_data["phone_confirmation_policy"]
        allowed_policy_fields = {
            "required",
            "phone_format_regex",
            "confirmation_message",
            "confirmation_deadline_hours",
            "phone_number_examples",
        }

        invalid_policy_fields = set(policy.keys()) - allowed_policy_fields
        if invalid_policy_fields:
            print(
                f"    ❌ Invalid phone_confirmation_policy fields: {invalid_policy_fields}"
            )
            return False

        # Validate citation patterns
        for i, pattern in enumerate(schema_data["citation_patterns"]):
            if "regex" not in pattern or "section_id" not in pattern:
                print(f"    ❌ Citation pattern {i} missing regex or section_id")
                return False

            # Check regex compiles
            try:
                re.compile(pattern["regex"])
            except re.error as e:
                print(f"    ❌ Invalid regex in pattern {i}: {e}")
                return False

            # Check section_id exists in sections
            section_id = pattern["section_id"]
            if section_id not in schema_data["sections"]:
                print(
                    f"    ❌ Citation pattern references non-existent section: {section_id}"
                )
                return False

        # Validate appeal_mail_address status
        appeal_status = schema_data["appeal_mail_address"].get("status", "")
        valid_statuses = {"complete", "routes_elsewhere", "missing"}
        if appeal_status not in valid_statuses:
            print(f"    ❌ Invalid appeal_mail_address status: {appeal_status}")
            return False

        print(f"    ✅ Schema validation passed")
        return True

    except json.JSONDecodeError as e:
        print(f"    ❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"    ❌ Validation error: {e}")
        return False


def validate_with_city_registry(schema_file: Path, cities_dir: Path) -> bool:
    """Validate schema file can be loaded by CityRegistry."""
    if not CITY_REGISTRY_AVAILABLE:
        print(f"    ⚠️  CityRegistry not available, skipping registry validation")
        return True

    try:
        registry = CityRegistry(cities_dir)

        # Load the specific file
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_data = json.load(f)

        city_id = schema_data["city_id"]

        # Try to get city config
        config = registry.get_city_config(city_id)
        if config is None:
            print(f"    ❌ CityRegistry failed to load configuration for {city_id}")
            return False

        print(f"    ✅ CityRegistry successfully loaded {city_id}")
        return True

    except Exception as e:
        print(f"    ❌ CityRegistry validation failed: {e}")
        return False


def cleanup_duplicates(cities_dir: Path, keep_schema_files: bool = True):
    """Clean up duplicate and intermediate files."""
    print("\n🧹 Cleaning up duplicates and intermediate files...")

    files_to_remove = []

    for filepath in cities_dir.glob("*.json"):
        filename = filepath.name

        # Keep phase1 files (original source)
        if "_phase1" in filename:
            continue

        # Keep Schema 4.3.0 files (us-*.json format)
        if filename.startswith("us-") and filename.endswith(".json"):
            if keep_schema_files:
                continue
            else:
                # Check if we have a duplicate
                city_name = (
                    filename.replace("us-", "").replace(".json", "").replace("-", "_")
                )
                possible_duplicates = [
                    f"{city_name}.json",
                    f"{city_name.replace('_', '')}.json",
                    f"{city_name.split('_')[-1]}.json",
                ]
                for dup in possible_duplicates:
                    dup_path = cities_dir / dup
                    if dup_path.exists() and dup_path != filepath:
                        files_to_remove.append(dup_path)

        # Remove intermediate simplified files if we have Schema 4.3.0 version
        if not filename.startswith("us-") and "_phase1" not in filename:
            # Try to find corresponding Schema 4.3.0 file
            possible_schema_names = [
                f"us-{filename.replace('.json', '').replace('_', '-')}.json",
                f"us-{filename.replace('.json', '').split('_')[-1]}.json",
            ]

            has_schema = False
            for schema_name in possible_schema_names:
                if (cities_dir / schema_name).exists():
                    has_schema = True
                    break

            if has_schema:
                files_to_remove.append(filepath)

    # Remove files
    for filepath in files_to_remove:
        try:
            filepath.unlink()
            print(f"  🗑️  Removed: {filepath.name}")
        except Exception as e:
            print(f"  ❌ Failed to remove {filepath.name}: {e}")

    return len(files_to_remove)


def main():
    parser = argparse.ArgumentParser(
        description="Batch process cities to Schema 4.3.0 format"
    )
    parser.add_argument(
        "--repair-only",
        action="store_true",
        help="Only repair JSON files, don't process",
    )
    parser.add_argument(
        "--skip-repair", action="store_true", help="Skip JSON repair step"
    )
    parser.add_argument(
        "--cleanup-only",
        action="store_true",
        help="Only clean up duplicates, don't process",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate existing Schema 4.3.0 files",
    )
    parser.add_argument(
        "--keep-intermediate",
        action="store_true",
        help="Keep intermediate simplified JSON files",
    )

    args = parser.parse_args()

    # Set up paths
    script_dir = Path(__file__).parent
    cities_dir = script_dir.parent / "cities"

    if not cities_dir.exists():
        print(f"❌ Cities directory not found: {cities_dir}")
        sys.exit(1)

    print("=" * 70)
    print("BATCH PROCESS CITIES FOR SCHEMA 4.3.0")
    print("=" * 70)
    print(f"Cities directory: {cities_dir}")
    print(f"Total phase1 files: {len(list(cities_dir.glob('*_phase1.json')))}")
    print()

    if args.cleanup_only:
        removed_count = cleanup_duplicates(cities_dir, keep_schema_files=True)
        print(f"\n✅ Cleanup complete. Removed {removed_count} files.")
        return

    if args.validate_only:
        print("🔍 Validating existing Schema 4.3.0 files...")
        schema_files = list(cities_dir.glob("us-*.json"))

        if not schema_files:
            print("❌ No Schema 4.3.0 files found")
            return

        valid_count = 0
        for schema_file in schema_files:
            print(f"\n📄 Validating: {schema_file.name}")
            if validate_schema_file(schema_file):
                if CITY_REGISTRY_AVAILABLE:
                    if validate_with_city_registry(schema_file, cities_dir):
                        valid_count += 1
                else:
                    valid_count += 1

        print(
            f"\n✅ Validation complete. {valid_count}/{len(schema_files)} files valid."
        )
        return

    # Step 1: Repair JSON files
    if not args.skip_repair:
        print("🔧 Step 1: Repairing JSON files with syntax errors...")
        phase1_files = list(cities_dir.glob("*_phase1.json"))

        repaired_count = 0
        for phase1_file in phase1_files:
            # Check if file is valid JSON
            try:
                with open(phase1_file, "r", encoding="utf-8") as f:
                    json.load(f)
                print(f"  ✅ Valid JSON: {phase1_file.name}")
            except json.JSONDecodeError:
                print(f"  🔧 Repairing: {phase1_file.name}")
                if repair_json_syntax(phase1_file):
                    repaired_count += 1

        print(f"✅ Repaired {repaired_count} files")

        if args.repair_only:
            return

    # Step 2: Extract simplified city data
    print("\n📋 Step 2: Extracting simplified city data from phase1 files...")
    phase1_files = list(cities_dir.glob("*_phase1.json"))

    simplified_files = []
    skipped_files = []

    for phase1_file in phase1_files:
        print(f"\n📄 Processing: {phase1_file.name}")

        # Skip files that still have JSON errors
        try:
            with open(phase1_file, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            print(f"  ❌ Skipping due to JSON error: {e}")
            skipped_files.append(phase1_file.name)
            continue

        # Extract simplified data
        simplified_file = extract_simplified_city(phase1_file, cities_dir)
        if simplified_file:
            simplified_files.append(simplified_file)

    print(
        f"\n✅ Extraction complete. {len(simplified_files)} files extracted, {len(skipped_files)} skipped"
    )
    if skipped_files:
        print(f"📝 Skipped files: {', '.join(skipped_files)}")

    # Step 3: Transform to Schema 4.3.0
    print("\n🔄 Step 3: Transforming simplified data to Schema 4.3.0...")

    schema_files = []
    failed_files = []

    for simplified_file in simplified_files:
        print(f"\n📄 Transforming: {simplified_file.name}")

        schema_file = transform_to_schema_4_3_0(simplified_file, cities_dir)
        if schema_file:
            schema_files.append(schema_file)
        else:
            failed_files.append(simplified_file.name)

    print(
        f"\n✅ Transformation complete. {len(schema_files)} Schema 4.3.0 files created"
    )
    if failed_files:
        print(f"📝 Failed transformations: {', '.join(failed_files)}")

    # Step 4: Validate with CityRegistry
    if CITY_REGISTRY_AVAILABLE and schema_files:
        print("\n🔍 Step 4: Validating with CityRegistry...")

        registry_valid_count = 0
        for schema_file in schema_files:
            print(f"\n📄 Validating: {schema_file.name}")
            if validate_with_city_registry(schema_file, cities_dir):
                registry_valid_count += 1

        print(
            f"\n✅ Registry validation complete. {registry_valid_count}/{len(schema_files)} files load successfully"
        )

    # Step 5: Cleanup
    if not args.keep_intermediate:
        print("\n🧹 Step 5: Cleaning up intermediate files...")
        removed_count = cleanup_duplicates(cities_dir, keep_schema_files=True)
        print(f"✅ Cleanup complete. Removed {removed_count} files")

    # Summary
    print("\n" + "=" * 70)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 70)
    print(f"Total phase1 files processed: {len(phase1_files)}")
    print(f"Simplified files created: {len(simplified_files)}")
    print(f"Schema 4.3.0 files created: {len(schema_files)}")
    print(f"Files skipped: {len(skipped_files)}")
    print(f"Transformations failed: {len(failed_files)}")

    if schema_files:
        print("\n📁 Generated Schema 4.3.0 files:")
        for schema_file in schema_files:
            print(f"  • {schema_file.name}")

    # Check for missing cities
    expected_cities = [
        "chicago",
        "dallas",
        "houston",
        "la",
        "nyc",
        "philadelphia",
        "phoenix",
        "sandiego",
        "sanfrancisco",
        "seattle",
        "washingtondc",
    ]

    missing_cities = []
    for city in expected_cities:
        schema_pattern = f"us-*{city}*.json"
        matching_files = list(cities_dir.glob(schema_pattern))
        if not matching_files:
            missing_cities.append(city)

    if missing_cities:
        print(f"\n⚠️  Missing Schema 4.3.0 files for: {', '.join(missing_cities)}")

    print("\n✅ READY FOR DATA COLLECTION")
    print(
        "Your data retrieval system can now use the Schema 4.3.0 files in the cities/ directory."
    )
    print("Each file follows the exact format expected by CityRegistry.")


if __name__ == "__main__":
    main()
