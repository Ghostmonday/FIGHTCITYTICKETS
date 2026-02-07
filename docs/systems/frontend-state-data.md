# Frontend State & Data Layer

Purpose: explain how client state is managed and how API calls are made.

## Responsibilities
- Maintain appeal state across pages using React context + sessionStorage.
- Provide a resilient API client with retries/backoff.
- Normalize city/route data for navigation.

## Key files
- `frontend/app/lib/appeal-context.tsx` — React context, reducer, persistence to sessionStorage; tests in `appeal-context.test.tsx`.
- `frontend/app/lib/api-client.ts` — fetch wrapper with retries, timeouts, and JSON parsing; tests in `api-client.test.ts`.
- `frontend/app/lib/cities.ts`, `city-routing.ts`, `california-cities.ts` — registry for cities and routes.
- `frontend/app/lib/config.ts` — base URLs/env-aware config.

## State persistence
- On each update, context writes to sessionStorage to survive reloads.
- Hydration reads from storage, validates shape, and populates context.

## API client behavior
- Retries with exponential backoff on network/server errors.
- Timeouts to avoid hanging requests.
- JSON response parsing with error throwing on non-2xx.
- Base URL from `NEXT_PUBLIC_API_BASE` (or config helper).

## Rebuild checklist
- Mirror reducer shape and storage keys so data survives navigation.
- Keep retry/backoff parameters sensible for frontend (short total timeout).
- Always include request ID headers from backend if exposed for debugging.
