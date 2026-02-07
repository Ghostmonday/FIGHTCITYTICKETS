# Statement Refinement (AI)

Purpose: describe AI-assisted appeal text generation with UPL safeguards.

## Responsibilities
- Accept user-provided statement and context.
- Call DeepSeek API to refine language while preserving user voice and facts.
- Enforce UPL constraints (no legal advice, no evidence recommendations).
- Handle retries/timeouts and return safe fallbacks.

## Key files
- `backend/src/routes/statement.py` — `POST /statement/refine`.
- `backend/src/services/statement.py` — DeepSeek integration, prompt construction, safety filters.
- `frontend/app/appeal/review/page.tsx` — UI call site and display of refined text.

## Flow
1. User writes statement; client sends to `/statement/refine` with citation context.
2. Service builds prompt with constraints and city rules; calls DeepSeek.
3. Response is sanitized and trimmed; profanity or risky content should be filtered.
4. If AI fails, return user’s original text with error flag for UI.

## Config / env
- `DEEPSEEK_API_KEY`
- Timeouts and max tokens set in service defaults (respect production-safe values).

## Safety
- Guardrails in prompt to avoid legal advice.
- Error handling returns safe fallback (no nulls).
- Circuit breaker (middleware/resilience) protects upstream from repeated failures.

## Rebuild checklist
- Mirror prompt instructions and safety filters.
- Implement retries with backoff and total timeout.
- Preserve user tone; avoid adding evidence or admissions.
