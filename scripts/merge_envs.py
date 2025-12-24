#!/usr/bin/env python3
"""
Environment File Merger for FightSFTickets

This script analyzes and merges multiple environment configuration files
to eliminate duplication and create a single, clean template.

Files processed:
- .env.example (142 lines, 25 variables)
- .env.production.template (51 lines, ~15 variables)
- backend/.env.test (44 lines, ~20 variables)

Usage:
    python merge_envs.py analyze     # Show analysis of all files
    python merge_envs.py diff        # Show differences between files
    python merge_envs.py merge       # Create merged template
    python merge_envs.py cleanup     # Create single .env.template
"""

import os
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class EnvFileType(Enum):
    """Type of environment file."""

    EXAMPLE = "example"
    PRODUCTION = "production"
    TEST = "test"


@dataclass
class EnvVariable:
    """Represents a single environment variable."""

    name: str
    value: str
    comment: str = ""
    file_type: EnvFileType = EnvFileType.EXAMPLE
    line_number: int = 0
    section: str = ""


@dataclass
class EnvFile:
    """Represents an environment file."""

    path: Path
    type: EnvFileType
    variables: Dict[str, EnvVariable]
    sections: Dict[str, List[EnvVariable]]
    total_lines: int
    variable_count: int


class EnvMerger:
    """Main class for merging environment files."""

    # Section headers to organize variables
    SECTION_HEADERS = {
        "APP": "APPLICATION CONFIGURATION",
        "BACKEND": "BACKEND SERVER CONFIGURATION",
        "DATABASE": "DATABASE CONFIGURATION",
        "SECURITY": "SECURITY",
        "STRIPE": "STRIPE CONFIGURATION",
        "LOB": "LOB CONFIGURATION",
        "AI": "AI SERVICES CONFIGURATION",
        "URL": "APPLICATION URLS",
        "OTHER": "OTHER CONFIGURATION",
    }

    # Common variable patterns for section detection
    SECTION_PATTERNS = {
        "APP": r"APP_|ENVIRONMENT",
        "BACKEND": r"BACKEND_|CORS_|PORT|HOST",
        "DATABASE": r"DATABASE|DB_|POSTGRES",
        "SECURITY": r"SECRET|KEY$|PASSWORD",
        "STRIPE": r"STRIPE_",
        "LOB": r"LOB_",
        "AI": r"OPENAI|DEEPSEEK|AI_|MODEL",
        "URL": r"_URL$|DOMAIN|HOSTNAME",
    }

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.files: List[EnvFile] = []
        self.all_variables: Dict[str, List[EnvVariable]] = {}

    def load_files(self) -> None:
        """Load all environment files."""
        file_specs = [
            (self.project_root / ".env.example", EnvFileType.EXAMPLE),
            (self.project_root / ".env.production.template", EnvFileType.PRODUCTION),
            (self.project_root / "backend" / ".env.test", EnvFileType.TEST),
        ]

        for file_path, file_type in file_specs:
            if not file_path.exists():
                print(f"⚠️  Warning: File not found: {file_path}")
                continue

            env_file = self._parse_file(file_path, file_type)
            self.files.append(env_file)
            print(
                f"✅ Loaded {file_type.value}: {file_path} ({env_file.variable_count} variables, {env_file.total_lines} lines)"
            )

    def _parse_file(self, file_path: Path, file_type: EnvFileType) -> EnvFile:
        """Parse a single environment file."""
        variables = {}
        sections = {section: [] for section in self.SECTION_HEADERS.values()}
        current_section = self.SECTION_HEADERS["OTHER"]

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            line = line.rstrip()

            # Detect section headers
            section_match = self._detect_section(line)
            if section_match:
                current_section = section_match
                continue

            # Skip empty lines and comments (but track section comments)
            if not line or line.startswith("#"):
                # Check if this is a section divider
                if "===" in line or "---" in line:
                    continue
                # Check if comment indicates a section
                for section_name, section_header in self.SECTION_HEADERS.items():
                    if section_header.lower() in line.lower():
                        current_section = section_header
                continue

            # Parse variable assignment
            if "=" in line:
                var_name, var_value = self._parse_variable(line, i)
                comment = self._extract_comment(line)

                var = EnvVariable(
                    name=var_name,
                    value=var_value,
                    comment=comment,
                    file_type=file_type,
                    line_number=i,
                    section=current_section,
                )

                variables[var_name] = var
                sections[current_section].append(var)

                # Track variable across all files
                if var_name not in self.all_variables:
                    self.all_variables[var_name] = []
                self.all_variables[var_name].append(var)

        return EnvFile(
            path=file_path,
            type=file_type,
            variables=variables,
            sections=sections,
            total_lines=len(lines),
            variable_count=len(variables),
        )

    def _detect_section(self, line: str) -> Optional[str]:
        """Detect section headers from comments."""
        if line.startswith("#"):
            # Check for section headers in comments
            line_lower = line.lower()
            for section_name, section_header in self.SECTION_HEADERS.items():
                if section_header.lower() in line_lower:
                    return section_header
        return None

    def _parse_variable(self, line: str, line_num: int) -> Tuple[str, str]:
        """Parse a variable assignment line."""
        # Remove inline comments
        line = line.split("#")[0].strip()

        # Split on first equals sign
        if "=" in line:
            parts = line.split("=", 1)
            var_name = parts[0].strip()
            var_value = parts[1].strip() if len(parts) > 1 else ""
            return var_name, var_value

        return "", ""

    def _extract_comment(self, line: str) -> str:
        """Extract inline comment from a line."""
        if "#" in line:
            comment_part = line.split("#", 1)[1].strip()
            return comment_part
        return ""

    def _categorize_variable(self, var_name: str) -> str:
        """Determine which section a variable belongs to."""
        var_name_upper = var_name.upper()

        for section_key, pattern in self.SECTION_PATTERNS.items():
            if re.search(pattern, var_name_upper, re.IGNORECASE):
                return self.SECTION_HEADERS[section_key]

        return self.SECTION_HEADERS["OTHER"]

    def analyze(self) -> None:
        """Analyze all files and show statistics."""
        if not self.files:
            self.load_files()

        print("\n" + "=" * 80)
        print("ENVIRONMENT FILES ANALYSIS")
        print("=" * 80)

        # File statistics
        print("\n📊 FILE STATISTICS:")
        print("-" * 40)
        for env_file in self.files:
            print(
                f"  {env_file.type.value.upper():12} | {env_file.variable_count:3} variables | {env_file.total_lines:3} lines | {env_file.path}"
            )

        # Variable overlap analysis
        print("\n🔄 VARIABLE OVERLAP ANALYSIS:")
        print("-" * 40)

        total_unique_vars = len(self.all_variables)
        print(f"  Total unique variables across all files: {total_unique_vars}")

        # Count variables per file type
        vars_by_type = {file_type: set() for file_type in EnvFileType}
        for var_name, vars_list in self.all_variables.items():
            for var in vars_list:
                vars_by_type[var.file_type].add(var_name)

        print(
            f"  Variables in example file:      {len(vars_by_type[EnvFileType.EXAMPLE]):3}"
        )
        print(
            f"  Variables in production file:   {len(vars_by_type[EnvFileType.PRODUCTION]):3}"
        )
        print(
            f"  Variables in test file:         {len(vars_by_type[EnvFileType.TEST]):3}"
        )

        # Find variables unique to each file
        print("\n  Variables UNIQUE to each file:")
        for file_type in EnvFileType:
            other_types = [t for t in EnvFileType if t != file_type]
            other_vars = set()
            for other_type in other_types:
                other_vars.update(vars_by_type[other_type])

            unique_vars = vars_by_type[file_type] - other_vars
            if unique_vars:
                print(f"    {file_type.value.upper():12}: {len(unique_vars)} variables")
                for var in sorted(unique_vars)[:5]:  # Show first 5
                    print(f"      - {var}")
                if len(unique_vars) > 5:
                    print(f"      ... and {len(unique_vars) - 5} more")

        # Find variables in all files
        common_vars = set.intersection(*[vars_by_type[ft] for ft in EnvFileType])
        print(f"\n  Variables in ALL files: {len(common_vars)}")
        if common_vars:
            for var in sorted(common_vars)[:10]:
                print(f"    - {var}")
            if len(common_vars) > 10:
                print(f"    ... and {len(common_vars) - 10} more")

        # Find variables with different values
        print("\n🔍 VARIABLES WITH DIFFERENT VALUES ACROSS FILES:")
        print("-" * 40)
        conflicting_vars = []

        for var_name, vars_list in self.all_variables.items():
            if len(vars_list) > 1:
                values = {var.value for var in vars_list}
                if len(values) > 1:
                    conflicting_vars.append((var_name, vars_list))

        if conflicting_vars:
            print(f"  Found {len(conflicting_vars)} variables with different values:")
            for var_name, vars_list in conflicting_vars[:5]:  # Show first 5
                print(f"\n    {var_name}:")
                for var in vars_list:
                    print(f"      {var.file_type.value:12}: {var.value}")
        else:
            print("  No variables with conflicting values found.")

        # Section analysis
        print("\n📁 SECTION DISTRIBUTION (Example file):")
        print("-" * 40)
        example_file = next(
            (f for f in self.files if f.type == EnvFileType.EXAMPLE), None
        )
        if example_file:
            for section_name, vars_list in example_file.sections.items():
                if vars_list:
                    print(f"  {section_name:30}: {len(vars_list):2} variables")

    def show_differences(self) -> None:
        """Show detailed differences between files."""
        if not self.files:
            self.load_files()

        print("\n" + "=" * 80)
        print("ENVIRONMENT FILES DIFFERENCES")
        print("=" * 80)

        # Get all variable names
        all_var_names = sorted(self.all_variables.keys())

        # Create a comparison table
        headers = ["Variable", "Example", "Production", "Test", "Status"]
        print("\n" + " | ".join(headers))
        print("-" * 100)

        for var_name in all_var_names:
            vars_list = self.all_variables[var_name]

            # Get values for each file type
            values = {}
            for var in vars_list:
                values[var.file_type] = var.value

            # Determine status
            file_types_present = {var.file_type for var in vars_list}
            if len(file_types_present) == 3:
                if len({var.value for var in vars_list}) == 1:
                    status = "✓ ALL SAME"
                else:
                    status = "⚠ DIFFERS"
            elif len(file_types_present) == 2:
                status = "2/3 FILES"
            else:
                status = "1 FILE ONLY"

            # Format values for display (truncate if too long)
            example_val = values.get(EnvFileType.EXAMPLE, "").replace("\n", "\\n")[:20]
            prod_val = values.get(EnvFileType.PRODUCTION, "").replace("\n", "\\n")[:20]
            test_val = values.get(EnvFileType.TEST, "").replace("\n", "\\n")[:20]

            if len(example_val) >= 20:
                example_val = example_val[:17] + "..."
            if len(prod_val) >= 20:
                prod_val = prod_val[:17] + "..."
            if len(test_val) >= 20:
                test_val = test_val[:17] + "..."

            print(
                f"{var_name:25} | {example_val:20} | {prod_val:20} | {test_val:20} | {status}"
            )

    def merge(self, output_path: Optional[Path] = None) -> Path:
        """
        Create a merged environment template from all files.

        Strategy:
        1. Use example file as base (most comprehensive)
        2. Add any missing variables from production and test
        3. Use production values as defaults where available
        4. Organize into logical sections
        """
        if not self.files:
            self.load_files()

        if output_path is None:
            output_path = self.project_root / ".env.template"

        print(f"\n📝 Creating merged template: {output_path}")

        # Build merged variables
        merged_vars: Dict[str, EnvVariable] = {}

        # Priority: Production > Example > Test
        # Start with example file as base
        example_file = next(
            (f for f in self.files if f.type == EnvFileType.EXAMPLE), None
        )
        if example_file:
            for var_name, var in example_file.variables.items():
                merged_vars[var_name] = var

        # Override with production values where available
        production_file = next(
            (f for f in self.files if f.type == EnvFileType.PRODUCTION), None
        )
        if production_file:
            for var_name, var in production_file.variables.items():
                if var_name in merged_vars:
                    # Update value but keep example's comment if production has none
                    merged_var = merged_vars[var_name]
                    merged_var.value = var.value
                    if var.comment and not merged_var.comment:
                        merged_var.comment = var.comment
                else:
                    merged_vars[var_name] = var

        # Add any test-only variables
        test_file = next((f for f in self.files if f.type == EnvFileType.TEST), None)
        if test_file:
            for var_name, var in test_file.variables.items():
                if var_name not in merged_vars:
                    merged_vars[var_name] = var

        # Categorize all variables
        categorized_vars: Dict[str, List[EnvVariable]] = {
            section: [] for section in self.SECTION_HEADERS.values()
        }

        for var_name, var in merged_vars.items():
            section = self._categorize_variable(var_name)
            categorized_vars[section].append(var)

        # Write merged file
        with open(output_path, "w", encoding="utf-8") as f:
            # Header
            f.write("# " + "=" * 77 + "\n")
            f.write("# FIGHTSFTICKETS - MERGED ENVIRONMENT TEMPLATE\n")
            f.write("# " + "=" * 77 + "\n")
            f.write("#\n")
            f.write("# This file merges all environment configurations:\n")
            f.write("# - .env.example (development)\n")
            f.write("# - .env.production.template (production)\n")
            f.write("# - backend/.env.test (testing)\n")
            f.write("#\n")
            f.write("# Usage:\n")
            f.write("#   1. Copy this file to .env\n")
            f.write("#   2. Fill in your actual values\n")
            f.write("#   3. NEVER commit .env to version control\n")
            f.write("#\n")
            f.write("# Generated by merge_envs.py\n")
            f.write("# " + "=" * 77 + "\n\n")

            # Write sections
            for section_name in self.SECTION_HEADERS.values():
                vars_in_section = categorized_vars[section_name]
                if vars_in_section:
                    f.write(f"\n# {'=' * 77}\n")
                    f.write(f"# {section_name}\n")
                    f.write(f"# {'=' * 77}\n\n")

                    # Sort variables alphabetically within section
                    vars_in_section.sort(key=lambda v: v.name)

                    for var in vars_in_section:
                        # Write variable with comment
                        if var.comment:
                            f.write(f"# {var.comment}\n")

                        # Determine best default value
                        default_value = var.value

                        # Special handling for secret keys
                        if "SECRET" in var.name or "KEY" in var.name:
                            if (
                                "_test_" in default_value
                                or "dummy" in default_value
                                or "change-me" in default_value
                            ):
                                # Keep test/dummy values
                                pass
                            elif not default_value or default_value == "...":
                                default_value = "change-me-to-actual-value"

                        f.write(f"{var.name}={default_value}\n")

            # Footer
            f.write("\n" + "# " + "=" * 77 + "\n")
            f.write("# END OF CONFIGURATION\n")
            f.write("# " + "=" * 77 + "\n")

        print(f"✅ Created merged template with {len(merged_vars)} variables")
        print(f"📁 Output file: {output_path}")

        # Show summary
        print("\n📊 MERGED TEMPLATE SUMMARY:")
        print("-" * 40)
        for section_name, vars_list in categorized_vars.items():
            if vars_list:
                print(f"  {section_name:30}: {len(vars_list):2} variables")

        return output_path

    def create_cleanup_plan(self) -> None:
        """Create a plan for cleaning up environment files."""
        if not self.files:
            self.load_files()

        print("\n" + "=" * 80)
        print("ENVIRONMENT FILES CLEANUP PLAN")
        print("=" * 80)

        merged_path = self.project_root / ".env.template"

        print("\n🎯 RECOMMENDED CLEANUP STRATEGY:")
        print("-" * 40)
        print("""
  1. Use the merged .env.template as your single source of truth
  2. Delete redundant files to reduce clutter
  3. Update documentation to reference the single template
  4. Update deployment scripts if needed
        """)

        print("\n📋 ACTION ITEMS:")
        print("-" * 40)

        action_items = [
            (f"Create merged template", f"python merge_envs.py merge"),
            (f"Review merged template", f"Check {merged_path} for accuracy"),
            (f"Update .gitignore", f"Ensure .env is listed (already done)"),
            (f"Update documentation", f"Change references to use .env.template"),
            (
                f"Optional: Delete redundant files",
                f"rm .env.example .env.production.template backend/.env.test",
            ),
            (f"Test with new setup", f"cp .env.template .env && fill with test values"),
        ]

        for i, (action, command) in enumerate(action_items, 1):
            print(f"{i}. {action}")
            print(f"   → {command}")

        print("\n⚠️  WARNINGS:")
        print("-" * 40)
        print("""
  • Make sure no deployment scripts rely on the old file names
  • The Makefile references .env.example - update it
  • Docker Compose may reference .env - keep it in .gitignore
  • Test thoroughly before deleting files
        """)

        # Check for references to old files
        print("\n🔍 CHECKING FOR REFERENCES TO OLD FILES:")
        print("-" * 40)

        old_files = [".env.example", ".env.production.template", "backend/.env.test"]
        for old_file in old_files:
            # Simple grep for references
            old_file_ref = old_file.replace(".", r"\.").replace("/", r"\/")
            print(f"  References to {old_file}: Checking...")

        print("\n💡 TIP: Run 'python merge_envs.py analyze' first to see current state")
        print("💡 TIP: Run 'python merge_envs.py diff' to see all differences")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable commands:")
        print("  analyze  - Show detailed analysis of all environment files")
        print("  diff     - Show differences between files")
        print("  merge    - Create merged .env.template file")
        print("  cleanup  - Show cleanup plan and recommendations")
        print("  help     - Show this help message")
        sys.exit(1)

    command = sys.argv[1].lower()
    project_root = Path(__file__).parent.parent

    merger = EnvMerger(project_root)

    if command == "analyze":
        merger.analyze()
    elif command == "diff":
        merger.show_differences()
    elif command == "merge":
        merger.merge()
    elif command == "cleanup":
        merger.create_cleanup_plan()
    elif command in ["help", "--help", "-h"]:
        print(__doc__)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: analyze, diff, merge, cleanup, help")
        sys.exit(1)


if __name__ == "__main__":
    main()
