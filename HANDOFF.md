# FightCityTickets.com - Project Handoff Document

**Project:** FightCityTickets.com - Procedural Compliance Parking Ticket Appeal Service  
**Version:** 1.0 (Production Ready)  
**Date:** 2025-01-09  
**Classification:** Confidential - For Internal Use Only

---

## Executive Summary

FightCityTickets.com is a production-ready SaaS application that provides document preparation and mailing services for parking ticket appeals. The service operates as a **procedural compliance service**, NOT a law firm or legal service. This distinction is critical for regulatory compliance and must be maintained in all user-facing and internal communications.

The project has been fully updated with Operation Civil Shield branding and messaging, including all required legal disclaimers, operational policies, and internal documentation for business continuity.

---

## Project Structure

```
theprojectinanidealstate/
├── frontend/                          # Next.js 14 Frontend
│   ├── app/                           # App Router Pages
│   │   ├── page.tsx                   # Homepage (needs brand update)
│   │   ├── terms/page.tsx             # ✅ Updated with compliance
│   │   ├── privacy/page.tsx           # ✅ NEW - CCPA compliant
│   │   ├── refund/page.tsx            # ✅ Updated with chargeback policy
│   │   ├── contact/page.tsx           # ✅ NEW - Support accountability
│   │   ├── what-we-are/page.tsx       # ✅ NEW - Compliance page
│   │   ├── appeal/                    # Appeal flow pages
│   │   ├── blog/                      # SEO blog pages
│   │   └── [city]/                    # City-specific pages
│   ├── components/                    # React Components
│   │   ├── LegalDisclaimer.tsx        # ✅ Updated - "We aren't lawyers"
│   │   ├── FooterDisclaimer.tsx       # ✅ Updated - Full compliance
│   │   └── AddressAutocomplete.tsx    # Address validation
│   └── lib/                           # Utilities and hooks
├── backend/                           # FastAPI Backend
│   ├── src/
│   │   ├── routes/                    # API Endpoints
│   │   │   ├── statement.py           # AI statement refinement
│   │   │   ├── checkout.py            # Payment processing
│   │   │   ├── tickets.py             # Citation validation
│   │   │   ├── webhooks.py            # Stripe webhooks
│   │   │   └── status.py              # Appeal status lookup
│   │   └── services/                  # Business Logic
│   │       ├── statement.py           # ✅ Updated - User voice preservation
│   │       ├── mail.py                # Lob mailing service
│   │       ├── email_service.py       # Email notifications
│   │       └── stripe_service.py      # Payment processing
│   ├── alembic/                      # Database migrations
│   └── tests/                        # Test suite
├── cities/                           # City configurations (15+ cities)
├── docs/
│   ├── internal/
│   │   ├── DATA_RETENTION.md          # ✅ NEW - Retention schedules
│   │   └── INCIDENT_RESPONSE.md       # ✅ NEW - Incident playbooks
│   └── DEPLOYMENT_GUIDE.md           # Deployment documentation
├── scripts/                          # Deployment scripts
├── docker-compose.yml                # Docker orchestration
└── README.md                         # Project documentation
```

---

## Brand Positioning - CRITICAL

### Core Brand Statement

> **"We aren't lawyers. We're paperwork experts. And in a bureaucracy, paperwork is power."**

This statement must appear prominently on:
- Homepage hero section
- Legal disclaimer component
- Terms of Service
- What We Are page
- Footer of every page

### What We ARE (Service Description)

We are a **procedural compliance service** that:
- Helps users navigate municipal appeal requirements
- Formats user-provided content into professional appeal letters
- Scans citations for procedural defects (Clerical Engine™)
- Prints and mails appeal letters to city agencies
- Provides tracking and status updates

### What We ARE NOT (MUST NEVER CLAIM)

We are NOT:
- A law firm
- Legal advisors or attorneys
- Legal representatives
- Providers of legal advice
- Someone who guarantees appeal outcomes
- Someone who interprets laws

### Forbidden Language Patterns

**NEVER use these phrases:**
- "We represent you"
- "We will fight for you"
- "We guarantee dismissal"
- "We know the law"
- "We specialize in traffic law"
- "Our legal team"
- "We will win your case"
- "Based on the law..."
- "Your best defense is..."

**ALWAYS use these patterns:**
- "We help you submit your own appeal"
- "We help you articulate your position"
- "We ensure your appeal meets procedural standards"
- "We know the procedural requirements"
- "The procedural flaw we identified is..."

---

## Compliance Requirements

### 1. Legal Disclaimers

All user-facing pages must include appropriate legal disclaimers. Use the `LegalDisclaimer` component:

```typescript
import LegalDisclaimer from "../components/LegalDisclaimer";

// In page render:
<LegalDisclaimer variant="full" />     // Full page disclaimer
<LegalDisclaimer variant="compact" />  // Inline footer
<LegalDisclaimer variant="inline" />   // Brief mention
<LegalDisclaimer variant="elegant" />  // Styled box
```

