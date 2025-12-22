# Task Queue

## Current Sprint: SF City Flow Implementation

> **Goal**: Complete intake → payment → mail output flow
> **Timeline**: 6 weeks
> **Last Updated**: January 2025

---

## 🔴 In Progress

### TASK-106: Lob Mail Service
**Priority**: HIGH
**Estimated Effort**: 6 hours
**Files to Create**: `backend/src/services/mail.py`

**Requirements**:
- [ ] Generate appeal PDF (letter + photos + metadata)
- [ ] Send via Lob API (standard or certified)
- [ ] Route to correct SFMTA address
- [ ] Return tracking info

**Acceptance Criteria**:
- [ ] PDF includes: letter text, selected photos, signature, timestamp
- [ ] Standard mail: ~$1, Certified: ~$10.50
- [ ] Returns Lob tracking ID

**Reference**: `miscellaneous/original_project_dump/FightSFTickets_CODE_POLISHED/backend_lob_service.txt`

---

## 📋 Backlog - Phase 1: Backend Core Services (Week 1-2)

### TASK-101: Citation Validation Service
**Status**: ✅ COMPLETED
**Completed**: January 2025
**Files Created**: `backend/src/services/citation.py`

**Requirements**:
- [x] Validate SF citation number format (9-digit starting with 9)
- [x] Calculate 21-day appeal deadline from violation date
- [x] Return agency routing info (SFMTA vs other)
- [x] Check if citation is within appeal window

**Acceptance Criteria**:
- [x] Valid citations return `{valid: true, deadline: date, agency: "SFMTA"}`
- [x] Invalid format returns clear error message
- [x] Expired deadline returns `{valid: false, reason: "deadline_passed"}`

**Reference**: `miscellaneous/original_project_dump/FightSFTickets_CODE_POLISHED/backend_api_service.txt`

---

### TASK-102: Stripe Checkout Integration
**Status**: ✅ COMPLETED
**Completed**: January 2025
**Files to Modify**: `backend/src/routes/checkout.py`
**Files to Create**: `backend/src/services/stripe_service.py`

**Requirements**:
- [x] Create Stripe checkout session with appeal metadata
- [x] Support two price tiers: Standard ($9) and Certified ($19)
- [x] Embed all appeal data in session metadata for webhook retrieval
- [x] Handle success/cancel redirects

**Acceptance Criteria**:
- [x] `POST /checkout/create-session` returns Stripe URL
- [x] Metadata includes: citation_number, user_info, appeal_reason
- [x] Works with both test and live Stripe keys

**Reference**: `miscellaneous/original_project_dump/FightSFTickets_CODE_POLISHED/backend_checkout.txt`

---

### TASK-103: Stripe Webhook Handler
**Status**: ✅ COMPLETED
**Completed**: January 2025
**Files Created**: `backend/src/routes/webhooks.py`

**Requirements**:
- [x] Verify Stripe webhook signature
- [x] Handle `checkout.session.completed` event
- [x] Extract appeal data from session metadata
- [ ] Trigger mail fulfillment on successful payment

**Acceptance Criteria**:
- [x] Invalid signatures rejected with 400
- [ ] Valid payments trigger Lob mail service
- [x] Idempotent: duplicate webhooks don't double-send

---

### TASK-104: DeepSeek Statement Refinement
**Status**: ✅ COMPLETED
**Completed**: January 2025
**Files to Create**: `backend/src/services/statement.py`

**Requirements**:
- [x] Call DeepSeek API with user transcript
- [x] Use UPL-compliant system prompt (no legal advice)
- [x] Return professionally formatted appeal letter
- [x] Fallback to basic formatting if API unavailable

**Acceptance Criteria**:
- [x] Informal input → formal letter output
- [x] No legal advice language in output
- [x] Graceful degradation on API failure

**Reference**: `miscellaneous/original_project_dump/FightSFTickets_CODE_POLISHED/backend_appeal_generator.txt`

