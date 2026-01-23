
# FIGHTCITYTICKETS.com - Technical Handoff Document

**Version:** 1.0  
**Date:** January 10, 2025  
**Status:** Pre-Launch / Production Ready

---

## Executive Summary

FIGHTCITYTICKETS.com is a procedural compliance service that helps users prepare and mail parking ticket appeals to municipalities across the United States. The system is built on a modern full-stack architecture with FastAPI (Python) backend, Next.js (React/TypeScript) frontend, PostgreSQL database, and integration with Stripe (payments), Lob (certified mail), and DeepSeek (AI letter refinement).

**Critical Business Model Notes:**
- NOT a law firm - we provide document preparation services only
- Must comply with state-by-state UPL (Unauthorized Practice of Law) regulations
- Revenue model: $9 (standard) or $12 (certified mail) per appeal
- Margin protection requires careful attention to mail service configuration

---

## Architecture Overview

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|----------|
| **Frontend** | Next.js 15, React 18, TypeScript | User-facing web application |
| **Backend** | FastAPI (Python 3.12), SQLAlchemy | API server, business logic |
| **Database** | PostgreSQL (via Supabase/Neon) | Persistent storage |
| **Payments** | Stripe | Checkout sessions, webhook handling |
| **Mail** | Lob API | Certified/standard mail fulfillment |
| **AI** | DeepSeek | Appeal letter refinement |
| **Infrastructure** | Docker, DigitalOcean | Container orchestration |
| **DNS** | Namecheap | Domain management |

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                              │
│                    (Next.js Frontend)                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NGINX REVERSE PROXY                         │
│                    (SSL Termination, Routing)                    │
└──────────┬────────────────────────┬───────────────────────┬──────┘
           │                        │                       │
           ▼                        ▼                       ▼
┌──────────────────┐    ┌───────────────────┐    ┌───────────────┐
│  Next.js :3000   │    │  FastAPI :8000    │    │  PostgreSQL   │
│  (Frontend)      │    │  (API Server)     │    │  (Database)   │
└──────────────────┘    └─────────┬───────────┘    └───────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
        ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
        │   Stripe    │   │    Lob     │   │  DeepSeek   │
        │  (Payments) │   │   (Mail)   │   │    (AI)     │
        └─────────────┘   └─────────────┘   └─────────────┘
```

---

## Critical Fixes Implemented

### 1. UPL Compliance - Red State Blocking

**File:** `backend/src/routes/checkout.py`

```python
# States where service is blocked due to UPL regulations
BLOCKED_STATES = ["TX", "NC", "NJ", "WA"]

# In create_appeal_checkout function:
if appeal_request.user_state in BLOCKED_STATES:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="We are currently unable to offer our services in your state due to local regulations."
    )
```

**Why:** These states have strict Unauthorized Practice of Law regulations that could expose the company to legal liability.

---

### 2. Address Validation - Prevent Undeliverable Mail Burn

**File:** `backend/src/routes/checkout.py`

```python
async def verify_user_address(address1: str, city: str, state: str, zip_code: str) -> tuple:
    """Validate user return address using Lob's US verification API."""
    auth = (settings.lob_api_key, "")
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://api.lob.com/v1/us_verifications",
            auth=auth,
            json={
                "primary_line": address1,
                "city": city,
                "state": state,
                "zip_code": zip_code,
            },
        )
    
    data = resp.json()
    if data.get("deliverability") == "undeliverable":
        return False, "The return address provided is invalid or undeliverable."
    return True, None
```

**Why:** Prevents paying for mail that will be returned undeliverable, protecting revenue.

---

### 3. Margin Optimization - Mail Service Configuration

**File:** `backend/src/services/mail.py`

```python
# DEFAULT SETTINGS (For $9 Standard Mail)
payload = {
    "description": f"Appeal letter for citation {request.citation_number}",
    "to": agency_address.to_lob_dict(),
    "from": user_address.to_lob_dict(),
    "file": pdf_base64,
    "file_type": "application/pdf",
    "mail_type": "usps_first_class",  # Default for standard
    "color": False,
    "double_sided": True,  # Save cost on Standard
    "address_placement": "top_first_page",  # Use top of first page
    "merge_variables": {"name": user_first_name},
}

