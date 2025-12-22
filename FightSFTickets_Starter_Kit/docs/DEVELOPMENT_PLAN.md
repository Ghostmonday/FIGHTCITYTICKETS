# FightSFTickets Development Plan

> **Generated**: January 2025
> **Status**: Ready for Implementation
> **Target**: Complete SF City Flow (Intake → Payment → Mail Output)

---

## Executive Summary

FightSFTickets.com is a production SaaS that automates San Francisco parking ticket appeals via physical mail. Users submit evidence, record their story, receive AI-drafted appeal letters, and the system mails them via Lob API.

This document provides a structured implementation roadmap to complete the SF city flow from the current skeleton state to a fully operational system.

---

## 1. Key Components Summary

### 1.1 Technology Stack

| Layer | Technology | Status |
|-------|------------|--------|
| **Frontend** | Next.js 14 + TypeScript + Tailwind CSS | Skeleton exists |
| **Backend** | FastAPI (Python 3.11+) | Skeleton exists |
| **Database** | PostgreSQL (Docker) | Container running |
| **Transcription** | OpenAI Whisper API | Needs implementation |
| **Letter Drafting** | DeepSeek API | Needs implementation |
| **Mailing** | Lob API (print & mail) | Needs implementation |
| **Payments** | Stripe Checkout | Needs implementation |
| **Hosting** | Hetzner VPS (5.161.239.203) | Operational |

### 1.2 External Service Dependencies

| Service | Purpose | API Key Prefix | Dashboard |
|---------|---------|----------------|-----------|
| **Stripe** | Payment processing | `sk_live_` / `sk_test_` | dashboard.stripe.com |
| **Lob** | Physical mail delivery | `live_` / `test_` | dashboard.lob.com |
| **DeepSeek** | AI statement refinement | `sk-` | platform.deepseek.com |
| **OpenAI** | Whisper transcription | `sk-` | platform.openai.com |

### 1.3 Pricing Model

| Plan | Price | Stripe Fee | Lob Cost | Net Profit | Margin |
|------|-------|------------|----------|------------|--------|
| **Standard** | $9.00 | $0.56 | ~$1.00 | ~$7.42 | 82% |
| **Certified** | $19.00 | $0.85 | ~$10.50 | ~$7.63 | 40% |

---

## 2. Critical Constraints & Compliance

### 2.1 UPL (Unauthorized Practice of Law) Compliance — NON-NEGOTIABLE

| Rule | Implementation |
|------|----------------|
| **No Legal Advice UX** | System NEVER says "you should include X" or "this will help your case" |
| **User Selects Evidence** | Present photos → user taps which to include → system does not recommend |
| **User Review Gate** | User MUST see/edit letter before signature/payment |
| **No Outcome Promises** | Never say "guaranteed to win" or "high success rate" |
| **Factual Statements Only** | AI drafts facts, not opinions or legal arguments |

### 2.2 Required Disclaimers (Must appear on site)

```text
FightSFTickets.com is NOT a law firm and does not provide legal advice.
We are a document preparation service that helps you submit your own appeal.
We make no guarantees about the outcome of your appeal.
```

### 2.3 Data & Security Rules

| Rule | Implementation |
|------|----------------|
| **Secrets Never in Repo** | Use `.env` files, never commit API keys |
| **Minimal Data Retention** | Don't store more than needed for fulfillment |
| **Physical Mail Only** | Avoid portal automation (CAPTCHA/ToS risk) |
| **Evidence Metadata** | Store GPS + capture time with each photo |

---

## 3. User Flow (State Machine)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. CAMERA  │───▶│  2. VOICE   │───▶│  3. DRAFT   │
│ Upload/Take │    │  Record     │    │  AI Letter  │
│   Photos    │    │  Story      │    │  Generated  │
└─────────────┘    └─────────────┘    └─────────────┘
                                            │
                                            ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 6. FINALIZE │◀───│ 5. REVIEW   │◀───│ 4. EVIDENCE │
│  PDF+Mail   │    │  +SIGN+PAY  │    │  SELECTOR   │
│  via Lob    │    │  $9 / $19   │    │  User Picks │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Stage Details

