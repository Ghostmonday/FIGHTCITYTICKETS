# Appeal Data Lifecycle

Purpose: capture how user inputs are persisted and progressed across steps.

## Responsibilities
- Store intake data (citation, contact, vehicle, photos).
- Store refined statement drafts and signature artifacts.
- Expose status lookup for users.
- Collect telemetry (optional) for OCR/UX metrics.

## Key files
- `backend/src/routes/appeals.py` — persistence endpoints for frontend.
- `backend/src/routes/status.py` — status lookup.
- `backend/src/routes/telemetry.py` — optional telemetry.
- `backend/src/services/database.py` — DB access layer.
- `frontend/app/lib/appeal-context.tsx` — client state holder.
- `frontend/app/appeal/*` — pages for data entry, review, signature, status.

## Flow (high level)
1. Intake: save citation + contact + city; return IDs.
2. Statement: save user text; optionally refine via AI; update draft record.
3. Photos: upload refs (currently client-managed references; ensure persisted).
4. Signature: capture and store (usually base64 or blob ref).
5. Checkout: Payment links to intake/draft IDs.
6. Post-payment: webhook updates status; mail service generates PDF and dispatches.
7. Status lookup: user queries by tracking ID; backend returns status and mail info.

## Data contracts (conceptual)
- Intake create: `{ citationNumber, cityId, userContact, vehicle, photos? } -> { intakeId, trackingId }`
- Draft update: `{ intakeId, statementRaw, statementRefined?, signature? } -> { draftId }`
- Status: `{ trackingId } -> { state, lastUpdated, mailStatus?, paymentStatus? }`

## Rebuild checklist
- Keep intake/draft IDs immutable and used across services (including Stripe metadata).
- Track status transitions in DB with timestamps.
- Ensure status endpoint does not leak PII beyond what user supplied for lookup.
