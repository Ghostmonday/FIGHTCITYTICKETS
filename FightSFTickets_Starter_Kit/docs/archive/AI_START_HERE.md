# FIGHTCITYTICKETS - SINGLE SOURCE OF TRUTH
**Last Updated**: 2025-01-09
**Purpose**: Comprehensive project reference for all AI assistants and developers

---

## 🚀 EXECUTIVE SUMMARY

**Project**: FightCityTickets (formerly FightSFTickets) - Multi-city parking ticket appeal automation
**Status**: ✅ **Production Live** with SF-only implementation, transitioning to 37-city Schema 4.3.0
**Live Site**: https://fightcitytickets.com (178.156.215.100)
**Git Repo**: https://github.com/Ghostmunday/FightCityTickets.git (branch: main)
**Local Path**: `C:\Comapnyfiles\provethat.io\FightSFTickets_Starter_Kit`

**Current Focus**: **Phase 0.3** - Schema Adaptation & City Data Extraction
**Next Milestone**: Complete multi-city foundation for 11 cities (Phase 0)

---

## 📍 PROJECT CONTEXT

### **Current State (Production - SF Only)**
- **Frontend**: Next.js 14 with lenient validation (5+ character citation)
- **Backend**: FastAPI with hardcoded SF patterns
- **Database**: PostgreSQL with `city="sf"` placeholder column
- **Mail Service**: Lob with fixed SFMTA address (11 South Van Ness Ave)
- **Validation**: Bypassed client-side, basic server-side matching
- **User Experience**: 6-step appeal flow (citation → photos → review → signature → checkout → success)

### **Target State (37-City Schema 4.3.0)**
- **Schema Version**: 4.3.0 (strict regex, union addresses, phone confirmation)
- **Goal**: Expand to 37 cities with automated citation → city → section matching
- **Core Service**: `city_registry.py` ✅ **COMPLETE** (Phase 0.1)
- **Key Metrics**: >25% landing→start, >50% start→completion, <8 min time-to-complete

---

## 🏗️ ARCHITECTURE STATE

### **Multi-City Core Services (Phase 0)**
| Service | Status | File | Notes |
|---------|--------|------|-------|
| **City Registry** | ✅ Complete | `backend/src/services/city_registry.py` | Schema 4.3.0 implemented, tested |
| **Citation Service** | ✅ Updated | `backend/src/services/citation.py` | Uses CityRegistry (backward compatible) |
| **Schema Adapter** | ✅ Built | `backend/src/services/schema_adapter.py` | Ready for transformation |
| **Mail Service** | 🔄 Needs Update | `backend/src/services/mail.py` | Update for dynamic addresses |

### **Data Pipeline Status**
| Component | Status | Files | Issues |
|-----------|--------|-------|--------|
| **Phase1 Files** | ✅ 15 cities | `cities/*_phase1.json` | Raw source data |
| **Simplified Extraction** | ✅ Script Ready | `scripts/extract_city_simple.py` | Extracts from Phase1 |
| **Schema Transformation** | ✅ Script Ready | `scripts/transform_simplified_to_schema.py` | **BUG: "Unknown City" issue** |
| **Batch Processing** | ✅ Script Ready | `scripts/batch_process_cities.py` | Automates pipeline |
| **Generated Schema 4.3.0** | ✅ 14/15 cities | `cities/us-*.json` | **14 files, all have "Unknown City" bug** |

### **Critical Data Issues**
1. **"Unknown City" Bug**: All 14 generated Schema 4.3.0 files have `"city": "Unknown City"` in appeal addresses
2. **Phoenix Missing**: No Schema 4.3.0 file (Phase1 lacks `city_parking_authority` section)
3. **File Loading Pattern**: `city_registry.py` only loads `us-*.json` files (14/31 files loaded)
4. **City Field Mapping**: Transformation script doesn't properly map `city` field from simplified data

---

## 📊 AUDIT STATUS & PROGRESS

