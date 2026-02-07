# Webhooks & Fulfillment

Purpose: handle Stripe webhook events idempotently and trigger fulfillment (PDF + mail + email).

## Responsibilities
- Verify Stripe webhook signatures.
- Enforce idempotency (cache/store processed events).
- Update payment records and trigger downstream actions (mail, email).
- Handle retries safely.

## Key files
- `backend/src/routes/webhooks.py` — `POST /webhook/webhook`.
- `backend/src/services/stripe_service.py` — event verification, helpers.
- `backend/src/services/mail.py` — PDF generation + Lob dispatch.
- `backend/src/services/email_service.py` — notifications.
- `backend/src/services/database.py` — update payment/intake status.

## Flow
1. Stripe sends event (e.g., `checkout.session.completed`).
2. Verify signature with `STRIPE_WEBHOOK_SECRET`.
3. Check idempotency cache/storage to skip already-processed events.
4. Lookup Intake/Draft/Payment by metadata IDs.
5. Mark payment paid; generate PDF; call Lob to mail; send confirmation email.
6. Log outcomes; respond 200 even if downstream fails after marking event processed (decide policy).

## Config / env
- `STRIPE_WEBHOOK_SECRET`
- `LOB_API_KEY`, `LOB_MODE`
- `SENDGRID_API_KEY`, `SERVICE_EMAIL`, `SUPPORT_EMAIL`
- `APP_URL` for email links.

## Error handling & idempotency
- Signature verification failure → 400.
- Missing metadata/records → 400/404 with error code.
- Idempotent: cache event IDs; DB state guard ensures no duplicate mail on replay.
- Circuit breakers around Lob/SendGrid to prevent cascading failures; consider DLQ for retries.

## Rebuild checklist
- Treat webhook handler as pure side-effect orchestrator; keep it fast.
- Make DB updates transactional where possible.
- Ensure mail/email only happen after payment confirmed.
- Return quickly; log failures with request ID for later replay.