---

### TASK-105: OpenAI Whisper Transcription
**Status**: ✅ COMPLETED
**Completed**: January 2025
**Files to Create**: `backend/src/services/transcription.py`

**Requirements**:
- [x] Accept audio file upload (webm, mp3, wav, m4a)
- [x] Call OpenAI Whisper API for transcription
- [x] Return text transcript
- [x] Enforce 2-minute max duration

**Acceptance Criteria**:
- [x] `POST /api/transcribe` accepts audio file
- [x] Returns `{transcript: "text", duration_seconds: number}`
- [x] Rejects files over 2 minutes

---

### TASK-106: Lob Mail Service
**Status**: 🔴 IN PROGRESS
**Estimated Effort**: 6 hours
**Files Created**: `backend/src/services/mail.py`

**Requirements**:
- [x] Generate appeal PDF (letter + photos + metadata)
- [x] Send via Lob API (standard or certified)
- [x] Route to correct SFMTA address
- [x] Return tracking info

**Acceptance Criteria**:
- [x] PDF includes: letter text, selected photos, signature, timestamp
- [x] Standard mail: ~$1, Certified: ~$10.50
- [x] Returns Lob tracking ID

**Reference**: `miscellaneous/original_project_dump/FightSFTickets_CODE_POLISHED/backend_lob_service.txt`

---

## 📋 Backlog - Phase 2: API Routes (Week 2-3)

### TASK-201: Citation Validation Endpoint
**Status**: ✅ COMPLETED
**Completed**: January 2025
**Files Modified**: `backend/src/routes/tickets.py`

**Requirements**:
- [x] `POST /api/citation/validate` endpoint
- [x] Accept citation_number, license_plate, violation_date
- [x] Return validation result with deadline

---

### TASK-202: Transcription Endpoint
**Status**: ✅ COMPLETED
**Completed**: January 2025
**Files Created**: `backend/src/routes/transcribe.py`

**Requirements**:
- [x] `POST /api/transcribe` endpoint
- [x] Accept multipart form with audio file
- [x] Return transcript text

---

### TASK-203: Statement Refinement Endpoint
**Status**: ✅ COMPLETED
**Completed**: January 2025
**Files Created**: `backend/src/routes/statement.py`

**Requirements**:
- [x] `POST /api/statement/refine` endpoint
- [x] Accept raw transcript + ticket metadata
- [x] Return polished letter text

---

### TASK-204: Session Status Endpoint
**Status**: ✅ COMPLETED
**Completed**: January 2025
**Files Modified**: `backend/src/routes/checkout.py`

**Requirements**:
- [x] `GET /api/session/{session_id}` endpoint
- [x] Return payment status and metadata

---

## 📋 Backlog - Phase 3: Frontend (Week 3-4)

### TASK-401: Connect Webhook to Mail Service
**Priority**: HIGH
**Estimated Effort**: 2 hours
**Files to Modify**: `backend/src/routes/webhooks.py`

**Requirements**:
- [ ] Import mail service in webhook handler
- [ ] Extract appeal data from Stripe metadata
- [ ] Call mail service on successful payment
- [ ] Handle errors gracefully

**Acceptance Criteria**:
- [ ] Successful payments trigger mail fulfillment
- [ ] Failed mail attempts are logged and retried
- [ ] Webhook remains idempotent

### TASK-301: Landing Page Redesign
**Priority**: HIGH
**Estimated Effort**: 4 hours
**Files to Modify**: `frontend/app/page.tsx`

**Requirements**:
- [ ] Hero section with value proposition
- [ ] 3-step process visualization
- [ ] Pricing cards ($9 / $19)
- [ ] CTA buttons to start appeal
- [ ] UPL disclaimer in footer

---

### TASK-302: Citation Entry Page
**Priority**: HIGH
**Estimated Effort**: 3 hours
**Files to Create**: `frontend/app/appeal/page.tsx`