### **Audit Comparison (V1 → V2)**
| Metric | Initial Audit | Current Audit | Change |
|--------|---------------|---------------|---------|
| **Critical Issues** | 3 | 0 | ✅ **100% resolved** |
| **High Priority** | 5 | 4 | ✅ **20% resolved** |
| **Medium Priority** | 8 | 8 | ⚠️ **No change** |
| **Overall Score** | 6/10 | 7/10 | ✅ **+1 point improvement** |

### **Resolved Critical Issues**
1. ✅ **Broken Import Statements** - All imports corrected in `app.py`
2. ✅ **Missing Service Import** - `stripe_service` imports fixed in checkout/webhooks
3. ✅ **Hardcoded API Token** - Security vulnerability eliminated
4. ✅ **Backup Files** - Repository cleaned up

### **High Priority Issues (Remaining)**
1. ⚠️ **Orphaned Transcribe Endpoint Reference** - `app.py:162` documents non-existent `/api/transcribe`
2. ⚠️ **Missing Environment Template** - No `.env.template` file exists
3. ⚠️ **No Request ID Tracking** - Error handler returns `request_id: "N/A"`
4. ⚠️ **Weak Admin Authentication** - Simple header-based auth in `admin.py`

### **Cities Data Audit Summary**
- **Total Files**: 31 JSON files in `cities/` directory
- **Schema 4.3.0 Files**: 14 generated (matching `us-*.json` pattern)
- **Phase 1 Files**: 15 source files (with `_phase1.json` suffix)
- **Critical Issue**: Only 14/31 files loaded by application (file pattern mismatch)

---

## 📁 CRITICAL FILES REFERENCE

### **Backend Core Services**
```
backend/src/services/
├── city_registry.py           # ✅ COMPLETE - Schema 4.3.0 city matching
├── citation.py                # ✅ UPDATED - Uses CityRegistry
├── schema_adapter.py          # ✅ BUILT - Transforms rich JSON → Schema 4.3.0
├── mail.py                    # 🔄 Needs Update - Dynamic addresses
├── stripe_service.py          # ✅ COMPLETE - Payment processing
├── statement.py               # ✅ COMPLETE - DeepSeek AI refinement
└── transcription.py           # ✅ COMPLETE - OpenAI Whisper
```

### **API Routes**
```
backend/src/routes/
├── tickets.py                 # ✅ Citation validation endpoint
├── checkout.py                # ✅ Stripe checkout
├── webhooks.py                # ✅ Stripe webhook handler
├── statement.py               # ✅ AI statement refinement
├── health.py                  # ✅ Health checks
├── admin.py                   # ⚠️ Needs authentication improvement
└── transcribe.py              # ✅ Audio transcription (exists but not in app.py)
```

### **Frontend Core**
```
frontend/app/
├── page.tsx                   # Homepage (needs city detection)
├── appeal/page.tsx            # Citation form (update for multi-city)
├── lib/appeal-context.tsx     # State management (add city/section)
├── admin/page.tsx             # Admin dashboard
└── layout.tsx                 # Root layout
```

### **Data & Scripts**
```
cities/                        # City configuration files
├── *_phase1.json              # 15 source files (Phase 1 schema)
├── us-*.json                  # 14 generated files (Schema 4.3.0)
└── sf.json                    # ✅ San Francisco baseline

scripts/
├── extract_city_simple.py     # ✅ Extract simplified from Phase1
├── transform_simplified_to_schema.py  # ✅ Transform to Schema 4.3.0 (BUG)
├── batch_process_cities.py    # ✅ Batch automation
└── auto_setup_ssl.py          # SSL automation
```

### **Configuration**
```
docker-compose.yml             # ✅ Updated with health checks
backend/requirements.txt       # ✅ Python dependencies
frontend/package.json          # ✅ Next.js dependencies
Makefile                       # Build/deployment commands
```

---

## 🎯 TASK QUEUE & PRIORITIES

### **🔴 COMPLETED PRIORITIES ✅**
1. ✅ **Documentation Consolidation** - Created single source of truth `AI_START_HERE.md`
2. ✅ **Updated Coordination** - `AI_COORDINATION.md` references single source

