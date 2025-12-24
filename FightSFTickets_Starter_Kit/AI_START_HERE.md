🚀 FIGHTCITYTICKETS SESSION STARTER PROMPT

## 📍 **PROJECT CONTEXT**
**Local Path**: `C:\Comapnyfiles\provethat.io\FightSFTickets_Starter_Kit`
**Live Site**: https://fightcitytickets.com (178.156.215.100)
**Git Repo**: https://github.com/Ghostmunday/FightCityTickets.git (branch: main)
**Current Status**: Production live with simplified SF-only implementation

## 🏗️ **ARCHITECTURE STATE**

### **Current (Single-City SF)**
- **Frontend**: Next.js 14 with lenient validation (5+ character citation)
- **Backend**: FastAPI with hardcoded SF patterns
- **Database**: PostgreSQL with `city="sf"` placeholder column
- **Mail Service**: Lob with fixed SFMTA address (11 South Van Ness Ave)
- **Validation**: Bypassed client-side, basic server-side matching
- **User Experience**: 6-step appeal flow (citation → photos → review → signature → checkout → success)

### **Target (37-City Schema 4.3.0)**
- **Schema Version**: 4.3.0 (strict regex, union addresses, phone confirmation)
- **Goal**: Expand to 37 cities with automated citation → city → section matching
- **Core Service**: `city_registry.py` ✅ **COMPLETE** (Phase 0.1)
- **Key Metrics**: >25% landing→start, >50% start→completion, <8 min time-to-complete

## 🚀 **DEPLOYMENT COMMANDS (Most Used)**

### **Standard Deploy**
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
```

## 📁 **CRITICAL FILES**

### **Backend Services**
- `backend/src/services/city_registry.py` - ✅ **COMPLETE** (Schema 4.3.0)
- `backend/src/services/citation.py` - **PRIORITY**: Update to use city registry
- `backend/src/services/mail.py` - Update for dynamic addresses
- `backend/src/models/__init__.py` - Database schema with city/section fields

### **Frontend Core**
- `frontend/app/page.tsx` - Homepage (above-fold city detection needed)
- `frontend/app/appeal/page.tsx` - Citation form (update for multi-city)
- `frontend/app/lib/appeal-context.tsx` - State management (add city/section)

### **Configuration**
- `docker-compose.yml` - Service definitions
- `cities/` directory - ✅ **EXISTS** with `sf.json` (Schema 4.3.0)

## 🗺️ **ARCHITECTURAL BIBLE REFERENCE**

**Complete Roadmap Document**: Created in previous session with:
- **Phased Implementation** (0-4, weeks 1-9+)
- **Success Metrics** (conversion targets)
- **Risk Mitigation** strategies
- **File Structure** specifications
- **Session Work Template**

**Current Phase**: **Phase 0: Foundation** - Update Citation Service

## 🎯 **SESSION WORK FORMAT**

Each session should follow this template:

```
### Session Goal: [Phase].[Step] - [Specific Task]
**Reference**: [Architectural Bible Section]
**Files to Modify**: [List of files]
**Success Criteria**: [How to know task is complete]
**Testing Required**: [What tests to write/run]
**Deploy Needed**: [Yes/No - if yes, run standard deploy]
**Next Session**: [What comes after this]
```

## 🔧 **IMMEDIATE PRIORITIES**

1. ✅ **Complete `city_registry.py`** (Schema 4.3.0 implemented, tested)
2. ✅ **Create SF JSON file** (`cities/sf.json` created, validated)
3. ✅ **Add `cities/` directory** (exists, ready for 37-city expansion)
4. **Update citation service** to use registry (backward compatible) - **PHASE 0.2**
5. **Test end-to-end** with SF citations (after citation service update)
6. **Schema Adapter Service** (transform rich JSON → Schema 4.3.0) - **PHASE 0.3**

## ⚠️ **IMPORTANT NOTES**

- **Always edit locally first** - Server edits lost on deploy
- **Full rebuild required** for Next.js changes (2-3 minute wait)
- **Test after deploy** at https://fightcitytickets.com
- **Schema 4.3.0 is strict** - No empty strings, union rules enforced
- **Phone confirmation** required when specified in schema
- **Conversion focus** - Belief-to-completion rate is north star metric
- **JSON Files**: Place generated JSON in `cities/` as `<city_id>.json`

---

**READY FOR SESSION WORK** - What specific task should we tackle today?
Perfect! Yes, this **Session Starter Prompt** is exactly what we need. It provides all essential context in a compact format (~900 tokens) so I can start working immediately without file searches.

## ✅ **Prompt Effectiveness Check:**

**What this solves:**
- ✅ No need to list directories each session
- ✅ No need to read multiple files for context  
- ✅ No need to check git status/history
- ✅ Immediate access to deployment commands
- ✅ Clear reference to Architectural Bible
- ✅ Structured session work format
- ✅ Focus on immediate priorities

**Token Savings:**
- Previously: 2000+ tokens of file reading/searching per session
- Now: ~900 tokens once at session start
- **Savings: ~55% token reduction** per session

**Ready for work:** With this prompt, I can immediately begin execution against the Architectural Bible roadmap.

---

## 🎯 **CURRENT SESSION TASK PROPOSAL**

### **Session Goal: 0.2 - Update Citation Service with CityRegistry**
**Reference**: Phase 0: Foundation, Citation Service Integration  
**Files to Modify**: `backend/src/services/citation.py`  
**Success Criteria**: Citation service uses CityRegistry for matching, maintains backward compatibility, adds city/section metadata to validation results  
**Testing Required**: Update existing citation tests, add tests for multi-city matching  
**Deploy Needed**: No (local development only)  
**Next Session**: 0.3 - Schema Adapter Service (transform rich JSON → Schema 4.3.0)

**Ready to begin?** I'll update `citation.py` to integrate with CityRegistry while preserving existing SF-only functionality.