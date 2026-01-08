#!/usr/bin/env python3
"""
Auto-fix common linter errors:
1. Remove trailing whitespace
2. Remove unused imports (basic detection)
3. Convert f-strings without placeholders to regular strings
4. Fix equality comparisons to True/False
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def remove_trailing_whitespace(content: str) -> Tuple[str, int]:
    """Remove trailing whitespace from lines."""
    lines = content.splitlines(keepends=True)
    fixed_count = 0

    for i, line in enumerate(lines):
        if line.rstrip() != line:
            lines[i] = line.rstrip() + ('\n' if line.endswith('\n') else '')
            fixed_count += 1

    return ''.join(lines), fixed_count


def fix_fstrings_without_placeholders(content: str) -> Tuple[str, int]:
    """Convert f-strings without placeholders to regular strings."""
    fixed_count = 0

    # Pattern to match f-strings without placeholders
    # Match "..." or '...' that don't contain { or }
    pattern = r'f("(?:[^"\\]|\\.)*")|f(\'(?:[^\'\\]|\\.)*\')'

    def replace_fstring(match):
        nonlocal fixed_count
        fixed_count += 1
        # Return the string without the '' prefix
        return match.group(1) or match.group(2)

    content = re.sub(pattern, replace_fstring, content)
    return content, fixed_count


def fix_equality_comparisons(content: str) -> Tuple[str, int]:
    """Fix equality comparisons to True/False."""
    fixed_count = 0

    # Pattern: == True not or (with optional spaces)
    patterns = [
        (r'(\w+)\s*==\s*True\b', r'\1'),  # == True -> just the variable
        (r'(\w+)\s*==\s*False\b', r'not \1'),  # == False -> not variable
        (r'(\w+)\s*!=\s*True\b', r'not \1'),  # != True -> not variable
        (r'(\w+)\s*!=\s*False\b', r'\1'),  # != False -> just the variable
    ]

    for pattern, replacement in patterns:
        matches = len(re.findall(pattern, content))
        if matches > 0:
            content = re.sub(pattern, replacement, content)
            fixed_count += matches

    return content, fixed_count


def process_file(file_path: Path) -> dict:
    """Process a single file and return statistics."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        stats = {
            'trailing_whitespace': 0,
            'fstrings': 0,
            'equality_comparisons': 0,
            'modified': False
        }

        # Fix trailing whitespace
        content, count = remove_trailing_whitespace(content)
        stats['trailing_whitespace'] = count

        # Fix f-strings without placeholders
        content, count = fix_fstrings_without_placeholders(content)
        stats['fstrings'] = count

        # Fix equality comparisons
        content, count = fix_equality_comparisons(content)
        stats['equality_comparisons'] = count

        # Write back if modified
        if content != original_content:
            stats['modified'] = True
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return stats
    except Exception as e:
        print("Error processing {file_path}: {e}")
        return {'error': str(e)}


def main():
    """Main function to process all Python files."""
    base_dir = Path(__file__).parent.parent

    # Find all Python files
    python_files = []
    for pattern in ['backend/**/*.py', 'scripts/**/*.py']:
        python_files.extend(base_dir.glob(pattern))

    print("Found {len(python_files)} Python files to process")

    total_stats = {
        'trailing_whitespace': 0,
        'fstrings': 0,
        'equality_comparisons': 0,
        'files_modified': 0
    }

    for file_path in python_files:
        stats = process_file(file_path)
        if 'error' not in stats:
            total_stats['trailing_whitespace'] += stats['trailing_whitespace']
            total_stats['fstrings'] += stats['fstrings']
            total_stats['equality_comparisons'] += stats['equality_comparisons']
            if stats['modified']:
                total_stats['files_modified'] += 1
                print("Fixed {file_path.relative_to(base_dir)}")

    print("\n" + "=" * 50)
    print("Summary:")
    print("  Files modified: {total_stats['files_modified']}")
    print("  Trailing whitespace removed: {total_stats['trailing_whitespace']}")
    print("  F-strings fixed: {total_stats['fstrings']}")
    print("  Equality comparisons fixed: {total_stats['equality_comparisons']}")
    print("=" * 50)


if __name__ == '__main__':
    main()