### **🚨 IMMEDIATE PRIORITIES (Next Session)**
1. **Fix "Unknown City" Bug** - Update transformation script and schema adapter
2. **Fix Phoenix Data** - Add `city_parking_authority` section or modify extraction
3. **Regenerate Schema 4.3.0 Files** - Run corrected pipeline on all 15 cities
4. **Test Multi-City Validation** - Verify CityRegistry works with all cities

### **🚧 CURRENT SPRINT: Phase 0 Foundation**
| Task | Status | Description |
|------|--------|-------------|
| **0.1: City Registry** | ✅ Complete | Schema 4.3.0 implemented |
| **0.2: Citation Service** | ✅ Complete | Integrated with CityRegistry |
| **0.3: Schema Adapter** | 🟡 In Progress | **BUG: City field transformation** |
| **0.4: Mail Service** | 🔜 Next | Update for dynamic addresses |
| **0.5: Frontend** | 🔜 Next | Multi-city detection |

### **📋 BACKLOG - By Phase**

#### **Phase 1: Backend Core Services** (Week 1-2) ✅ **COMPLETE**
- ✅ TASK-101: Citation Validation Service
- ✅ TASK-102: Stripe Checkout Integration
- ✅ TASK-103: Stripe Webhook Handler
- ✅ TASK-104: DeepSeek Statement Refinement
- ✅ TASK-105: OpenAI Whisper Transcription
- ✅ TASK-106: Lob Mail Service

#### **Phase 2: API Routes** (Week 2-3) ✅ **COMPLETE**
- ✅ TASK-201: Citation Validation Endpoint
- ✅ TASK-202: Transcription Endpoint
- ✅ TASK-203: Statement Refinement Endpoint
- ✅ TASK-204: Session Status Endpoint

#### **Phase 3: Frontend Implementation** (Week 3-4) 🔜 **NEXT**
- TASK-301: Landing Page Redesign
- TASK-302: Citation Entry Page
- TASK-303: Photo Upload Component
- TASK-304: Voice Recorder Component
- TASK-305: Evidence Selector
- TASK-306: Letter Review Page
- TASK-307: Signature Component
- TASK-308: Checkout Page
- TASK-309: Success Page
- TASK-310: Terms of Service
- TASK-311: Privacy Policy

#### **Phase 4: Integration & Testing** (Week 4-5)
- TASK-401: Appeal Flow State Management
- TASK-402: API Client Library
- TASK-403: Backend Unit Tests
- TASK-404: End-to-End Tests

#### **Phase 5: Production Deployment** (Week 5-6)
- TASK-501: Production Environment Setup
- TASK-502: Stripe Production Setup
- TASK-503: Deployment Scripts
- TASK-504: Monitoring Setup

---

## 🚀 DEPLOYMENT COMMANDS

### **Standard Deploy (Most Used)**
```bash
cd "C:\Comapnyfiles\provethat.io\FightSFTickets_Starter_Kit"
tar -czf /tmp/project-deploy.tar.gz --exclude=node_modules --exclude=.next --exclude=__pycache__ --exclude=.git --exclude=credentials --exclude='*.tar.gz' backend frontend docker-compose.yml Makefile
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/project-deploy.tar.gz root@178.156.215.100:/var/www/fightcitytickets/
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@178.156.215.100 "cd /var/www/fightcitytickets && tar -xzf project-deploy.tar.gz && docker-compose down && docker-compose up -d --build --force-recreate"
```

### **Quick Commands**
```bash
# Restart services
ssh root@178.156.215.100 "cd /var/www/fightcitytickets && docker-compose restart"

# View logs
ssh root@178.156.215.100 "cd /var/www/fightcitytickets && docker-compose logs -f"

# Health check
ssh root@178.156.215.100 "curl -s http://localhost:8000/health"

# Check status
ssh root@178.156.215.100 "cd /var/www/fightcitytickets && docker-compose ps"
```

### **Local Development**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose up -d --build --force-recreate api