# OVERRIDE FOR CERTIFIED MAIL ($12 Premium)
if request.appeal_type == "certified":
    payload["mail_type"] = "usps_certified"
    payload["extra_service"] = "certified_return_receipt"  # Green Card proof
    payload["double_sided"] = False  # Professional single-sided look
    payload["return_envelope"] = False  # City pays for return envelope
```

**Margin Impact:**
- `insert_blank_page` → `top_first_page`: Save ~$0.15/letter
- `return_envelope: False`: Save ~$0.50/letter (certified only)

---

### 4. PDF Generation - Window Envelope Compliance

**File:** `backend/src/services/mail.py`

```python
def _generate_appeal_pdf(self, request: AppealLetterRequest) -> bytes:
    # ... existing code ...
    story = []

    # Top spacer for return address window (2 inches = 144 points)
    story.append(Spacer(1, 144))

    # Header
    story.append(Paragraph("PARKING CITATION APPEAL", title_style))
    # ... rest of PDF generation
```

**Why:** Proper spacing ensures the return address aligns with #10 double window envelopes, avoiding Lob's costly cover sheet.

---

### 5. Tracking Gate - Privacy for Standard Mail

**File:** `backend/src/routes/status.py`

```python
# TRACKING GATE: Hide tracking for standard mail users
is_certified = payment.appeal_type.value == "certified"
tracking_number = payment.lob_tracking_id if is_certified else None
```

**File:** `backend/src/routes/checkout.py`

```python
class SessionStatusResponse(BaseModel):
    # ... existing fields ...
    tracking_visible: bool = True  # False for standard mail ($9) users
```

**Frontend:** Status page checks `tracking_visible` before showing tracking information.

**Why:** Standard mail doesn't include tracking - don't promise what you can't deliver.

---

### 6. Frontend Citation Validation

**File:** `frontend/app/appeal/checkout/page.tsx`

```python
# Citation format patterns by city
CITATION_PATTERNS: Record<string, RegExp> = {
  sf: /^[A-Z0-9]{6,12}$/i,
  "us-ca-san_francisco": /^[A-Z0-9]{6,12}$/i,
  la: /^[A-Z0-9]{6,10}$/i,
  "us-ca-los_angeles": /^[A-Z0-9]{6,10}$/i,
  nyc: /^[A-Z0-9]{8,12}$/i,
  "us-ny-new_york": /^[A-Z0-9]{8,12}$/i,
  # ... additional cities
};
```

**Why:** Catch format errors early in the browser before backend validation.

---

### 7. Checkout Risk Modal - Standard Mail Disclaimer

**File:** `frontend/app/appeal/checkout/page.tsx`

When user selects standard mail ($9), a warning modal appears:

```typescript
if (state.appealType === "standard" && !confirmedStandardRisk) {
    setShowStandardMailWarning(true);
    return;
}
```

Users must acknowledge:
> "I acknowledge that Standard Mail is untracked and I waive liability for lost mail. I understand the city may not receive my appeal."

---

### 8. Webhook Fulfillment - Critical Path

**File:** `backend/src/routes/webhooks.py`

The `handle_checkout_session_completed` function:

1. Validates payment status is "paid"
2. Fetches payment, intake, and draft from database
3. Constructs `AppealLetterRequest`
4. Calls `mail_service.send_appeal_letter(mail_request)`
5. Updates payment with tracking number
6. Sends email confirmations

**This is the CRITICAL PATH - if this fails, no mail is sent.**

---

## Deployment Information

### Production URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://fightcitytickets.com |
| **API** | https://fightcitytickets.com/api |
| **Health Check** | https://fightcitytickets.com/health |
| **API Docs** | https://fightcitytickets.com/docs |

### Environment Variables

**Required in `.env`:**

```bash
# Stripe (Get from https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STANDARD=price_...
STRIPE_PRICE_CERTIFIED=price_...

# Lob (Get from https://dashboard.lob.com/settings/api)
LOB_API_KEY=live_...
LOB_MODE=live