**Requirements**:
- [ ] Citation number input with validation
- [ ] License plate input
- [ ] Violation date picker
- [ ] Vehicle description field
- [ ] "Next" button to camera step

---

### TASK-303: Photo Upload Component
**Priority**: HIGH
**Estimated Effort**: 4 hours
**Files to Create**: `frontend/app/appeal/camera/page.tsx`, `frontend/app/components/PhotoUploader.tsx`

**Requirements**:
- [ ] Drag-and-drop file upload
- [ ] Camera capture on mobile
- [ ] Extract GPS metadata if available
- [ ] Timestamp each photo
- [ ] Preview thumbnails

---

### TASK-304: Voice Recorder Component
**Priority**: HIGH
**Estimated Effort**: 4 hours
**Files to Create**: `frontend/app/appeal/voice/page.tsx`, `frontend/app/components/VoiceRecorder.tsx`

**Requirements**:
- [ ] Request microphone permission
- [ ] Record audio with visualization
- [ ] Show duration timer (max 2 min)
- [ ] Play back recording
- [ ] Send to transcription API

**Reference**: `miscellaneous/original_project_dump/FightSFTickets_CODE_POLISHED/VoiceRecorder.txt`

---

### TASK-305: Evidence Selector Component
**Priority**: HIGH
**Estimated Effort**: 3 hours
**Files to Create**: `frontend/app/appeal/evidence/page.tsx`, `frontend/app/components/EvidenceSelector.tsx`

**Requirements**:
- [ ] Display photo grid
- [ ] Tap to select/deselect
- [ ] Show selection count
- [ ] NO recommendations (UPL compliance)
- [ ] Default: all selected

---

### TASK-306: Letter Review Page
**Priority**: HIGH
**Estimated Effort**: 4 hours
**Files to Create**: `frontend/app/appeal/review/page.tsx`, `frontend/app/components/LetterEditor.tsx`

**Requirements**:
- [ ] Display AI-generated letter
- [ ] "Edit" button to enable editing
- [ ] "Polish with AI" button for refinement
- [ ] Character count
- [ ] UPL disclaimer visible

---

### TASK-307: Signature Component
**Priority**: HIGH
**Estimated Effort**: 3 hours
**Files to Create**: `frontend/app/components/SignaturePad.tsx`

**Requirements**:
- [ ] Touch/mouse signature capture
- [ ] Clear button
- [ ] Export as image
- [ ] Attestation checkbox

---

### TASK-308: Checkout Page
**Priority**: HIGH
**Estimated Effort**: 4 hours
**Files to Create**: `frontend/app/appeal/checkout/page.tsx`

**Requirements**:
- [ ] Display order summary
- [ ] Standard vs Certified selection
- [ ] Show price breakdown
- [ ] "Pay" button → Stripe redirect
- [ ] Loading state during redirect

---

### TASK-309: Success Page
**Priority**: MEDIUM
**Estimated Effort**: 2 hours
**Files to Create**: `frontend/app/success/page.tsx`

**Requirements**:
- [ ] Confirmation message
- [ ] Expected delivery timeline
- [ ] Next steps info
- [ ] Receipt email mention

---

### TASK-310: Terms of Service Page
**Priority**: HIGH
**Estimated Effort**: 2 hours
**Files to Create**: `frontend/app/terms/page.tsx`

**Requirements**:
- [ ] Full Terms of Service text
- [ ] "Not a law firm" disclaimer box
- [ ] Last updated date

---

### TASK-311: Privacy Policy Page
**Priority**: HIGH
**Estimated Effort**: 2 hours
**Files to Create**: `frontend/app/privacy/page.tsx`

**Requirements**:
- [ ] Privacy Policy text
- [ ] CCPA compliance section
- [ ] Data retention policy
- [ ] Contact information

---

