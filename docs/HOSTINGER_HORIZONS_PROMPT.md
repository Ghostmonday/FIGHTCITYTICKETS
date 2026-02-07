# Hostinger Horizons – Single Prompt for Full Rebuild

Copy everything below the line into Horizons as one prompt. Refine with follow-up prompts as needed.

---

I want to build a **SaaS web app** that automates **parking-ticket appeals** for ~15 US cities. It is **procedural document preparation only** (UPL compliant); we are not a law firm. Below is a detailed breakdown so you can recreate the product intent, workflows, compliance guardrails, and technical setup.

**Priorities:** Database-first workflows (persist all data before payment), UPL compliance (disclaimers everywhere, no legal advice, blocked states), idempotent webhooks, and robust testing/deployment.

---

## Product Overview & Ops

**What the product is**
- SaaS that automates parking-ticket appeals for ~15 US cities.
- Workflow: validate citation → capture user statement → AI refine → draft letter → capture photos/signature → Stripe checkout → webhook fulfillment → PDF + Lob mail → email confirmations → status lookup.
- Positioning: procedural document preparation only (UPL compliance). Not a law firm.

**Core guardrails**
- **Database-first:** Persist intake/draft before payment; Stripe metadata stores only internal IDs (no PII).
- **UPL compliance:** Disclaimers on all user-facing pages; no legal advice; block states TX, NC, NJ, WA.
- **Idempotency:** Webhook event cache; database state is source of truth; no duplicate mail on retries.
- **Resilience:** Rate limiting, circuit breakers for external APIs, request IDs on every request, structured (JSON) logs.

**Environments & URLs**
- Local: web `http://localhost:3000`, API `http://localhost:8000`.
- Configurable via `API_URL`, `APP_URL`, `FRONTEND_URL`, `NEXT_PUBLIC_API_BASE` for redirects and links.

**External services (env vars)**
- **Stripe:** secret key, publishable key, webhook secret, certified price ID.
- **Lob:** `LOB_API_KEY`, `LOB_MODE` (live/test) — mail + address verification.
- **DeepSeek:** `DEEPSEEK_API_KEY` — statement refinement.
- **Google Places:** `NEXT_PUBLIC_GOOGLE_PLACES_API_KEY` — address autocomplete (optional).
- **SendGrid:** `SENDGRID_API_KEY`, `SERVICE_EMAIL`, `SUPPORT_EMAIL` — email notifications.
- **PostgreSQL 16:** `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.
- **Supabase:** Use for auth, realtime, or storage as needed. Credentials (wire these in env):
  - **URL:** `https://fvfaayuhhiujuabjnkae.supabase.co`
  - **Publishable (anon key):** `[REDACTED - set via NEXT_PUBLIC_SUPABASE_ANON_KEY env var]` → env: `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - **Secret (service role):** `[REDACTED - set via SUPABASE_SERVICE_ROLE_KEY env var]` → env: `SUPABASE_SERVICE_ROLE_KEY`
  - Also set `NEXT_PUBLIC_SUPABASE_URL=https://fvfaayuhhiujuabjnkae.supabase.co` for the frontend.

**Observability**
- JSON logging to stdout by default; include `request_id` and timestamps.
- Optional Sentry via `SENTRY_DSN`.
- Health endpoints: `/health` (liveness), `/health/ready` (DB), `/health/detailed` (counts + dependencies).

**Compliance artifacts**
- Legal disclaimers via shared components (full, compact, inline, elegant); footer disclaimer.
- State blocking enforced in city registry and UI; data handling minimal and documented.

---

## Backend Platform (FastAPI)

**Stack:** FastAPI 0.115+, Python 3.12.

**Responsibilities**
- Initialize app with lifespan hook (DB readiness check on startup; dispose on shutdown).
- Middleware order: Request ID → metrics (request/error counts) → rate limiting (e.g. slowapi) → CORS → error handling.
- Register routers: tickets, statement, appeals, checkout, webhooks, status, health, admin, places, telemetry.
- Centralize config (Pydantic settings), structured logging, optional Sentry.