# DeepSeek (Get from https://platform.deepseek.com/api-keys)
DEEPSEEK_API_KEY=sk-...

# Database
DATABASE_URL=postgresql://...

# App
SECRET_KEY=...
APP_ENV=production
```

### Deployment Commands

```bash
# Via Docker Compose (recommended)
docker compose up -d --build

# Or deploy to DigitalOcean App Platform
# See deploy_temp/scripts/deploy_prod.sh
```

---

## Supported Cities

| City | State | Status | Citation Pattern |
|------|-------|--------|------------------|
| San Francisco | CA | ✅ Ready | `^[A-Z0-9]{6,12}$` |
| Los Angeles | CA | ✅ Ready | `^[A-Z0-9]{6,10}$` |
| San Diego | CA | ✅ Ready | `^[A-Z0-9]{7,12}$` |
| New York City | NY | ✅ Ready | `^[A-Z0-9]{8,12}$` |
| Chicago | IL | ✅ Ready | `^[A-Z0-9]{8,12}$` |
| Denver | CO | ✅ Ready | `^[A-Z0-9]{6,10}$` |
| Phoenix | AZ | ✅ Ready | `^[A-Z0-9]{7,12}$` |
| Portland | OR | ✅ Ready | `^[A-Z0-9]{6,10}$` |
| Philadelphia | PA | ✅ Ready | `^[A-Z0-9]{6,12}$` |
| Salt Lake City | UT | ✅ Ready | `^[A-Z0-9]{6,12}$` |
| Seattle | WA | ⚠️ LLLT Required | `^[A-Z0-9]{6,12}$` |
| Dallas | TX | 🔴 BLOCKED | UPL Risk |
| Houston | TX | 🔴 BLOCKED | UPL Risk |
| Charlotte | NC | 🔴 BLOCKED | UPL Risk |

---

## Known Issues & Technical Debt

### High Priority

1. **MSYS2/GCC Installation Incomplete**
   - GCC compiler not installed
   - Impact: Cannot compile native Python packages locally
   - Workaround: Use pre-built wheels from PyPI

2. **SSL Certificate Not Yet Installed**
   - Server networking issue prevented certbot from running
   - Impact: HTTPS not working on production
   - Fix: DigitalOcean support ticket submitted

### Medium Priority

3. **City Data Incomplete**
   - Some cities have incomplete address data in `deploy_temp/cities/`
   - Impact: Cannot serve appeals for those cities
   - Fix: Complete city configuration files

4. **No Subscription Model**
   - Currently one-time payments only
   - Impact: Low LTV
   - Fix: Implement recurring subscription option

### Low Priority

5. **No Retry Logic for Lob API**
   - Transient failures in mail service may go unhandled
   - Fix: Add exponential backoff retry

6. **No Email Template Management**
   - Hardcoded email templates
   - Fix: Store templates in database

---

## Monitoring & Observability

### Health Check Endpoints

```bash
# Overall health
curl https://fightcitytickets.com/health

