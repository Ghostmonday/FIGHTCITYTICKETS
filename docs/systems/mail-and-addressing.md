# Mail Generation & Addressing (Lob)

Purpose: generate appeal PDFs and dispatch via Lob with address verification and retries.

## Responsibilities
- Build PDF letter from stored data (citation, statement, signature).
- Verify recipient address via Lob US verification API.
- Send certified or standard mail via Lob with tracking info.
- Record mail status back to DB for status lookup.

## Key files
- `backend/src/services/mail.py` — PDF generation, Lob client usage.
- `backend/src/services/address_validator.py` — address verification helper.
- `backend/src/routes/webhooks.py` — triggers mail after payment success.
- Frontend signature/photo capture: `frontend/app/appeal/camera/page.tsx`, `signature/page.tsx`.

## Flow
1. After payment success, backend fetches intake/draft data.
2. Validate/standardize address; if invalid, flag error for manual handling.
3. Generate PDF (template + data + signature + photos if included).
4. Call Lob to create letter (certified by default if price matches).
5. Store Lob IDs/tracking in DB; update status for user lookup.

## Config / env
- `LOB_API_KEY`
- `LOB_MODE` (`live` or `test`)
- Template paths/settings inside `mail.py` (ensure deterministic layout).

## Error handling
- If address verification fails, do not send mail; log and surface status requiring intervention.
- Lob API errors should be retried with backoff; guard with circuit breaker.
- PDF generation errors should fail the fulfillment step but keep payment recorded; allow replay.

## Rebuild checklist
- Use a deterministic PDF template; include disclaimer and signature.
- Store Lob letter ID and tracking URL in DB.
- Keep mail sending idempotent using existing IDs; avoid duplicate sends on retries.
