# Citation Validation & City Registry

Purpose: handle citation parsing, validation, city detection, and state blocking.

## Responsibilities
- Validate citation numbers per city rules.
- Detect city from input (pattern + optional OCR data).
- Enforce blocked states (TX, NC, NJ, WA by default).
- Provide city-specific schema/adapters for downstream forms.

## Key files
- `backend/src/routes/tickets.py` — `POST /tickets/validate`.
- `backend/src/services/citation.py` — validation logic.
- `backend/src/services/city_registry.py` — registry of supported cities, blocked states.
- `backend/src/services/schema_adapter.py` — per-city schema adjustments.
- `frontend/app/lib/cities.ts`, `california-cities.ts`, `city-routing.ts` — client registry + routing.

## Flow
1. Client sends citation details (number, city/state hints, possibly plate and date).
2. Backend validates format, looks up city in registry, checks blocklist.
3. Returns normalized city payload (id, name, deadlines if available) or error with reason.
4. Frontend routes user to city-specific page via routing helpers.

## Data contracts (conceptual)
- Request: `{ citationNumber, state, cityHint?, plate?, issueDate? }`.
- Response success: `{ cityId, cityName, isBlocked: false, deadline?, notes? }`.
- Response blocked: `{ error: "STATE_BLOCKED", state }`.
- Response invalid: `{ error: "INVALID_CITATION", details }`.

## Rebuild checklist
- Keep registry as single source for supported cities and blocked states.
- Implement deterministic validation per city; include unit tests for patterns.
- Ensure consistent error codes/messages for UI handling.
- Maintain routing map in frontend in sync with backend city IDs.