# Detailed status (includes service health)
curl https://fightcitytickets.com/status
```

### Logging

Logs are written to:
- `/var/log/backend.log` (production)
- Console output (development)

### Key Metrics to Monitor

1. **Revenue:** Stripe payment success rate
2. **Fulfillment:** Lob API success rate
3. **Email Deliverability:** Bounce rates
4. **API Latency:** Response times on /api endpoints
5. **Conversion:** Checkout completion rate

---

## Security Considerations

### Data Classification

| Data Type | Storage | Encryption |
|-----------|---------|------------|
| Credit Cards | Stripe Only | PCI Compliant |
| API Keys | Environment Variables | Encrypted at rest |
| User Addresses | Database | At rest encryption |
| Citation Numbers | Database | At rest encryption |
| Appeal Letters | Database | At rest encryption |

### UPL Compliance Checklist

- [x] Red State blocking implemented
- [x] Legal disclaimers on all pages
- [x] "Not a law firm" language prominent
- [x] No legal advice claims in copy
- [x] User attestation required at checkout

### API Security

- Rate limiting enabled (10 requests/minute/IP)
- Request ID tracking for debugging
- CORS configured for frontend origins only
- Webhook signature verification enabled

---

## Development Setup

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Ghostmonday/FightSFTickets.git
cd FightSFTickets

# 2. Frontend Setup
cd frontend
npm install
npm run dev

# 3. Backend Setup (new terminal)
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8000

# 4. Access
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Full Dependency Installation

```powershell
# Run as Administrator for system-wide installation
cd C:\Comapnyfiles\provethat.io
powershell -ExecutionPolicy Bypass -File setup_dev_env.ps1
```

### Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

---

## File Structure

```
provethat.io/
├── backend/
│   ├── src/
│   │   ├── app.py              # FastAPI application
│   │   ├── config.py           # Settings
│   │   ├── routes/
│   │   │   ├── checkout.py     # Payment flow + UPL blocking
│   │   │   ├── status.py       # Appeal status lookup
│   │   │   ├── webhooks.py     # Stripe webhook handler
│   │   │   └── tickets.py      # Citation validation
│   │   ├── services/
│   │   │   ├── mail.py         # Lob API integration
│   │   │   ├── stripe_service.py
│   │   │   ├── citation.py     # City validation
│   │   │   └── database.py
│   │   └── models/            # SQLAlchemy models
│   ├── alembic/               # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Homepage
│   │   ├── appeal/
│   │   │   ├── checkout/      # Checkout flow
│   │   │   ├── pricing/       # Mail type selection
│   │   │   └── status/        # Appeal tracking
│   │   └── components/        # React components
│   ├── package.json
│   └── next.config.js
├── deploy_temp/
│   ├── cities/                # City configurations
│   ├── scripts/               # Deployment scripts
│   └── docs/                  # Documentation
├── docker-compose.yml
├── nginx/
│   └── conf.d/
│       └── fightcitytickets.conf
└── README.md
```

---

## Emergency Procedures

### Payment Issues

1. Check Stripe Dashboard for failed payments
2. Verify webhook delivery in Stripe Dashboard
3. Check backend logs for errors: `grep ERROR /var/log/backend.log`

### Mail Not Sending

1. Verify Lob API key is valid
2. Check Lob Dashboard for sent letters
3. Check payment fulfillment status in database

### Server Down

1. Check DigitalOcean console
2. Verify Docker containers are running: `docker ps`
3. Check container logs: `docker logs <container_name>`
4. Restart if needed: `docker compose restart`

---

## Key Contacts

| Role | Contact |
|------|---------|
| **Primary Engineer** | See GitHub contributors |
| **Infrastructure** | DigitalOcean Support |
| **Payments** | Stripe Support |
| **Mail Services** | Lob Support |
| **Domain/DNS** | Namecheap Support |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-10 | Initial handoff document |

---

## Appendices

### Appendix A: Stripe Price IDs

**Must match exactly between `.env` and Stripe Dashboard:**

| Price | Environment | Price ID |
|-------|-------------|----------|
| Standard ($9) | Test | `price_...` |
| Certified ($12) | Test | `price_...` |
| Standard ($9) | Live | `price_...` |
| Certified ($12) | Live | `price_...` |

### Appendix B: Lob Mail Types

| Mail Type | Cost | Tracking | Return Envelope |
|-----------|------|----------|-----------------|
| usps_first_class | ~$0.50 | No | No |
| usps_certified | ~$4.00 | Yes | Optional |

### Appendix C: Citation Validation Patterns

```python
# From backend/src/services/citation.py
SFMTA_PATTERN = re.compile(r"^9\d{8}$")  # San Francisco
SFPD_PATTERN = re.compile(r"^[A-Z0-9]{6,10}$")  # SF Police
LAPD_PATTERN = re.compile(r"^[A-Z0-9]{6,10}$")  # LA
NYPD_PATTERN = re.compile(r"^[A-Z0-9]{8,12}$")  # NYC
```

---

**Document Generated:** 2025-01-10  
**Last Updated:** 2025-01-10  
**Maintained By:** FIGHTCITYTICKETS Engineering Team

---

*This document is intended for internal use only. Do not distribute externally without approval.*
