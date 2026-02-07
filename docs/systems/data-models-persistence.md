# Data Models & Persistence

Purpose: describe database schema, service layer, and lifecycle so storage can be recreated.

## Responsibilities
- Persist intake, drafts, and payments before Stripe checkout.
- Provide DB connectivity + health checks.
- Expose safe CRUD via service layer (no raw DB access from routes).

## Key files
- `backend/src/models/__init__.py` — SQLAlchemy models `Intake`, `Draft`, `Payment`.
- `backend/src/services/database.py` — DB service, engine/session creation, helpers.
- Migrations: expected via Alembic (not shown here; tables validated at startup).

## Entities (conceptual)
- Intake: citation metadata, user contact, city, vehicle details, photos refs, status.
- Draft: refined statement text, AI inputs/outputs, signatures, generated PDF references.
- Payment: Stripe session/intent IDs, status, amounts, currency, links to intake/draft.

## Patterns
- Database-first: create Intake/Draft records before checkout session.
- Stripe metadata carries only internal IDs; actual data remains in DB.
- Health check pings DB engine on startup; engine disposed on shutdown.
- Sessions are managed via service; ensure scoped sessions per request.

## Rebuild checklist
- Use SQLAlchemy 2.0 style models.
- Define proper FKs between Payment → Intake/Draft.
- Add created_at/updated_at timestamps and idempotency keys where applicable.
- Provide `health_check()` that verifies connectivity.