1. **CAMERA**: User captures/uploads photos. GPS + timestamp captured on device.
2. **VOICE**: User records voice note → backend transcribes via Whisper.
3. **DRAFT**: Backend calls DeepSeek with transcript + ticket metadata → returns draft letter.
4. **EVIDENCE SELECTOR**: Show photo grid. User taps photos to include. (Default: all selected)
5. **REVIEW & SIGN**: User edits statement, signs digitally, attests, then pays ($9 or $19).
6. **FINALIZE**: Backend compiles PDF → Lob mails to SFMTA.

---

## 4. Implementation Roadmap

### Phase 1: Backend Core Services (Week 1-2)

#### 1.1 Citation Validation Service
**Priority**: HIGH
**Files to Create**: `backend/src/services/citation.py`

```python
# Required functionality:
- validate_citation_number(number: str) -> bool
- calculate_appeal_deadline(violation_date: date) -> date  # 21 days from issue
- get_agency_info(citation_number: str) -> AgencyInfo
- check_online_appeal_available(citation_number: str) -> bool
```

**Reference**: `miscellaneous/original_project_dump/FightSFTickets_CODE_POLISHED/backend_api_service.txt`

#### 1.2 Statement Refinement Service (DeepSeek)
**Priority**: HIGH
**Files to Create**: `backend/src/services/statement.py`

```python
# Required functionality:
- refine_statement(raw_transcript: str, ticket_metadata: dict) -> str
- Uses DeepSeek API with specific system prompt (see section 5.1)
- Falls back to basic formatting if API unavailable
```

**Reference**: `miscellaneous/original_project_dump/FightSFTickets_CODE_POLISHED/backend_appeal_generator.txt`

#### 1.3 Transcription Service (OpenAI Whisper)
**Priority**: HIGH
**Files to Create**: `backend/src/services/transcription.py`

```python
# Required functionality:
- transcribe_audio(audio_file: UploadFile) -> str
- Supports: webm, mp3, wav, m4a formats
- Max duration: 2 minutes
```

#### 1.4 Checkout Service (Stripe)
**Priority**: HIGH
**Files to Modify**: `backend/src/routes/checkout.py`

```python
# Required functionality:
- create_checkout_session(appeal_data: AppealRequest) -> CheckoutSession
- handle_webhook(payload: bytes, signature: str) -> None
- get_session_status(session_id: str) -> SessionStatus
```

**Reference**: `miscellaneous/original_project_dump/FightSFTickets_CODE_POLISHED/backend_checkout.txt`

#### 1.5 Mail Service (Lob)
**Priority**: HIGH
**Files to Create**: `backend/src/services/mail.py`

```python
# Required functionality:
- send_appeal_letter(appeal_data: AppealData, mail_type: str) -> MailResult
- generate_appeal_pdf(appeal_data: AppealData) -> bytes
- get_mailing_address(citation_number: str) -> Address  # Routes to correct agency
```

**Reference**: `miscellaneous/original_project_dump/FightSFTickets_CODE_POLISHED/backend_lob_service.txt`

---

### Phase 2: Backend API Routes (Week 2-3)

#### 2.1 Required Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check (exists) |
| `/api/citation/validate` | POST | Validate citation number |
| `/api/transcribe` | POST | Transcribe voice recording |
| `/api/statement/refine` | POST | AI-refine user statement |
| `/api/checkout/create-session` | POST | Create Stripe checkout |
| `/api/webhook/stripe` | POST | Handle Stripe webhooks |
| `/api/session/{id}` | GET | Check payment status |

#### 2.2 Data Models

```python
# backend/src/models/appeal.py

class CitationValidation(BaseModel):
    citation_number: str
    license_plate: str
    violation_date: date | None = None

class AppealRequest(BaseModel):
    citation_number: str
    violation_date: date
    vehicle_info: str
    user_statement: str
    selected_photos: list[str]  # URLs or IDs
    user_name: str
    user_address: str
    user_city: str
    user_state: str
    user_zip: str
    mail_type: Literal["standard", "certified"]

class CheckoutMetadata(BaseModel):
    citation_number: str
    appeal_type: str
    user_name: str
    user_address_line1: str
    user_city: str
    user_state: str
    user_zip: str
    violation_date: str
    vehicle_info: str
    appeal_reason: str
```

---

### Phase 3: Frontend Implementation (Week 3-4)

#### 3.1 Page Structure

