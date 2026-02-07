# Testing & QA

Purpose: outline available tests and recommended manual checks.

## Automated tests
- Backend: run via Docker Compose — `docker compose exec api pytest` (per README).
- Integration: `docker compose exec api pytest tests/test_e2e_integration.py` (per README).
- Frontend: `cd frontend && npm test` (Jest).
- Frontend unit tests present for API client and appeal context: `frontend/app/lib/api-client.test.ts`, `frontend/app/lib/appeal-context.test.tsx`.

## Manual test checklist (suggested)
- Citation validation: valid/invalid patterns; blocked states.
- AI refinement: success and failure fallback.
- Appeal flow: full journey with photos/signature, refresh mid-flow (state persists).
- Checkout: create session, handle Stripe error, cancel, success redirect.
- Webhook: simulate `checkout.session.completed`; confirm PDF/mail/email triggered.
- Status lookup: valid tracking ID vs unknown ID.
- Compliance: disclaimers present on all pages; blocked state messaging.
- Observability: request IDs in logs; health endpoints respond.

## Rebuild checklist
- Mirror or extend existing tests; ensure env vars available in test harness.
- Add webhook replay tests for idempotency.
