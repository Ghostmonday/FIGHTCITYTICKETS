# FightSFTickets (Skeleton Workspace)

This repository is a **project skeleton** intended for an AI agent (e.g., DeepSeek) to flesh out into a complete, runnable system.

## What you should see at the root
- `backend/` — FastAPI service skeleton (Python)
- `frontend/` — Next.js web app skeleton (TypeScript)
- `infra/` — Docker + infrastructure scaffolding
- `scripts/` — helper scripts
- `credentials/` — **you will place your credential file(s) here**
- `docs/` — operator + AI handoff docs generated for this skeleton
- `miscellaneous/` — **everything that existed in the original folder** (untouched)

## Quick start (developer)
### With Docker
```bash
docker compose up --build
```

### Without Docker
Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Credentials
Place your credential file(s) in:
- `credentials/` (recommended name: `service_account.json`)

Then copy/rename `.env.example` → `.env` and fill in paths/values.

Generated on 2025-12-20.