## 📋 Backlog - Phase 4: Integration & Testing (Week 4-5)

### TASK-401: Appeal Flow State Management
**Priority**: HIGH
**Estimated Effort**: 4 hours
**Files to Create**: `frontend/app/lib/appeal-context.tsx`

**Requirements**:
- [ ] React Context for appeal state
- [ ] Persist to sessionStorage
- [ ] Clear on completion/abandon

---

### TASK-402: API Client Library
**Priority**: HIGH
**Estimated Effort**: 3 hours
**Files to Create**: `frontend/app/lib/api.ts`

**Requirements**:
- [ ] Typed fetch functions for all endpoints
- [ ] Error handling
- [ ] Loading states

---

### TASK-403: Backend Unit Tests
**Priority**: HIGH
**Estimated Effort**: 4 hours
**Files to Create**: `backend/tests/test_*.py`

**Requirements**:
- [ ] Citation validation tests
- [ ] Checkout session tests
- [ ] Webhook handler tests
- [ ] Mail service tests (mocked)

---

### TASK-404: End-to-End Tests
**Priority**: MEDIUM
**Estimated Effort**: 4 hours
**Files to Create**: `frontend/e2e/appeal-flow.spec.ts`

**Requirements**:
- [ ] Complete flow test with mocked APIs
- [ ] Error state tests
- [ ] Mobile viewport tests

---

## 📋 Backlog - Phase 5: Deployment (Week 5-6)

### TASK-501: Production Environment Setup
**Priority**: HIGH
**Estimated Effort**: 3 hours

**Requirements**:
- [ ] Create `.env.production` template
- [ ] Document all required env vars
- [ ] Set up production database

---

### TASK-502: Stripe Production Setup
**Priority**: HIGH
**Estimated Effort**: 2 hours

**Requirements**:
- [ ] Create production products/prices in Stripe
- [ ] Register webhook endpoint
- [ ] Verify Apple Pay domain

---

### TASK-503: Deployment Scripts
**Priority**: MEDIUM
**Estimated Effort**: 3 hours
**Files to Create**: `scripts/deploy.py`

**Requirements**:
- [ ] Backend deployment script
- [ ] Frontend build and deploy
- [ ] Health check verification

---

### TASK-504: Monitoring Setup
**Priority**: MEDIUM
**Estimated Effort**: 2 hours

**Requirements**:
- [ ] Health check monitoring
- [ ] Error alerting
- [ ] Uptime monitoring

---

## ✅ Completed

### TASK-001: Project Skeleton Setup
**Completed**: January 2025
- Created Docker Compose configuration
- Set up FastAPI backend skeleton
- Set up Next.js frontend skeleton
- Deployed to Hetzner server

### TASK-002: Server Cleanup
**Completed**: January 2025
- Removed unused Docker volumes (633MB reclaimed)
- Cleaned old project remnants
- Verified running services

### TASK-003: Documentation Review
**Completed**: January 2025
- Analyzed all starter kit documentation
- Created DEVELOPMENT_PLAN.md
- Identified all required components

---

## 📝 Notes

### UPL Compliance Checklist
Every frontend page must:
- [ ] NOT recommend specific evidence
- [ ] NOT promise outcomes
- [ ] NOT provide legal advice
- [ ] Show disclaimer where appropriate
- [ ] Let user make all decisions

### API Keys Required
- `STRIPE_SECRET_KEY` - Payment processing
- `STRIPE_WEBHOOK_SECRET` - Webhook verification
- `LOB_API_KEY` - Mail service
- `DEEPSEEK_API_KEY` - Statement refinement
- `OPENAI_API_KEY` - Voice transcription

### Test Mode vs Live Mode
- Development: Use `sk_test_` (Stripe), `test_` (Lob)
- Production: Use `sk_live_` (Stripe), `live_` (Lob)
- Card for testing: `4242424242424242`

---

*Update this file as tasks are started and completed.*