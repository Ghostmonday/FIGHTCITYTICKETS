# Product Overview & Ops

Purpose: describe what the service does, compliance stance, environments, and operational expectations so a builder can recreate the product intent, not just the code.

## What the product is
- SaaS that automates parking-ticket appeals for ~15 US cities.
- Workflow: validate citation → capture user statement → AI refine → draft letter → capture photos/signature → Stripe checkout → webhook fulfillment → PDF + Lob mail → email confirmations → status lookup.
- Positioning: procedural document preparation only (UPL compliance). Not a law firm.

## Core guardrails
- Database-first: persist intake/draft before payment; Stripe metadata stores IDs only.
- UPL compliance: disclaimers everywhere; no legal advice; blocks states TX/NC/NJ/WA.
- Idempotency: webhook cache; database state transitions are the source of truth.
- Resilience: rate limiting, circuit breakers for external APIs, request IDs, structured logs.

## Environments & URLs
- Local: web `http://localhost:3000`, api `http://localhost:8000`.
- API base: configurable via `API_URL`, `NEXT_PUBLIC_API_BASE`.
- App base: `APP_URL`; used in emails and redirects.

## External services
- Stripe (checkout + webhooks) — requires secret, publishable, webhook secret, price ID.
- Lob (mail + address verification) — `LOB_API_KEY`, `LOB_MODE` (live/test).
- DeepSeek (statement refinement) — `DEEPSEEK_API_KEY`.
- Google Places (address autocomplete) — `NEXT_PUBLIC_GOOGLE_PLACES_API_KEY`.
- SendGrid (email) — `SENDGRID_API_KEY`, `SERVICE_EMAIL`, `SUPPORT_EMAIL`.
- PostgreSQL 16 — `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.

## Observability & safety
- Logging: JSON by default to stdout; request IDs included.
- Sentry: optional, enabled via `SENTRY_DSN`.
- Metrics: request/error counters in health module; rate limit events handled explicitly.
- Health endpoints: `/health`, `/health/ready`, `/health/detailed`.

## Compliance artifacts
- Legal disclaimers rendered by shared components; footer + inline variants.
- State blocking enforced in city registry and UI messaging.
- Data handling documented in existing compliance docs (retain sensitive data minimally).

## Runbooks (high-level)
- Startup: ensure .env populated; `docker compose up --build`.
- Payment issues: check Stripe dashboard + webhook logs; verify metadata IDs map to DB rows.
- Mail failures: inspect Lob logs; retry via mail service with same IDs for idempotency.
- AI failures: fall back to user-provided statement; surface friendly errors.
- Incident response: follow playbooks in compliance/operations docs.
