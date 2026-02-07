# Frontend Appeal Flow

Purpose: detail the user journey across appeal pages and the data passed between them.

## Steps (pages)
- `app/page.tsx` — homepage: citation input, city detection.
- `app/[city]/page.tsx` — city-specific landing, eligibility, CTA into appeal.
- `app/appeal/page.tsx` — appeal intro, gathers contact + citation basics.
- `app/appeal/camera/page.tsx` — photo capture/upload (for citation images).
- `app/appeal/review/page.tsx` — statement editing and AI refinement display.
- `app/appeal/signature/page.tsx` — signature capture.
- `app/appeal/checkout/page.tsx` — initiates Stripe checkout via API.
- `app/appeal/status/page.tsx` — status lookup by tracking ID.
- `app/success/page.tsx` — post-checkout confirmation (if present in success folder).

## Data handoff
- Appeal context (sessionStorage) carries citation, contact, photos, refined statement, signature, intake/draft IDs.
- API client used on each step to persist updates (`/appeals` endpoints) and to start checkout.

## UX rules
- Always surface legal disclaimers on pages with user decisions.
- Show city/blocked-state messaging early.
- On AI failure, keep user text and show fallback notice.
- Checkout errors show retry CTA; do not lose state.

## Rebuild checklist
- Keep same route structure to match backend assumptions for redirects.
- Persist partial data frequently to avoid loss on refresh.
- Use optimistic UI but confirm with backend responses before advancing critical steps (checkout).
