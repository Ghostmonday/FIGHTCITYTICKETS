# Frontend Build Prompt: Fight City Tickets

Build a complete, production-ready frontend for **Fight City Tickets** — a UPL-compliant parking ticket appeal document preparation service. This frontend must integrate seamlessly with an existing FastAPI backend.

---

## 🎯 BUILD SCOPE (Important!)

**What YOU Build**: Complete React frontend UI/UX with **mock API calls**. All pages, components, styling, forms, state management, validation, and user flows.

**What I Handle After**: Integrating the real FastAPI backend endpoints, wiring Supabase Storage for photo uploads, adding Vite config, and deploying to Vercel/Netlify.

**Your Job**: Give me a fully styled, functional frontend with mock/stub API responses. Make it look production-ready and work with mock data. I'll replace your mocks with real backend calls.

---

## ⚡ Quick Clarifications

**Build Scope**: You build the complete UI/UX with mock API calls. I'll integrate the real FastAPI backend + Supabase Storage afterward.

**Tech Stack**: **React 18.2.0 + Vite + JavaScript** (NOT Next.js/TypeScript). Use React Router 6.16.0, TailwindCSS + shadcn/ui, React Context API (instead of Zustand), custom fetch hooks (instead of TanStack Query).

**Backend Integration (for reference)**: FastAPI backend exists on port 8000. You'll use mock responses; I'll wire real endpoints after. Backend can use Supabase PostgreSQL but currently uses standard PostgreSQL.

**Supabase Storage (for reference)**: I'll integrate Supabase for photo uploads after you build the UI. You just need: photo upload component with previews, validation (2–5 photos, JPG/PNG, 8MB max), store URLs in state. I'll add the Supabase upload logic.

**Stripe Integration (for reference)**: I'll handle Stripe Checkout redirect. You build: checkout page with $39 display, attestation checkbox, "Proceed to Payment" button. I'll wire the redirect.

**Design Aesthetic**: Modern, minimalist (Stripe + Notion vibe). Subtle animations only. No heavy gradients or flashy effects. Focus on clarity and conversion.

**Dark Mode**: Nice-to-have, user-selectable toggle. Light mode is default.

