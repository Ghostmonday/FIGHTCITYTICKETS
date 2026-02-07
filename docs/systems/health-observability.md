# Health, Readiness & Observability

Purpose: define probes and logging/metrics expectations.

## Responsibilities
- Expose health endpoints for liveness/readiness.
- Provide request/error counters for lightweight metrics.
- Standardize logging with request IDs.
- Optional Sentry integration.

## Key files
- `backend/src/routes/health.py` — `/health`, `/health/ready`, `/health/detailed`.
- `backend/src/logging_config.py` — logging setup.
- `backend/src/sentry_config.py` — Sentry initialization.
- Metrics helpers imported in `app.py` middleware.

## Endpoints
- `/health` — basic liveness (always true if app responds).
- `/health/ready` — checks DB connectivity.
- `/health/detailed` — includes counts and dependency statuses.

## Logging
- JSON logs by default; file logging when JSON disabled.
- Include `request_id` and timestamps; respect `LOG_LEVEL`.

## Rebuild checklist
- Keep health endpoints light; avoid heavy queries.
- Ensure readiness fails when DB unavailable.
- Maintain request/error counters exposed internally (for scraping if needed).
- Wire Sentry with environment tag; safe to run without DSN.
