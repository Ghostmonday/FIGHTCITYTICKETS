# Trunk/IDE Linter Suppression Guide

This guide explains how to silence Trunk and IDE linter warnings in this project.

## Quick Solutions

### Option 1: Disable Unused Import Warnings Globally (Recommended)

The `backend/pyproject.toml` file has been configured to ignore unused import warnings globally:

```toml
[tool.ruff]
ignore = ["F401", "F841"]  # Unused imports and variables
```

This will silence unused import warnings across all Python files.

### Option 2: File-Level Suppression

Add this comment at the top of any file to suppress all Trunk warnings:

```python
# trunk-ignore-all(trunk-check-unused-imports)
# trunk-ignore-all(trunk-check-unused-variables)
```

### Option 3: Line-Level Suppression

For specific lines, add inline comments:

```python
import json  # trunk-ignore(trunk-check-unused-imports)
```

### Option 4: Disable Trunk Entirely

Edit `trunk.yaml` and disable specific linters:

```yaml
linters:
  ruff:
    enabled: false
  pylint:
    enabled: false
```

## Configuration Files Created

1. **`trunk.yaml`** - Main Trunk configuration
   - Located in project root
   - Configures which linters are enabled/disabled

2. **`backend/pyproject.toml`** - Python linting configuration
   - Configures Ruff, Pylint, and MyPy
   - Disables unused import warnings globally

3. **`.trunkignore`** - Files/directories to ignore
   - Similar to `.gitignore`
   - Tells Trunk to skip certain paths

## IDE-Specific Settings

### VS Code / Cursor

1. **Disable Trunk Extension:**
   - Open Settings (Ctrl+,)
   - Search for "Trunk"
   - Disable the Trunk extension

2. **Disable Python Linting:**
   - Settings → Search "python linting"
   - Disable "Pylint", "Ruff", or "Flake8"

3. **Workspace Settings:**
   Create `.vscode/settings.json`:
   ```json
   {
     "python.linting.enabled": false,
     "trunk.enabled": false
   }
   ```

### PyCharm

1. **Disable Inspections:**
   - File → Settings → Editor → Inspections
   - Uncheck "Unused import" under Python

2. **Suppress for File:**
   - Right-click file → Suppress → For file

### Other IDEs

Most IDEs allow you to:
- Disable specific linter rules in settings
- Add `# noqa` comments to suppress warnings
- Configure `.pylintrc` or `setup.cfg` files

## Common Suppression Patterns

### Python (Ruff/Pylint)

```python
# Ignore unused imports
import json  # noqa: F401

# Ignore unused variables
unused_var = 5  # noqa: F841

# Ignore entire file
# ruff: noqa
# pylint: disable-all
```

### Trunk-Specific

```python
# Suppress specific rule
# trunk-ignore(trunk-check-unused-imports)

# Suppress all Trunk checks for file
# trunk-ignore-all
```

## Troubleshooting

### Linter Cache Issues

If linter shows stale errors:

1. **Restart IDE** - Clears cache
2. **Reload Window** - VS Code/Cursor: Ctrl+Shift+P → "Reload Window"
3. **Clear Trunk Cache:**
   ```bash
   trunk cache clean
   ```

### False Positives

If you see errors for imports that don't exist:

1. Check the actual file content
2. Clear linter cache (see above)
3. Add file-level suppression if needed

## Best Practices

1. **Don't suppress everything** - Only suppress known false positives
2. **Use file-level suppressions** for test files (common false positives)
3. **Document why** you're suppressing warnings
4. **Review periodically** - Some suppressions may no longer be needed

## Files Already Configured

- `backend/tests/test_e2e_integration.py` - Has file-level suppressions
- `backend/pyproject.toml` - Global unused import suppression
- `trunk.yaml` - Trunk linter configuration

## Need Help?

- Check Trunk docs: https://docs.trunk.io
- Check Ruff docs: https://docs.astral.sh/ruff/
- Check your IDE's linting documentation