# Run tests
cd backend && python -m pytest tests/
```

---

## 📝 SESSION WORK TEMPLATE

**Every session should follow this format:**

```
### Session Goal: [Phase].[Step] - [Specific Task]
**Reference**: [Architectural Bible Section]
**Files to Modify**: [List of files]
**Success Criteria**: [How to know task is complete]
**Testing Required**: [What tests to write/run]
**Deploy Needed**: [Yes/No - if yes, run standard deploy]
**Next Session**: [What comes after this]
```

### **Example Session**
```
### Session Goal: 0.3.1 - Fix "Unknown City" Bug in Transformation
**Reference**: Phase 0: Schema Adapter & Data Extraction
**Files to Modify**:
- `scripts/transform_simplified_to_schema.py` (lines 90-120)
- `backend/src/services/schema_adapter.py` (line 908)
**Success Criteria**: Generated Schema 4.3.0 files have correct city names (not "Unknown City")
**Testing Required**: Run transformation on LA phase1 file, verify city field
**Deploy Needed**: No (local data transformation only)
**Next Session**: 0.3.2 - Regenerate all Schema 4.3.0 files
```

---

## 🤝 COORDINATION GUIDELINES

### **AI Coordination Status**
- **AI Assistant #1 (Auto)**: Working backwards through audit items
- **Other AI**: Currently editing `backend/src/app.py` - **DO NOT TOUCH**
- **File Edit Status**:
  - ✅ `backend/src/middleware/` - Safe to edit
  - ✅ `docker-compose.yml` - Safe to edit
  - ✅ `backend/requirements.txt` - Safe to edit
  - ⚠️ `backend/src/app.py` - **OTHER AI EDITING - DO NOT TOUCH**
  - ⚠️ `backend/src/routes/admin.py` - Available for work
  - ⚠️ `backend/tests/` - Available for work

### **Coordination Rules**
1. **Check `AI_COORDINATION.md`** before starting work
2. **Add your entries** when you start/finish items
3. **Mark conflicts** if editing a file someone else is working on
4. **Update status** when you complete items
5. **Leave TODO notes** for other AI if integration is needed

### **Middleware Ready for Integration**
1. **Request ID Middleware** (`backend/src/middleware/request_id.py`)
   - TODO: Import in `app.py`, add `app.add_middleware(RequestIDMiddleware)`
   - TODO: Update error handler to use `get_request_id(request)`

2. **Rate Limiting Middleware** (`backend/src/middleware/rate_limit.py`)
   - TODO: Install `pip install slowapi==0.1.9`
   - TODO: Add to `app.py`: `app.state.limiter = get_rate_limiter()`

---

## ⚠️ IMPORTANT NOTES & WARNINGS

### **UPL Compliance (NON-NEGOTIABLE)**
Every frontend page must:
- ❌ NOT recommend specific evidence
- ❌ NOT promise outcomes
- ❌ NOT provide legal advice
- ✅ Show disclaimer where appropriate
- ✅ Let user make all decisions

### **Development Rules**
1. **Always edit locally first** - Server edits lost on deploy
2. **Full rebuild required** for Next.js changes (2-3 minute wait)
3. **Test after deploy** at https://fightcitytickets.com
4. **Schema 4.3.0 is strict** - No empty strings, union rules enforced
5. **Phone confirmation** required when specified in schema
6. **Conversion focus** - Belief-to-completion rate is north star metric

### **API Keys Required**
- `STRIPE_SECRET_KEY` - Payment processing
- `STRIPE_WEBHOOK_SECRET` - Webhook verification
- `LOB_API_KEY` - Mail service
- `DEEPSEEK_API_KEY` - Statement refinement
- `OPENAI_API_KEY` - Voice transcription

### **Test Mode vs Live Mode**
- **Development**: Use `sk_test_` (Stripe), `test_` (Lob)
- **Production**: Use `sk_live_` (Stripe), `live_` (Lob)
- **Test Card**: `4242424242424242`

---

## 🔧 TECHNICAL DETAILS

### **Schema 4.3.0 Structure**
```json
{
  "city_id": "us-ca-los_angeles",
  "name": "Los Angeles",
  "jurisdiction": "city",
  "citation_patterns": [{
    "regex": "^[0-9A-Z]{6,11}$",
    "section_id": "ladot_pvb",
    "description": "Los Angeles parking citation format"
  }],
  "appeal_mail_address": {
    "status": "complete",
    "department": "Parking Violations Bureau",
    "address1": "P.O. Box 30420",
    "city": "Los Angeles",  // ❌ CURRENT BUG: "Unknown City"
    "state": "CA",
    "zip": "90030-0968",
    "country": "US"
  },
  "phone_confirmation_policy": {
    "required": true,
    "confirmation_message": "Call to confirm mailing address"
  },
  "sections": {
    "ladot_pvb": {
      "name": "LADOT Parking Violations Bureau"
    }
  },
  "verification_metadata": {
    "last_updated": "2025-12-24",
    "confidence_score": 0.9
  }
}
```

### **City Data Pipeline**
```
Phase1 JSON (*_phase1.json)
    ↓ extract_city_simple.py
