# Tooling, Dev & Deploy

Purpose: describe how to build/run locally and deploy with provided scripts.

## Local development
- Requirements: Docker + Docker Compose, Node 20+, Python 3.12.
- Quick start: `cp .env.example .env`, fill secrets, `docker compose up --build`.
- Frontend dev: `cd frontend && npm install && npm run dev` (if running separately).
- Backend dev: run FastAPI with uvicorn using env from `.env`.

## Commands (from README)
- Backend tests: `docker compose exec api pytest`
- Integration: `docker compose exec api pytest tests/test_e2e_integration.py`
- Frontend tests: `cd frontend && npm test`

## Scripts
- Deploy: `scripts/deploy-fightcity.sh`
- Security hardening: `scripts/deploy-security.sh`
- Firewall/SSL: `scripts/setup-firewall.sh`, `scripts/setup-ssl.sh`
- Stripe helpers: `scripts/stripe_*` series for setup and credentials.
- Diagnostics: `scripts/diagnostics/*`

## Config files
- `docker-compose.yml` — services: api (8000), web (3000), db (5432), nginx (80/443).
- `frontend/Dockerfile`, `frontend/nixpacks.toml`, `frontend/Dockerrun`.
- Lint/format: `.eslintrc.json`, `.prettierrc.json`, `tailwind.config.js`.

## Rebuild checklist
- Preserve service names/ports so nginx config matches.
- Ensure env file mounted to both api and web containers.
- Set healthcheck endpoints for orchestrators if needed.