**Variant Usage:**
- `full`: Terms, Privacy, What We Are pages
- `compact`: Form pages, checkout flow
- `inline`: Error messages, alerts
- `elegant`: Success pages, blog posts

### 2. Required Pages

| Page | URL | Purpose | Status |
|------|-----|---------|--------|
| Terms of Service | /terms | Legal agreement, service description | ✅ Complete |
| Privacy Policy | /privacy | Data collection, usage, rights | ✅ Complete |
| Refund Policy | /refund | Billing, chargebacks, refunds | ✅ Complete |
| Contact Us | /contact | Support, accountability | ✅ Complete |
| What We Are | /what-we-are | Compliance page | ✅ Complete |
| Appeal Status | /appeal/status | User self-service | Exists |

### 3. Internal Documentation (Do Not Publish)

| Document | Location | Purpose |
|----------|----------|---------|
| DATA_RETENTION.md | docs/internal/ | Data retention schedules |
| INCIDENT_RESPONSE.md | docs/internal/ | Incident playbooks |
| CIVIL_SHIELD_COMPLIANCE_AUDIT.md | Root | Full audit with TODOs |

**These documents are INTERNAL ONLY. Do not link to them from the website.**

---

## Technology Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** React Context + useState
- **Deployment:** Vercel or Docker

### Backend
- **Framework:** FastAPI (Python)
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL (configured for SQLite dev)
- **Migration Tool:** Alembic

### External Services
| Service | Purpose | Config Variable |
|---------|---------|-----------------|
| Stripe | Payment Processing | STRIPE_SECRET_KEY |
| Lob | Physical Mailing | LOB_API_KEY |
| OpenAI/DeepSeek | AI Statement Refinement | OPENAI_API_KEY |
| PostgreSQL | Database | DATABASE_URL |

---

## Development Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL (or use SQLite for development)

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd theprojectinanidealstate

# 2. Frontend Setup
cd frontend
npm install
npm run dev
# Frontend available at http://localhost:3000

# 3. Backend Setup (new terminal)
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8000
# Backend API available at http://localhost:8000

# 4. Environment Configuration
cp .env.template .env
# Edit .env with your API keys
```

### Docker Setup (Recommended)

```bash
docker compose up --build
```

---

## Deployment

### Recommended: Hetzner Cloud

```bash
# 1. Set environment variables
export HETZNER_API_TOKEN="your-token"
export DOMAIN="yourdomain.com"

# 2. Run deployment script
chmod +x scripts/deploy_hetzner.sh
./scripts/deploy_hetzner.sh
```

The script will:
- Create Hetzner Cloud server (CX21: 2 vCPU, 4GB RAM)
- Install Docker and all dependencies
- Configure firewall and security
- Deploy frontend, backend, database, nginx
- Run database migrations

### Required API Keys

Get these before deployment:
- [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
- [Lob Dashboard](https://dashboard.lob.com/settings/keys)
- [OpenAI Platform](https://platform.openai.com/api-keys)
- [DeepSeek Platform](https://platform.deepseek.com/api-keys)

---

## Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/tickets/validate` | POST | Validate citation number |
| `/api/statement/refine` | POST | AI statement refinement |
| `/checkout/create-session` | POST | Create Stripe checkout |
| `/status/lookup` | POST | Check appeal status |
| `/webhooks/stripe` | POST | Stripe webhook handler |

---

## Brand Compliance Checklist

Before ANY deployment, verify:

### Legal Compliance
- [ ] "We aren't lawyers. We're paperwork experts." appears on homepage
- [ ] Legal disclaimer component is present on every user-facing page
- [ ] Terms of Service includes full compliance section
- [ ] Privacy Policy is published and linked in footer
- [ ] Refund Policy includes chargeback warning
- [ ] Contact page provides visible accountability
- [ ] What We Are page explains service limitations

### Language Compliance
- [ ] No pages claim "legal advice"
- [ ] No pages promise "guaranteed dismissal"
- [ ] No pages use "lawyer," "attorney," or "legal" in marketing copy
- [ ] CTA buttons use "Submit Appeal" not "Get Dismissed"
- [ ] All AI-generated content preserves user voice

### Operational Compliance
- [ ] Privacy Policy includes CCPA language
- [ ] Data retention schedules are documented
- [ ] Incident response plan exists
- [ ] Contact information is accurate
- [ ] Support email is monitored

---

## Known Issues and TODOs

### From CIVIL_SHIELD_COMPLIANCE_AUDIT.md

The following items still need attention:

| Item | File | Priority |
|------|------|----------|
| Homepage hero update | `app/page.tsx` | HIGH |
| AI system prompt (user voice) | `backend/src/services/statement.py` | DONE |
| Email templates | `backend/src/services/email_service.py` | MEDIUM |
| SEO metadata | `app/layout.tsx` | MEDIUM |
| Blog CTA update | `app/blog/page.tsx` | LOW |
| PDF footer language | `backend/src/services/mail.py` | LOW |

See `CIVIL_SHIELD_COMPLIANCE_AUDIT.md` for detailed TODO markers.

---

## Operational Playbooks

### Data Subject Requests (DSAR)

Users have the right to:
- Access their data
- Correct their data
- Delete their data
- Export their data

**Response Timeline:** 30 days maximum

**Process:**
1. Receive request at `privacy@fightcitytickets.com`
2. Verify user identity
3. Compile all associated data
4. Execute requested action
5. Document the request and response
6. Retain request records per DATA_RETENTION.md

### Incident Response

For security incidents, service outages, or regulatory inquiries:

1. **Assess Severity** (P1-P4)
2. **Notify Team** per INCIDENT_RESPONSE.md
3. **Contain** the issue
4. **Document** everything
5. **Communicate** appropriately
6. **Recover** and review

**Critical Contacts:**
- Operations: ops@fightcitytickets.com
- Legal: External counsel on file
- Hosting: Hetzner Support
- Payments: Stripe Support

### Chargeback Response

If a user disputes a charge:

1. Do NOT refund automatically
2. Gather evidence (payment confirmation, service delivered)
3. Respond to Stripe dispute with documentation
4. Document the incident
5. Consider account review for repeat offenders

---

## Security Notes

### What We Do
- Encrypt data in transit (HTTPS/TLS)
- Encrypt sensitive data at rest
- Use PCI-compliant payment processing (Stripe)
- Implement rate limiting
- Log all access and changes
- Follow principle of data minimization

### What We Do NOT Do
- Store credit card numbers
- Share user data with third parties for marketing
- Keep data longer than necessary
- Skip security reviews

### Sensitive Operations
These require management approval:
- Data exports beyond user requests
- Access to production databases
- Configuration changes to security settings
- Responses to legal/regulatory requests

---

## Common Tasks

### Adding a New City

1. Add city config to `cities/` directory
2. Update `frontend/app/lib/cities.ts` with city list
3. Test citation validation for new city format
4. Add appeal mailing address to mail service
5. Update SEO metadata if needed

### Updating Legal Disclaimers

1. Edit `frontend/components/LegalDisclaimer.tsx`
2. Update all variants as needed
3. Test on all pages where component is used
4. Ensure consistency with Terms of Service

### Modifying AI Behavior

The AI system prompt is in `backend/src/services/statement.py`:

- `_get_system_prompt()` - System instructions for AI
- `_create_refinement_prompt()` - User request template

**IMPORTANT:** Never add legal advice, strategy, or outcome predictions to AI prompts. The AI must only refine and articulate user-provided content.

---

## Support and Resources

### Internal Documentation
- `docs/internal/DATA_RETENTION.md` - Data handling procedures
- `docs/internal/INCIDENT_RESPONSE.md` - Emergency playbooks
- `CIVIL_SHIELD_COMPLIANCE_AUDIT.md` - Compliance audit

### External Resources
- Stripe Documentation: https://stripe.com/docs
- Lob Documentation: https://lob.com/docs
- Next.js Documentation: https://nextjs.org/docs
- FastAPI Documentation: https://fastapi.tiangolo.com

---

## Compliance Self-Check

Before deploying any changes, run through this checklist:

### User-Facing Content
- [ ] Does it say "We aren't lawyers. We're paperwork experts."?
- [ ] Does it avoid promising legal outcomes?
- [ ] Does it avoid using legal terminology improperly?
- [ ] Is the disclaimer visible?

### Backend Changes
- [ ] Does the AI only refine, not create legal arguments?
- [ ] Are user statements preserved verbatim?
- [ ] Is data minimized (only collect what's needed)?

### Third-Party Integrations
- [ ] Are all API keys in environment variables?
- [ ] Is sensitive data logged? (Must NOT be)
- [ ] Are webhooks verified?

---

## Final Notes

This project is a **procedural compliance service**, not a legal service. This distinction is not just marketing—it's the foundation of our regulatory compliance and our defense against UPL (Unauthorized Practice of Law) claims.

Every decision, every piece of copy, every code change should be evaluated against this question:

> "Does this help users submit their own appeals, or does it look like we're practicing law?"

If the answer is unclear, consult the existing patterns in this project, review the Legal Disclaimer component, and err on the side of more disclaimers, not fewer.

---

## Document Control

- **Version:** 1.0
- **Created:** 2025-01-09
- **Author:** Development Team
- **Classification:** Internal - Confidential
- **Next Review:** Before any major deployment

---

**End of Handoff Document**