Simplified JSON (city_id.json)
    ↓ transform_simplified_to_schema.py
Schema 4.3.0 JSON (us-*.json)
    ↓ city_registry.py
CityRegistry.load_cities()
```

### **Known Bugs to Fix**
1. **"Unknown City" in appeal_mail_address.city** - Schema adapter defaults
2. **Phoenix missing city_parking_authority** - Phase1 data issue
3. **File loading pattern** - Only `us-*.json` files loaded
4. **city_id field in appeal_mail_address** - Should be `city`

---

## 📞 CONTACT & REFERENCES

### **Live Server**
- **IP**: 178.156.215.100
- **SSH**: `ssh root@178.156.215.100`
- **Directory**: `/var/www/fightcitytickets/`
- **Services**:
  - API: http://localhost:8000
  - Frontend: http://localhost:3000
  - Database: PostgreSQL on localhost:5432

### **Documentation Files**
- `docs/DEVELOPMENT_PLAN.md` - Complete roadmap (weeks 1-9)
- `docs/TASK_QUEUE.md` - Detailed task tracking
- `docs/DEPLOYMENT_GUIDE.md` - Deployment instructions
- `CITIES_AUDIT.md` - City data analysis
- `REPO_AUDIT_V2.md` - Security/code audit
- `AUDIT_COMPARISON.md` - Progress tracking

### **External References**
- **Original Project**: https://github.com/Ghostmunday/FightCityTickets
- **Stripe Dashboard**: https://dashboard.stripe.com
- **Lob Dashboard**: https://dashboard.lob.com
- **Hetzner Cloud**: https://console.hetzner.cloud

---

## 🎯 CURRENT SESSION FOCUS

### **Documentation Consolidation Complete ✅**
- ✅ **Single source of truth created**: `AI_START_HERE.md` now contains all project context (459 lines)
- ✅ **All MD files consolidated**: 7+ MD files consolidated into one (no need to read multiple files)
- ✅ **Coordination updated**: `AI_COORDINATION.md` references single source and tracks current work
- ✅ **References added**: All major MD files point to `AI_START_HERE.md` for AI assistants
- ✅ **Session template**: Clear format for all future AI sessions

**Impact**: Any AI assistant can now read ONE file (`AI_START_HERE.md`) and have complete project context

### **Recommended Starting Point (Next Priority)**
```
### Session Goal: 0.3.1 - Fix "Unknown City" Bug
**Files**:
- `scripts/transform_simplified_to_schema.py` (update lines 90-120)
- `backend/src/services/schema_adapter.py` (modify line 908 defaults)
**Success**: Generated Schema 4.3.0 files show correct city names (not "Unknown City")
**Test**: Run on LA phase1 file, verify `city: "Los Angeles"` in output
**Deploy**: No (data transformation only)
**Next Session**: 0.3.2 - Regenerate all Schema 4.3.0 files for 15 cities
```

### **Alternative Starting Points**
1. **Fix Phoenix Data** - Add `city_parking_authority` to `phoenix_phase1.json`
2. **Update File Loading** - Modify `city_registry.py` to load all `.json` files
3. **Add Request ID Middleware** - Integrate existing middleware into `app.py`
4. **Create `.env.template`** - Quick win for configuration

---

**END OF SINGLE SOURCE OF TRUTH DOCUMENT**

*This document consolidates all MD files and provides complete context for any AI assistant or developer.*
*Consolidation completed: 2025-01-09*
*Last consolidated: 2025-01-09*
