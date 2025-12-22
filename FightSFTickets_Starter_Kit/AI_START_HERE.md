# AI Start Here (authoritative)

## Objective
Turn this skeleton into a **complete FightSFTickets project**:
- runnable locally (docker + non-docker),
- clear module boundaries,
- tests and CI scaffolding,
- production-ready configuration patterns (12-factor style),
- safe handling of credentials (never commit secrets).

## Constraints
- Do **not** modify anything under `miscellaneous/` except to read it for context.
- Do **not** invent secrets. Use `.env` and `credentials/` paths.
- Keep API contracts stable once defined; document changes.

## What to do first
1. Read `docs/DEEPSEEK_HANDOFF.md`.
2. Scan `miscellaneous/original_project_dump/` to understand intent and existing content.
3. Implement missing code iteratively:
   - backend endpoints + services + persistence
   - frontend pages + components + API integration
   - infra polish (docker, healthchecks)
4. Keep an updated task list in `docs/TASK_QUEUE.md`.

## How to run
- Docker: `docker compose up --build`
- Backend only: `cd backend && uvicorn src.app:app --reload --port 8000`
- Frontend only: `cd frontend && npm run dev`