```
frontend/app/
├── page.tsx                    # Landing page
├── layout.tsx                  # App layout
├── appeal/
│   ├── page.tsx               # Appeal flow start (citation entry)
│   ├── camera/page.tsx        # Photo capture/upload
│   ├── voice/page.tsx         # Voice recording
│   ├── evidence/page.tsx      # Photo selection
│   ├── review/page.tsx        # Review & edit letter
│   └── checkout/page.tsx      # Payment
├── success/page.tsx           # Payment success
├── terms/page.tsx             # Terms of Service
├── privacy/page.tsx           # Privacy Policy
└── components/
    ├── CitationForm.tsx
    ├── PhotoUploader.tsx
    ├── VoiceRecorder.tsx
    ├── EvidenceSelector.tsx
    ├── LetterEditor.tsx
    ├── SignaturePad.tsx
    └── CheckoutButton.tsx
```

#### 3.2 Key Components

**VoiceRecorder.tsx** (Reference: `FightSFTickets_CODE_POLISHED/VoiceRecorder.txt`)
- Audio level visualization
- Duration timer (max 2 minutes)
- Start/stop/replay controls
- Mic permission handling

**PhotoUploader.tsx**
- Drag-and-drop upload
- Camera capture on mobile
- GPS metadata extraction
- Timestamp capture

**EvidenceSelector.tsx**
- Photo grid display
- Tap-to-select/deselect
- Preview modal
- UPL-safe: no recommendations

**LetterEditor.tsx**
- Read-only by default, edit on request
- "Polish with AI" button
- Character count
- UPL disclaimer visible

#### 3.3 State Management

```typescript
// frontend/app/lib/appeal-context.tsx

interface AppealState {
  step: 'citation' | 'camera' | 'voice' | 'evidence' | 'review' | 'checkout';
  citation: {
    number: string;
    violationDate: string;
    vehicleInfo: string;
  };
  photos: Photo[];
  selectedPhotoIds: string[];
  voiceRecording: Blob | null;
  transcript: string;
  draftLetter: string;
  editedLetter: string;
  signature: string;
  userInfo: UserInfo;
  mailType: 'standard' | 'certified';
}
```

---

### Phase 4: Integration & Testing (Week 4-5)

#### 4.1 End-to-End Flow Testing

```bash
# Test sequence:
1. Enter citation number → validate
2. Upload photos → store with metadata
3. Record voice → transcribe via Whisper
4. Generate draft → DeepSeek API
5. Select evidence → user picks photos
6. Review letter → edit if needed
7. Sign & pay → Stripe checkout
8. Webhook fires → Lob sends mail
```

#### 4.2 Test Credentials

| Service | Test Mode |
|---------|-----------|
| Stripe | Card: `4242424242424242`, any future date, any CVC |
| Lob | Use `test_` API key — no real mail sent |
| DeepSeek | Use real key (no test mode) |
| OpenAI | Use real key (no test mode) |

#### 4.3 Required Tests

```python
# backend/tests/

test_citation_validation.py
  - test_valid_citation_format
  - test_invalid_citation_rejected
  - test_deadline_calculation

test_checkout.py
  - test_create_checkout_session
  - test_webhook_payment_succeeded
  - test_webhook_signature_verification

test_mail.py
  - test_pdf_generation
  - test_lob_letter_creation
  - test_address_routing
```

---

### Phase 5: Production Deployment (Week 5-6)

#### 5.1 Environment Setup

```env
# .env.production

# Stripe (LIVE)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Lob (LIVE)
LOB_API_KEY=live_...

# AI Services
DEEPSEEK_API_KEY=sk-...
OPENAI_API_KEY=sk-...

# App
APP_ENV=production
APP_URL=https://fightsftickets.com
API_URL=https://fightsftickets.com/api
CORS_ORIGINS=https://fightsftickets.com

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/fightsf
```

#### 5.2 Deployment Checklist

- [ ] All API keys rotated for production
- [ ] Stripe webhook endpoint registered
- [ ] SSL certificate valid
- [ ] CORS configured correctly
- [ ] Health check endpoint responding
- [ ] Error logging configured
- [ ] Database backups scheduled
- [ ] UPL disclaimers visible on all relevant pages

---

## 5. AI System Prompts

### 5.1 DeepSeek Statement Refinement Prompt

