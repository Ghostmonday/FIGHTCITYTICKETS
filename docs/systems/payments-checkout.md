# Payments & Checkout (Stripe)

Purpose: describe how checkout sessions are created and tied to persisted data.

## Responsibilities
- Create Stripe Checkout Session for appeal purchase.
- Use database-first pattern: persist intake/draft before creating session.
- Store only IDs in Stripe metadata for privacy and idempotency.
- Return redirect URL to frontend.

## Key files
- `backend/src/routes/checkout.py` — `POST /checkout/create-appeal-checkout`.
- `backend/src/services/stripe_service.py` — session creation, price handling, error handling.
- `frontend/app/appeal/checkout/page.tsx` — client integration.

## Flow
1. Client calls checkout endpoint with intake/draft IDs (already stored).
2. Backend validates records exist and not already paid.
3. Create Checkout Session with:
   - Line item price `stripe_price_certified`.
   - Currency (usually USD).
   - Success/cancel URLs from settings.
   - Metadata: `intake_id`, `draft_id`, `tracking_id`.
4. Return session URL for redirect.

## Config / env
- `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_PRICE_CERTIFIED`
- `STRIPE_WEBHOOK_SECRET` (for webhook verification)
- `APP_URL` / `FRONTEND_URL` for success/cancel.

## Error handling
- Validate required IDs; return structured errors if missing.
- Catch Stripe API errors; map to APIError codes.
- Rate limiting via shared limiter.

## Rebuild checklist
- Ensure metadata carries only internal IDs (no PII).
- Use HTTPS URLs in production.
- Set automatic tax/shipping off unless added intentionally.
- Keep idempotency by checking existing payments before creating new sessions.
