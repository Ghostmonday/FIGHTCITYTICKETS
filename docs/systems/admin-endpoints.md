# Admin Endpoints

Purpose: describe privileged routes and protections.

## Responsibilities
- Provide operational views or actions for staff (details depend on implementation).
- Enforce authentication/authorization and rate limiting.

## Key file
- `backend/src/routes/admin.py`

## Expected behavior
- Mounted under `/admin` (check router prefix in file).
- Should be behind auth (token/API key or IP allowlist) — ensure equivalent protection when rebuilding.
- Shares limiter instance to prevent abuse.

## Rebuild checklist
- Decide auth mechanism (header token, basic auth, or upstream proxy allowlist).
- Return structured JSON; include request ID in responses.
- Do not expose PII beyond operational need; paginate any lists.