**Key structure**
- Main app: `app.py` — middleware, router inclusion, CORS from `cors_origin_list()`.
- Middleware: request_id, errors (APIError + ErrorCode + unified JSON response), rate_limit, resilience (circuit breakers).
- Routes in a `routes/` folder; services in `services/`; no raw DB in routes — use a DB service layer.
- Share rate limiter instance with checkout, webhooks, admin, tickets, statement routes.

**Error handling**
- Custom `APIError` with error codes; `unhandled_exception_handler` fallback; rate-limit errors as structured JSON.
- Request IDs echoed to clients for support correlation.

---

## Backend Configuration & Settings

- Single Pydantic `Settings` class loading from env (e.g. `config.py`).
- Fields: `app_env`, `app_url`, `api_url`, `cors_origins`, `secret_key`, `database_url`, Stripe keys + webhook secret + `stripe_price_certified`, Lob key + mode, `deepseek_api_key`, SendGrid + service/support email, Supabase URL + anon key + service role key (see below).
- **Supabase credentials to include:** `NEXT_PUBLIC_SUPABASE_URL=https://fvfaayuhhiujuabjnkae.supabase.co`, `NEXT_PUBLIC_SUPABASE_ANON_KEY=[REDACTED - set via env var]`, `SUPABASE_SERVICE_ROLE_KEY=[REDACTED - set via env var]`.
- Helper: `cors_origin_list()` returning list from comma-separated `cors_origins`.
- Validate secrets in production (fail fast on defaults); allow safe dev defaults.

---

## Data Models & Persistence

**Stack:** SQLAlchemy 2.0, PostgreSQL 16; migrations (e.g. Alembic).

**Entities**
- **Intake:** citation metadata, user contact, city, vehicle, photo refs, status.
- **Draft:** refined statement, AI inputs/outputs, signature ref, PDF refs.
- **Payment:** Stripe session/intent IDs, status, amount, currency, FKs to Intake/Draft.

**Patterns**
- Database-first: create Intake and Draft before creating Stripe Checkout Session.
- Stripe metadata holds only `intake_id`, `draft_id`, `tracking_id` — no PII.
- DB service provides engine, sessions, `health_check()`; routes use service only.
- Timestamps (created_at/updated_at); idempotency keys where needed.

---

## Citation Validation & City Registry

**Endpoint:** `POST /tickets/validate`.

**Flow**
1. Client sends citation number, state, optional city hint, plate, issue date.
2. Backend validates format per city rules, looks up city in registry, checks blocked states (TX, NC, NJ, WA).
3. Returns city payload (id, name, deadline, notes) or error: `STATE_BLOCKED`, `INVALID_CITATION` with details.
4. Frontend uses city id for routing (e.g. `[city]` dynamic segment).

**Key pieces**
- Citation validation service; city registry as single source for supported cities and blocked states.
- Schema adapters per city for downstream forms.
- Frontend: cities registry and routing helpers in sync with backend city IDs.

---

## Statement Refinement (AI)

**Endpoint:** `POST /statement/refine`.

**Flow**
1. User writes statement; client sends it with citation context.
2. Backend builds prompt with UPL guardrails (no legal advice, no evidence recommendations), calls DeepSeek.
3. Response sanitized; if AI fails, return user’s original text with error flag for UI.
4. Circuit breaker around DeepSeek to avoid cascading failures; retries with backoff and timeout.

**Guardrails**
- Prompt must not add legal advice or recommend evidence; preserve user voice and facts.
- Safe fallback always (no null); filter risky content.

---

## Appeal Data Lifecycle

**Endpoints:** Appeals persistence (create/update intake and draft), status lookup, optional telemetry.

