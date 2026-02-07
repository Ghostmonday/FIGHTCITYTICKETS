# Backend Configuration & Settings

Purpose: define env schema, defaults, and safety checks the backend expects.

## Responsibilities
- Centralize configuration via Pydantic settings.
- Provide helper methods (CORS origins list, price IDs, environment flags).
- Validate required secrets and URLs early.

## Key file
- `backend/src/config.py` — Pydantic `Settings` class and helpers.

## Important fields (non-exhaustive)
- App/URLs: `app_env`, `app_url`, `api_url`, `frontend_url`, `cors_origins`.
- Security: `secret_key`, `allowed_hosts`, `json_logging`, `log_level`.
- Database: `database_url`, `db_pool_size`, `db_pool_timeout`.
- Stripe: `stripe_secret_key`, `stripe_publishable_key`, `stripe_webhook_secret`, `stripe_price_certified`.
- Lob: `lob_api_key`, `lob_mode` (`live`/`test`).
- AI: `deepseek_api_key`.
- Email: `sendgrid_api_key`, `service_email`, `support_email`.
- Feature flags: blocked states, telemetry toggle.

## Behavior
- CORS helper returns list parsed from CSV env.
- Price/ID fields are treated as required; missing values should fail fast.
- Environment detection drives Sentry environment and logging verbosity.

## Rebuild checklist
- Implement settings via Pydantic BaseSettings; load from env with case-insensitive keys.
- Provide helper methods for lists and defaults matching current semantics.
- Ensure secrets are mandatory in production; allow safe fallbacks in dev only.
