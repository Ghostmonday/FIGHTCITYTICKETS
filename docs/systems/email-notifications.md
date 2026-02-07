# Email Notifications (SendGrid)

Purpose: outline email triggers, content, and failure handling.

## Responsibilities
- Send confirmations and status emails after key events (payment success, mail sent).
- Use service email as sender; support email for replies.
- Handle failures gracefully without blocking main flows.

## Key files
- `backend/src/services/email_service.py` — SendGrid integration.
- `backend/src/routes/webhooks.py` — calls after fulfillment steps.
- `backend/src/config.py` — email settings.

## Flow
1. Webhook confirms payment and (optionally) mail dispatch.
2. Email service builds template (HTML/text) with tracking IDs and support links.
3. Send via SendGrid API.
4. Log success/failure; do not crash webhook on email errors.

## Config / env
- `SENDGRID_API_KEY`
- `SERVICE_EMAIL` (from)
- `SUPPORT_EMAIL` (reply-to/contact)
- `APP_URL` for links.

## Rebuild checklist
- Keep templates minimal and compliant; include disclaimers.
- Use request ID in logs for correlation.
- Implement retry/backoff; but avoid duplicate emails by checking event idempotency.
