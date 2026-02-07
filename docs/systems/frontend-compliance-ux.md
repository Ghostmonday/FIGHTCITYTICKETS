# Frontend Compliance UX

Purpose: ensure UPL compliance messaging and state restrictions are consistently presented.

## Components
- `frontend/components/LegalDisclaimer.tsx` — multiple variants (full, compact, inline, elegant) for different placements.
- `frontend/components/FooterDisclaimer.tsx` — footer copy with compliance text.
- `frontend/components/ErrorBoundary.tsx` — keeps app stable while showing helpful messaging.

## Usage expectations
- Show disclaimer on all user decision points (home, city pages, appeal steps, checkout).
- For blocked states, display clear messaging and prevent progression (align with backend block list).
- Keep wording aligned with “document preparation, not legal advice.”

## Styling/behavior
- Tailwind-based styling; variants chosen by props.
- Minimal interactivity; meant to be static informative text.

## Rebuild checklist
- Reuse same copy across pages; ensure localization-ready if expanded.
- Double-check state block messages appear both in UI and backend validation.
