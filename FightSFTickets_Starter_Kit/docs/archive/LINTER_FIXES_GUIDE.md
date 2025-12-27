# Linter Errors Fix Guide

## Summary
- **Initial errors:** 310
- **After auto-fix script:** 306
- **Remaining categories:**
  1. Trailing whitespace (~50 remaining)
  2. Unused imports (~80)
  3. F-strings without placeholders (~30 remaining)
  4. Equality comparisons to True/False (~20)
  5. Bare except clauses (~10)
  6. Module-level imports not at top (~5)
  7. Other issues (~20)

## Quick Fix Commands

### 1. Fix All Trailing Whitespace (PowerShell)
```powershell
cd FightSFTickets_Starter_Kit
Get-ChildItem -Recurse -Include *.py,*.md | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $newContent = $content -replace ' +$', ''
    if ($content -ne $newContent) {
        Set-Content -Path $_.FullName -Value $newContent -NoNewline
        Write-Host "Fixed: $($_.FullName)"
    }
}
```

### 2. Use Trunk Auto-fix (if available)
```bash
trunk fmt --write
```

## Manual Fixes Needed

### Unused Imports
Remove unused imports from these files:
- `backend/src/services/statement.py` - Remove `typing.Any`
- `backend/src/services/schema_adapter.py` - Remove `typing.Tuple`
- `backend/src/services/email_service.py` - Remove `datetime.datetime`
- `backend/src/services/appeal_storage.py` - Remove `json`
- `backend/src/middleware/rate_limit.py` - Remove `typing.Callable`
- And ~75 more files (see linter output)

### Equality Comparisons
Replace:
- `x == True` → `x`
- `x == False` → `not x`
- `x != True` → `not x`
- `x != False` → `x`

Files needing this fix:
- `backend/tests/test_citation_validation.py`
- `backend/tests/test_sf_schema_adapter.py`
- `backend/tests/test_schema_adapter.py`
- `backend/src/services/database.py`
- `backend/generate_lob_csv.py`

### Bare Except Clauses
Replace `except:` with specific exceptions:
- `except Exception:` or `except (ValueError, KeyError):`

Files needing this:
- `scripts/check_namecheap_domains.py`
- `scripts/fix_dns_now.py`
- `scripts/configure_subdomain_dns.py`
- `scripts/verify_dns_namecheap.py`
- `scripts/configure_existing_domains.py`
- `scripts/fix_dns_fightcitytickets.py`

### Module-Level Imports Not at Top
Move imports to the top of the file:
- `backend/run_e2e_tests.py` (line 25)
- `backend/test_address_validator_live.py` (lines 20-21)
- `backend/test_address_validator_standalone.py` (lines 47-48)

### Exception Handling
Add `from err` or `from None` to exception raises:
```python
# Before
except ValueError as e:
    raise CustomError("message")

# After
except ValueError as e:
    raise CustomError("message") from e
```

Files needing this:
- `backend/src/services/stripe_service.py`
- `backend/src/routes/statement.py`
- `backend/src/routes/status.py`
- `backend/src/services/city_registry.py`
- `backend/tests/test_sf_schema_adapter.py`

### Other Issues
- **Undefined name `settings`** in `backend/src/routes/webhooks.py:230`
- **Lambda expression** in `backend/src/services/citation.py:18` (already a def, may be false positive)
- **Dictionary key repeated** in `backend/src/services/address_validator.py:107`
- **SSL verification disabled** in `backend/test_address_validator_standalone.py:92` (security issue)
- **Dockerfile issues** - Add HEALTHCHECK and user creation

## Automated Fix Script

Run the provided script:
```bash
python scripts/fix_linter_errors.py
```

This will fix:
- Trailing whitespace
- F-strings without placeholders
- Some equality comparisons

## Priority Order

1. **High Priority (Security/Functionality):**
   - SSL verification disabled
   - Undefined names
   - Syntax errors in `scripts/e2e_full_route_coverage.py`

2. **Medium Priority (Code Quality):**
   - Unused imports
   - Bare except clauses
   - Exception handling improvements

3. **Low Priority (Style):**
   - Trailing whitespace
   - F-strings without placeholders
   - Equality comparisons

## Estimated Time

- Automated fixes: ~5 minutes
- Manual fixes: ~2-3 hours for all files
- Or focus on high-priority only: ~30 minutes