**Photo Upload & Signature**:
- Photos: Upload component with previews, 2–5 validation, JPG/PNG only, 8MB max. Store URLs in state (I'll add Supabase upload).
- Signature: Canvas with clear/redraw, auto-save to sessionStorage (debounced), mobile-optimized touch targets.

---

## 🎯 Project Overview

**Service**: Document preparation for parking ticket appeals (NOT legal advice)
**Brand**: "Fight City Tickets" (short form: "Fight City")
**Pricing**: $39 flat fee for document preparation and mailing
**Compliance**: Heavily UPL-safe with disclaimers everywhere

### Supported Cities
- San Francisco, CA (`us-ca-san_francisco`)
- Los Angeles, CA (`us-ca-los_angeles`)
- New York City, NY (`us-ny-new_york`)
- Chicago, IL (`us-il-chicago`)
- Seattle, WA (`us-wa-seattle`)

### Blocked States (UPL Restrictions)
Display "Service not available in your state" for: **TX, NC, NJ, WA**

---

## 🎨 Design
Stripe + Notion vibe: clean, minimal, no legal imagery. Colors: #DC2626 (CTAs), #111827 (text), #6B7280 (secondary), #F9FAFB (bg), #10B981 (success). Inter font. Tailwind + shadcn/ui. Mobile-first. Dark mode optional (light default). Subtle animations.

---

## 🔄 User Flow
1. **Home**: Hero "Got a Parking Ticket? Fight City Can Help You Prepare Your Appeal", CTA "Start Your Appeal", compact disclaimer.
2. **City**: List cities (SF, LA, NYC, Chicago, Seattle); block TX/NC/NJ/WA; disclaimer.
3. **Intake**: Citation (validate via API), vehicle details, 2–5 photos (Supabase), email/phone, address (Places proxy); address warning if undeliverable, allow proceed.
4. **Review**: Show all input; statement textarea; "Refine with AI" (API); signature canvas (clear/redraw, sessionStorage); edit links.
5. **Checkout**: $39; Stripe redirect (create-appeal-checkout → checkout_url); required UPL checkbox; "Proceed to Payment".
6. **Success**: clerical_id, confirmation, email stub, tracking link (certified only).

---

## 🔌 Backend Integration (For Reference - Use Mocks For Now)

**Note**: Build the UI with mock API responses. I'll replace with real FastAPI calls after.

**Base URL (for later)**: `VITE_API_URL` or `http://localhost:8000`

**Mock these endpoints**:
- `POST /api/tickets/validate` — Body: `citation_number`, optional `city_id`, `violation_date`, `license_plate`. Response: `is_valid`, `citation_number`, `agency`, `deadline_date`, `days_remaining`, `is_past_deadline`, `is_urgent`, `error_message`, `city_id`, `section_id`, `city_mismatch`, `selected_city_mismatch_message`
- `POST /api/appeals` — Body: citation_number, violation_date, vehicle_info, license_plate, appeal_reason, user_name, user_address_line1/2, user_city/state/zip, user_email/phone, city. Response: `message`, `intake_id`, `citation_number`
- `PUT /api/appeals/{intake_id}` — Same body fields (all optional). Response: `message`, `intake_id`, `updated_at`
- `POST /api/statement/refine` — Body: `original_statement`, optional citation_number, citation_type, desired_tone, max_length. Response: `status`, `original_statement`, `refined_statement`, `improvements`, `error_message`, `method_used`
- `POST /api/checkout/create-appeal-checkout` — Body: `citation_number`, `city_id`, optional section_id, user_email, **user_attestation: true**. Response: `checkout_url`, `session_id`, `amount` (cents), `clerical_id`
- `GET /api/checkout/session-status?session_id=` — Response: `status`, `payment_status`, `mailing_status`, `tracking_number`, `expected_delivery`, `clerical_id`
- `GET /api/places/autocomplete?input=&session_token=` — Google Places predictions
- `GET /api/places/details?place_id=&session_token=` — Address components
- `POST /api/status/lookup` — Body: `email`, `citation_number`. Response: citation_number, payment_status, mailing_status, tracking_number, amount_total, appeal_type, payment_date, mailed_date

---

## 📦 Supabase Integration (For Reference - I'll Wire After)

**Note**: Build the photo upload UI without Supabase integration. I'll add Supabase Storage after.

**What you build**: `PhotoUpload` component with file select, previews, validation (type/size/count), remove/replace, store URLs array in state.

**What I'll add later**: Supabase client init, upload logic, public URL generation. Just make the UI work with mock photo URLs for now.

| Location | What to do |
|----------|------------|
| **`src/lib/supabase.js`** | Create and export the Supabase client: `createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_ANON_KEY)`. Single place that reads env; all other code imports this client. |
| **`src/hooks/useSupabase.js`** (or inline in component) | Optional hook: `uploadTicketPhoto(file)` → uploads to bucket, returns public URL. Uses `supabase.storage.from(bucket).upload(path, file)` then `getPublicUrl(path)`. Bucket name from `import.meta.env.VITE_SUPABASE_STORAGE_BUCKET` (default `ticket-photos`). Generate path like `{intakeIdOrSessionId}/{timestamp}_{filename}` to avoid collisions. |
| **`src/components/PhotoUpload.jsx`** | **Where uploads happen.** On file select: validate type (JPG/PNG), size (≤8MB), count (2–5). Call upload (from hook or lib) for each file; collect array of public URLs. Store URLs in parent state or AppealContext (e.g. `photoUrls: string[]`). Show preview thumbnails and remove/replace. Do NOT send file blobs to the backend. |
| **`src/pages/AppealIntake.jsx`** | **Where PhotoUpload is used.** Render `<PhotoUpload value={photoUrls} onChange={setPhotoUrls} />` (or pass from AppealContext). Ensure photoUrls are in the same state/context as other intake fields (citation, vehicle, contact, address). |
| **`src/context/AppealContext.jsx`** | Hold `photoUrls` (array of strings) in appeal state. Persist to sessionStorage if you persist other intake fields. When restoring, only URLs are needed (no re-upload). |
| **`src/lib/api-client.js`** (or wherever you call backend) | **Where URLs are sent to backend.** In `createAppeal` and `updateAppeal`, include **`selected_evidence`** in the request body as an array of photo URL strings (backend field name). Backend stores these in DB; no Supabase call on backend. |
| **Backend** | No Supabase SDK. Intake model uses **`selected_evidence`** (list) for photo URLs. POST/PUT `/api/appeals` and `/api/appeals/{id}` already accept `selected_evidence`; just send the Supabase public URLs array. |

**One-time setup**: Supabase Dashboard → Storage → create bucket `ticket-photos`, set **Public**, file size limit 8MB. Add env in `.env`: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_SUPABASE_STORAGE_BUCKET=ticket-photos`.

**Flow summary**: User selects photos in AppealIntake → PhotoUpload validates and uploads each to Supabase Storage → URLs stored in AppealContext/state → on submit, api-client sends those URLs as **`selected_evidence`** in createAppeal/PUT appeal → backend saves URLs only.

---

## 🛡️ UPL Compliance (Critical!)
**Full** (checkout/success): "Document preparation only. Not a law firm; no legal advice. No attorney-client relationship. No outcome guarantees. User responsible for filing. Consult an attorney for legal advice."
**Compact** (home/city): "Document preparation only — not legal advice."
**Inline** (every step): "This is not legal advice."
**Blocked**: "We cannot process appeals for tickets in this state due to legal restrictions."
**Language**: Use "prepare your appeal", "document preparation"; never "win your case", "legal representation", "guaranteed dismissal".

---

## 🏗️ Tech Stack
**React 18.2 + Vite + JavaScript** (.jsx/.js). React Router 6.16. React Context + sessionStorage. Custom fetch hooks with retry. **Stripe Checkout redirect**: POST create-appeal-checkout → redirect to checkout_url → return /success?session_id=; no Stripe key. **Supabase Storage**: upload to `ticket-photos`, getPublicUrl, send URLs to backend; 2–5 photos, JPG/PNG 8MB, previews. SEO: React Helmet, sitemap, robots.

---

## 📁 Folder Structure (React + Vite)

`src/`: App.jsx, main.jsx; `pages/` (Home, CitySelection, AppealIntake, Review, Checkout, Success, Status); `components/` (ui/, AppealForm, CitationValidator, PhotoUpload, SignatureCanvas, StatementRefiner, CheckoutForm, DisclaimerText); `context/` AppealContext; `hooks/` useApi, useSupabase; `lib/` api-client.js, supabase.js, utils.js. Root: .env.example, vite.config.js, package.json, tailwind.config.js.

---

## 🚀 Deployment & Environment

### Env & Deploy
**Env**: VITE_API_URL, VITE_APP_URL, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_SUPABASE_STORAGE_BUCKET=ticket-photos. No Stripe key. Deploy: Vercel/Netlify, `npm run build` → dist/, set VITE_* in platform. Deps: react 18.2, react-router-dom 6.16, @supabase/supabase-js, tailwind, vite, @vitejs/plugin-react.

---

## 🎯 Edge Cases
- Citation: if city_mismatch show selected_city_mismatch_message; if is_past_deadline show urgent warning but allow proceed.
- Address: if undeliverable show "Address may be invalid" + "I confirm" checkbox; allow proceed.
- Payment: handle 409 (duplicate citation); user-friendly errors.
- Photos: validate type/size client-side; previews; toasts for errors.
- API: retry with backoff; toasts for transient errors; fallback if AI refinement down.

---

## ✅ Deliverables
All pages (home, city, intake, review, checkout, success, status). All components (forms, buttons, photo upload UI, signature canvas). React Context + sessionStorage. **Mock API calls** (I'll wire real backend). Tailwind styling, mobile-first, dark mode optional. UPL disclaimers everywhere. Error/loading states, toasts. Form validation. .env.example (with mock values), README.

**Key**: Make it visually complete and functionally testable with mock data. I'll handle backend + Supabase + deployment config.

---

## 🚦 Getting Started Instructions

### Setup
Node 18+. Create Vite+React: `npm create vite@latest frontend2 -- --template react`. Install: react-router-dom, tailwindcss, shadcn/ui. **Use mock API calls** — I'll wire real backend after. .env.example: VITE_API_URL (for later), VITE_APP_URL. `npm run dev` → localhost:5173.

### Mock API Responses (Build With These)
- `validateCitation`: `{is_valid: true, citation_number, city_id, days_remaining: 21}`
- `createAppeal`: `{intake_id: 1, message: "success"}`
- `createCheckout`: `{checkout_url: "/mock-checkout", session_id: "mock_123", clerical_id: "ND-MOCK-1234"}`
- `refineStatement`: `{status: "success", refined_statement: "...", original_statement: "..."}`
- `sessionStatus`: `{status: "complete", payment_status: "paid", clerical_id: "ND-MOCK-1234"}`

### Testing & Deploy
Test: backend up, full flow city→checkout→success, Stripe test card 4242... Deploy: build → dist; Vercel/Netlify; set VITE_*; Supabase bucket public.

---

## 💡 Recommendations
Lazy-load photos/signature; prefetch API; ARIA labels, keyboard nav; auto-save to sessionStorage; stepper progress. Optional: PDF preview, i18n, referral, live chat.

## 📝 Notes
**You build**: UI with mocks. Photo upload component (store mock URLs in state). Checkout page (mock redirect). All styling, forms, validation, state management.

**I handle after**: Real FastAPI endpoints, Supabase Storage upload, Stripe redirect, deployment. Show `clerical_id` (ND-XXXX-XXXX) on success. Block TX/NC/NJ/WA. UPL disclaimers mandatory. Signature: clear/redraw, sessionStorage debounced, 44px touch targets.

---

## 🎉 Final Output
Complete React + Vite app: all pages/components, production-ready UI/UX, Tailwind + shadcn/ui, mobile-first, **mock API calls**, full error handling, README. Beautiful, fast, UPL-compliant. **I'll integrate the real backend, Supabase Storage, and deployment after you deliver the UI.** Start building now!
