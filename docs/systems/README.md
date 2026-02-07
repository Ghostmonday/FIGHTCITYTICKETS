# Systems Documentation Index

This folder breaks the application into focused systems so another AI agent can recreate the product end to end. Each guide includes purpose, boundaries, key files, data contracts, flows, configuration, error-handling, and rebuild notes.

## Systems
- `product-overview-ops.md` — Vision, compliance stance, environments, runbooks, observability.
- `backend-platform.md` — FastAPI app bootstrap, middleware, router wiring, logging, Sentry.
- `backend-config.md` — Settings schema, env vars, defaults, safety validation.
- `data-models-persistence.md` — SQLAlchemy models, DB service, migrations, lifecycle.
- `citation-and-city.md` — Citation validation, city detection, registry, state blocking.
- `statement-refinement.md` — DeepSeek integration, prompts, UPL safeguards, retries.
- `appeal-lifecycle.md` — Intake/draft storage, status tracking, telemetry.
- `payments-checkout.md` — Stripe checkout creation, metadata, price config, failures.
- `webhooks-fulfillment.md` — Stripe webhook handling, idempotency, fulfillment actions.
- `mail-and-addressing.md` — PDF generation, Lob mail + address verification, retries.
- `email-notifications.md` — SendGrid triggers, templates, error handling.
- `admin-endpoints.md` — Admin routes, protections, operations.
- `health-observability.md` — Health/readiness endpoints, metrics, logging standards.
- `frontend-architecture.md` — Next.js layout, routing, error boundaries, providers, styling.
- `frontend-appeal-flow.md` — UX flow pages (home → city → appeal → camera → review → signature → checkout → status).
- `frontend-state-data.md` — Appeal context, sessionStorage, API client patterns.
- `frontend-integrations.md` — OCR, Google Places autocomplete, Stripe client usage, AI surfaces.
- `frontend-compliance-ux.md` — Disclaimers, blocked states surfacing, footer/legal copy.
- `seo-and-content.md` — Blog, SEO metadata, sitemap/robots.
- `testing-and-qa.md` — Tests available, how to run, manual checklists.
- `tooling-deploy.md` — Docker Compose, scripts, local dev commands, lint/format.
- `infrastructure-nginx.md` — Reverse proxy, SSL, routing to web/api, maintenance page.