**Flow**
1. **Intake:** Save citation, contact, city, vehicle, photos → return `intakeId`, `trackingId`.
2. **Draft:** Save/update statement (raw + refined), signature → return `draftId`.
3. **Checkout:** Client passes intake/draft IDs; backend creates Stripe session linked to those IDs.
4. **Post-payment:** Webhook updates payment and intake status; triggers PDF + mail + email.
5. **Status:** User looks up by `trackingId`; backend returns state, lastUpdated, mailStatus, paymentStatus (no PII leak beyond what user supplied).

**Frontend**
- Appeal context (React context + sessionStorage) holds citation, contact, photos, statement, signature, intake/draft IDs.
- Persist to backend at each step; use same IDs for checkout.

---

## Payments & Checkout (Stripe)

**Endpoint:** `POST /checkout/create-appeal-checkout`.

**Flow**
1. Client sends intake_id and draft_id (already stored).
2. Backend verifies records exist and are not already paid.
3. Create Stripe Checkout Session: line item = `stripe_price_certified`, currency USD, success/cancel URLs from settings, metadata = `intake_id`, `draft_id`, `tracking_id` only.
4. Return session URL for redirect.

**Rules**
- No PII in metadata. Check for existing payment to avoid duplicate sessions. Rate limit this endpoint.

---

## Webhooks & Fulfillment

**Endpoint:** `POST /webhook/webhook` (or equivalent path Stripe will call).

**Flow**
1. Verify Stripe signature with webhook secret.
2. Check idempotency (e.g. cache/store event id); skip if already processed.
3. On `checkout.session.completed`: resolve Intake/Draft by metadata IDs, mark payment paid, generate PDF, send mail via Lob, send confirmation email via SendGrid.
4. Respond 200 quickly; log failures with request ID for replay; do not duplicate mail on retry.

**Error handling**
- Signature failure → 400. Missing metadata/records → 400/404 with error code. Circuit breakers for Lob/SendGrid.

---

## Mail Generation & Addressing (Lob)

**Responsibilities**
- Build PDF appeal letter from intake + draft (citation, statement, signature).
- Verify/standardize address via Lob US verification; if invalid, do not send — log for manual handling.
- Create letter via Lob (certified or standard per product); store Lob letter ID and tracking in DB.
- Idempotent: same intake/draft IDs must not trigger duplicate sends.

**Config:** `LOB_API_KEY`, `LOB_MODE`. PDF template deterministic; include disclaimer and signature.

---

## Email Notifications (SendGrid)

- Send confirmation and status emails after payment success and (optionally) mail sent.
- Sender: `SERVICE_EMAIL`; reply/support: `SUPPORT_EMAIL`. Links use `APP_URL`.
- Do not crash webhook on email failure; log and optionally retry; avoid duplicate sends via idempotency.

---

## Admin Endpoints

- Mount under `/admin`; protect with auth (token, API key, or IP allowlist) and rate limiting.
- Return structured JSON with request ID; no PII beyond operational need; paginate lists.

---

## Health, Readiness & Observability

- **Endpoints:** `/health` (liveness), `/health/ready` (DB connectivity), `/health/detailed` (counts + dependency status).
- **Logging:** JSON by default, `request_id` and timestamps; respect `LOG_LEVEL`.
- **Sentry:** Optional; enable with `SENTRY_DSN`; tag environment.

---

## Frontend Architecture (Next.js 15)

**Stack:** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS.

**Structure**
- Root layout, `providers.tsx` (e.g. appeal context), `globals.css`, `error.tsx`, `global-error.tsx`, `not-found.tsx`.
- **Routes:** `page.tsx` (home), `[city]/page.tsx`, `appeal/page.tsx`, `appeal/camera`, `appeal/review`, `appeal/signature`, `appeal/checkout`, `appeal/status`, `success`, `blog`, `blog/[slug]`, `terms`, `privacy`, `refund`, `what-we-are`, `contact`.
- Tailwind everywhere; client components where interactivity needed.

---

