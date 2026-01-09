with open('tests/test_citation_validation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
# replace lines 189-196 (0-indexed 188-195)
new_lines = lines[:188] + [
    '        invalid_citations = [\n',
    '            "12345",  # Too short\n',
    '            "1234567890123",  # Too long\n',
    '            "!!!!!!",  # No alphanumeric characters\n',
    '            "   ",  # Whitespace only\n',
    '            "",  # Empty string\n',
    '        ]\n'
] + lines[196:]
with open('tests/test_citation_validation.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