```text
You are a professional document assistant for FightSFTickets.com.

Your task: Convert a user's informal spoken complaint about a parking ticket 
into a formal, factual appeal letter.

RULES:
1. NEVER give legal advice or recommend what evidence to include
2. Use neutral, professional language only
3. State FACTS, not opinions
4. Do not editorialize or add emotional language
5. Do not make claims the user did not make
6. Format as a formal letter to the citation agency

INPUT: User transcript about their parking ticket situation
OUTPUT: A professional appeal letter ready for signature

Structure:
- Header: Date, Recipient Address placeholder
- Subject: Citation Number
- Body: Factual statement of circumstances
- Closing: Request for review/dismissal
- Signature block placeholder
```

---

## 6. SFMTA Appeal Categories

The system should categorize appeals into official SFMTA categories:

1. METER PAID/MALFUNCTION
2. CURB PAINTING
3. MISSING/OBSCURED SIGN
4. SOLD/NOT OWNED YET
5. VALID PERMIT/DP DISPLAYED
6. COMPLIANCE/FIX IT CITATION
7. DISCLAIMER/NOT MY CAR
8. TRANSIT VIOLATION
9. STOLEN VEHICLE/PLATE
10. OTHER, EXPLAIN DETAILS

**Implementation**: Auto-detect category from user statement, but let user override.

---

## 7. Suggested Order of Operations

### Week 1: Foundation
1. ✅ Review all documentation (this step)
2. Set up environment variables template
3. Implement citation validation service
4. Implement Stripe checkout (copy from polished code)

### Week 2: Core Services
5. Implement DeepSeek statement refinement
6. Implement OpenAI Whisper transcription
7. Implement Lob mail service
8. Create webhook handlers

### Week 3: Frontend Flow
9. Build citation entry page
10. Build photo upload component
11. Build voice recorder component
12. Build evidence selector

### Week 4: Complete Flow
13. Build letter review/edit page
14. Build signature component
15. Build checkout page
16. Integrate all frontend pages

### Week 5: Testing & Polish
17. Write backend tests
18. Write frontend tests
19. End-to-end testing
20. UPL compliance review

### Week 6: Deployment
21. Production environment setup
22. Final security audit
23. Go live
24. Monitor first transactions

---

## 8. Reference Files in Starter Kit

| Need | Reference File |
|------|----------------|
| Stripe integration | `FightSFTickets_CODE_POLISHED/backend_checkout.txt` |
| Lob mail service | `FightSFTickets_CODE_POLISHED/backend_lob_service.txt` |
| Appeal generator | `FightSFTickets_CODE_POLISHED/backend_appeal_generator.txt` |
| API service | `FightSFTickets_CODE_POLISHED/backend_api_service.txt` |
| Voice recorder UI | `FightSFTickets_CODE_POLISHED/VoiceRecorder.txt` |
| Server deployment | `FightSFTickets_CODE_POLISHED/ops_deploy_backend.txt` |
| Health monitoring | `FightSFTickets_CODE_POLISHED/ops_health_monitor.txt` |

---

## 9. Success Metrics

### Launch Criteria
- [ ] User can complete full flow: citation → payment → mail sent
- [ ] All UPL disclaimers in place
- [ ] Terms of Service and Privacy Policy pages live
- [ ] Stripe webhooks verified working
- [ ] Lob test letter successfully created
- [ ] Health check endpoint returning 200

### Post-Launch KPIs
- Conversion rate: Citation entry → Payment
- Average time to complete flow
- Payment success rate
- Lob delivery success rate
- Customer support tickets per transaction

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| DeepSeek API down | Local fallback formatting (basic cleanup) |
| Whisper API down | Allow manual text entry as alternative |
| Lob API failure | Queue for retry, alert operator |
| Stripe webhook miss | Idempotency keys, manual reconciliation tool |
| UPL violation claim | Clear disclaimers, user-in-control design, legal review |

---

## Appendix: Quick Start Commands

```bash
# Start all services (Docker)
docker compose up --build

# Backend only (development)
cd backend
uvicorn src.app:app --reload --port 8000

# Frontend only (development)
cd frontend
npm run dev

# Run backend tests
cd backend
pytest

# Deploy to production (from scripts)
python scripts/deploy_backend.py
python scripts/deploy_frontend.py
```

---

*This plan is based on analysis of all documentation in the FightSFTickets Starter Kit.
Update `docs/TASK_QUEUE.md` as tasks are completed.*