## Frontend Appeal Flow (User Journey)

1. **Home:** Citation input → validate → city detection.
2. **City page:** City-specific landing, eligibility, CTA to appeal.
3. **Appeal:** Contact + citation basics.
4. **Camera:** Photo capture/upload for citation.
5. **Review:** Statement edit + AI refinement display (with fallback if AI fails).
6. **Signature:** Capture and store.
7. **Checkout:** Call backend for session URL → redirect to Stripe.
8. **Success:** Post-checkout confirmation.
9. **Status:** Lookup by tracking ID.

**UX rules:** Disclaimers on every decision step; blocked-state messaging early; preserve state on refresh (sessionStorage); checkout errors show retry without losing state.

---

## Frontend State & Data Layer

- **Appeal context:** React context + reducer; persist to sessionStorage on each update; hydrate from storage so state survives refresh.
- **API client:** Fetch wrapper with retries (exponential backoff), timeouts, JSON parse; base URL from `NEXT_PUBLIC_API_BASE`; throw on non-2xx.
- **City/route data:** Registry (e.g. `cities.ts`, `city-routing.ts`) in sync with backend city IDs.

---

## Frontend Integrations

- **OCR:** Tesseract.js to extract citation from uploaded images; normalize for validation.
- **Google Places:** Address autocomplete component; emit structured address to form; use only on client to avoid SSR issues.
- **Stripe (client):** Checkout page gets session URL from backend and redirects; publishable key from env.
- **AI:** Review page calls `/statement/refine` and shows original + refined with fallback.

---

## Frontend Compliance UX

- **Components:** LegalDisclaimer (variants: full, compact, inline, elegant), FooterDisclaimer, ErrorBoundary.
- **Usage:** Show disclaimer on all user decision points (home, city, appeal steps, checkout). Blocked states: clear message and prevent progression; wording = “document preparation, not legal advice.”

---

## SEO & Content

- Blog index and `blog/[slug]`; content from markdown or data (e.g. `content/blog/*.md`, `data/seo/*.csv`).
- `sitemap.ts` and `robots.ts`; metadata (title, description) per page via Next.js metadata.
- Keep slugs and sitemap in sync with routes.

---

## Testing & QA

**Automated**
- Backend: `pytest` (e.g. `docker compose exec api pytest`).
- Integration: e2e test for critical flow (e.g. `tests/test_e2e_integration.py`).
- Frontend: Jest (e.g. `npm test`); unit tests for API client and appeal context.

**Manual checklist**
- Citation validation (valid/invalid, blocked states).
- AI refinement (success + fallback).
- Full appeal flow + refresh mid-flow (state persists).
- Checkout (session, cancel, success redirect).
- Webhook: simulate `checkout.session.completed` → PDF/mail/email.
- Status lookup (valid vs unknown ID).
- Disclaimers and blocked-state messaging on all relevant pages.
- Health endpoints and request IDs in logs.

---

## Tooling, Dev & Deploy

**Local**
- Docker + Docker Compose; `cp .env.example .env`, fill secrets, `docker compose up --build`.
- Optional: frontend `npm run dev`, backend uvicorn with `.env`.

**Services (Compose):** `api` (8000), `web` (3000), `db` (5432), `nginx` (80/443). Env file mounted to api and web.

**Scripts:** Deploy, firewall, SSL, Stripe helpers, diagnostics as needed. Preserve service names/ports for nginx.

---

## Infrastructure & Nginx

- **Role:** Reverse proxy; terminate HTTP/HTTPS; route to web (Next.js) and API (FastAPI).
- **Routing:** `/` → frontend (port 3000); `/api` or chosen prefix → backend (8000); health routes to API.
- **SSL:** e.g. Let’s Encrypt via deploy script; nginx server blocks for 80/443.
- **Extras:** Maintenance page, static asset caching (long max-age for assets, not HTML), gzip and security headers, optional admin IP allowlist.

---
ASSssssssssss
