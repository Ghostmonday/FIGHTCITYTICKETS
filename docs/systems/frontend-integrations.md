# Frontend Integrations

Purpose: describe client-side integrations with external services and helpers.

## OCR
- File: `frontend/app/lib/ocr-helper.ts`.
- Uses Tesseract.js to extract citation numbers from uploaded images.
- Provides helpers to clean/normalize extracted text for validation step.

## Google Places Autocomplete
- Component: `frontend/components/AddressAutocomplete.tsx`.
- Uses `NEXT_PUBLIC_GOOGLE_PLACES_API_KEY`.
- Emits structured address (street, city, state, zip) back to parent forms.

## Stripe (client)
- Used in `appeal/checkout/page.tsx`.
- Receives Checkout Session URL from backend; redirects via `window.location`.
- Publishable key from env; ensure it matches backend secret environment.

## AI surface
- `appeal/review/page.tsx` calls backend refine endpoint and displays both original and refined text with fallback handling.

## Rebuild checklist
- Load external scripts (e.g., Places) only on client where needed to avoid SSR issues.
- Handle permission/camera for OCR/photo capture gracefully with fallbacks.
- Keep environment variables prefixed with `NEXT_PUBLIC_` for exposure.
