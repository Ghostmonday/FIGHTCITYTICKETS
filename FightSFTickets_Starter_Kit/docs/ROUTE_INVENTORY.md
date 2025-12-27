# Route Inventory - FightCityTickets.com

Complete inventory of all user-accessible routes, links, and navigation paths.

## Frontend Routes

### Public Pages
- `/` - Home page (citation validation form)
- `/privacy` - Privacy policy
- `/terms` - Terms of service

### City-Specific Pages
- `/[city]` - Dynamic city pages (e.g., `/sf`, `/la`, `/nyc`)
  - `/sf` or `/SF` - San Francisco
  - `/san_francisco` - San Francisco (slug format)
  - `/la` or `/LA` - Los Angeles
  - `/los_angeles` - Los Angeles (slug format)
  - `/nyc` or `/NYC` - New York City
  - `/chicago` - Chicago
  - `/seattle` - Seattle
  - `/phoenix` - Phoenix
  - `/denver` - Denver
  - `/dallas` - Dallas
  - `/houston` - Houston
  - `/philadelphia` - Philadelphia
  - `/portland` - Portland
  - `/san_diego` - San Diego
  - `/salt_lake_city` - Salt Lake City

### Appeal Flow Pages
- `/appeal` - Appeal landing page (requires citation/city params)
- `/appeal/camera` - Photo upload step
- `/appeal/review` - Review appeal letter
- `/appeal/signature` - Signature step
- `/appeal/checkout` - Payment checkout

### Admin Pages
- `/admin` - Admin dashboard (requires authentication)

## Backend API Routes

### Health & Status
- `GET /api/health` - API health check
- `GET /health` - Health endpoint
- `GET /api/webhook/health` - Webhook health check

### Citation & Tickets
- `POST /api/tickets/validate` - Validate citation number
- `GET /api/tickets` - List ticket types (deprecated)
- `GET /api/tickets/citation/{citation_number}` - Get citation info

### Statement Refinement
- `POST /api/statement/refine` - Refine appeal statement using AI
- `POST /api/statement/polish` - Polish statement (deprecated)

### Checkout & Payment
- `POST /api/checkout/create-session` - Create Stripe checkout session
- `GET /api/checkout/session/{session_id}` - Get session status
- `POST /api/checkout/test-checkout` - Test checkout endpoint

### Webhooks
- `POST /api/webhook/stripe` - Stripe webhook handler
- `POST /api/webhook/retry-fulfillment/{session_id}` - Retry fulfillment

### Admin API
- `GET /api/admin/stats` - System statistics
- `GET /api/admin/activity` - Recent activity log
- `GET /api/admin/intake/{intake_id}` - Get intake details
- `GET /api/admin/logs` - System logs

## Navigation Links

### Footer Links (on all pages)
- Privacy Policy → `/privacy`
- Terms of Service → `/terms`

### Home Page Links
- City detection → Auto-redirects to `/[detected_city]`
- Citation validation form → Stays on `/` or redirects to `/appeal`

### City Page Links
- "Continue to Appeal" button → `/appeal?city={city}&citation={citation}`
- Citation validation → Stays on `/[city]` page

### Appeal Flow Navigation
- Step 1: Camera → `/appeal/camera`
- Step 2: Review → `/appeal/review`
- Step 3: Signature → `/appeal/signature`
- Step 4: Checkout → `/appeal/checkout`

## User Flows

### Flow 1: Citation Validation → Appeal
1. User visits `/` or `/[city]`
2. Enters citation number
3. Clicks "Validate Citation"
4. If valid, clicks "Continue to Appeal"
5. Redirects to `/appeal?city={city}&citation={citation}`
6. Proceeds through appeal steps

### Flow 2: Direct City Access
1. User visits `/[city]` directly
2. Sees city-specific information
3. Can validate citation
4. Can start appeal process

### Flow 3: Home → Auto-Detection
1. User visits `/`
2. System detects location
3. Auto-redirects to `/[detected_city]` after 2 seconds

### Flow 4: Complete Appeal Process
1. `/appeal` - Landing page
2. `/appeal/camera` - Upload photos
3. `/appeal/review` - Review appeal letter
4. `/appeal/signature` - Sign appeal
5. `/appeal/checkout` - Payment
6. `/success` - Success page (if exists)

## State Dependencies

### Appeal Flow State
- `/appeal` requires: `city` and `citation` query params
- `/appeal/camera` requires: Appeal context (citation, city)
- `/appeal/review` requires: Photos uploaded
- `/appeal/signature` requires: Appeal letter reviewed
- `/appeal/checkout` requires: Signed appeal

### Admin State
- `/admin` requires: `X-Admin-Secret` header or `ADMIN_SECRET` env var

## Query Parameters

### Appeal Pages
- `city` - City identifier (e.g., `sf`, `us-ca-san_francisco`)
- `citation` - Citation number

### Optional Parameters
- `skip_city_redirect` - Skip auto-redirect on home page (sessionStorage)

## Expected Status Codes

### Frontend Routes
- `200` - Page loads successfully
- `302` - Redirect (acceptable for appeal flow)
- `404` - Page not found (should not occur)

### API Routes
- `200` - Success
- `400` - Bad request (validation errors)
- `401` - Unauthorized (admin routes)
- `403` - Forbidden
- `404` - Not found
- `500` - Server error (should not occur in production)

## Test Coverage Requirements

### Must Test
- ✅ All frontend routes load without errors
- ✅ All API endpoints respond correctly
- ✅ Navigation links work
- ✅ State transitions are smooth
- ✅ Query parameters are handled correctly
- ✅ Error states are handled gracefully
- ✅ Redirects work as expected
- ✅ Forms submit correctly
- ✅ API calls succeed/fail appropriately

### Edge Cases
- Invalid city slugs
- Missing query parameters
- Invalid citation numbers
- Network errors
- API failures
- Authentication failures

---

*Last Updated: 2025-12-26*
*Total Routes: 30+ frontend, 15+ API*

