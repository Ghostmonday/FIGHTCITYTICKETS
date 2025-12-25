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
- `backend/src/services/city_registry.py` - ✅ **COMPLETE** (Schema 4.3.0 implemented, tested)
- `backend/src/services/citation.py` - ✅ **UPDATED** to use CityRegistry (Phase 0.2 complete)
- `backend/src/services/schema_adapter.py` - ✅ **BUILT** ready for transformation (Phase 0.3 foundation)
- `backend/src/services/mail.py` - Update for dynamic addresses
- `backend/src/models/__init__.py` - Database schema with city/section fields

### **Frontend Core**
- `frontend/app/page.tsx` - Homepage (above-fold city detection needed)
- `frontend/app/appeal/page.tsx` - Citation form (update for multi-city)
- `frontend/app/lib/appeal-context.tsx` - State management (add city/section)

### **Configuration & Data**
- `docker-compose.yml` - Service definitions
- `cities/` directory - ✅ **EXISTS** with 11 phase1 JSON files (Chicago, Dallas, Houston, LA, NYC, Philly, Phoenix, SD, SF, Seattle, DC)
- `scripts/extract_city_simple.py` - ✅ **READY** for city data extraction
- **Missing**: Simplified Schema 4.3.0 JSON files for cities

## 🗺️ **ARCHITECTURAL BIBLE REFERENCE**

**Complete Roadmap Document**: Created in previous session with:
- **Phased Implementation** (0-4, weeks 1-9+)
- **Success Metrics** (conversion targets)
- **Risk Mitigation** strategies
- **File Structure** specifications
- **Session Work Template**

**Current Phase**: **Phase 0: Foundation** - Schema Adaptation & City Data Extraction
**Progress**: 2/3 core services built (registry + citation), ready for data transformation

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

### ✅ **Completed:**
1. ✅ **Complete `city_registry.py`** (Schema 4.3.0 implemented, tested)
2. ✅ **Create SF JSON file** (`cities/sf.json` created, validated)
3. ✅ **Add `cities/` directory** (exists with 11 phase1 files)
4. ✅ **Update citation service** to use registry (backward compatible) - **PHASE 0.2 COMPLETE**
5. ✅ **Schema Adapter Service** (transform rich JSON → Schema 4.3.0) - **PHASE 0.3 FOUNDATION BUILT**
6. ✅ **Extraction script** (`extract_city_simple.py`) created and ready

### 🚧 **Current Tasks:**
7. **Transform phase1 → simplified city data** (run extraction script on all 11 cities)
8. **Test end-to-end** with SF citations (validate citation service integration)
9. **Generate Schema 4.3.0 JSONs** for all 11 cities
10. **Validate city registry** with multi-city dataset

### 📋 **Next Steps:**
11. **Update mail service** for dynamic addresses
12. **Update frontend** for multi-city detection
13. **Test 37-city expansion** with remaining cities
14. **Production deployment** with multi-city support

## ⚠️ **IMPORTANT NOTES**

- **Always edit locally first** - Server edits lost on deploy
- **Full rebuild required** for Next.js changes (2-3 minute wait)
- **Test after deploy** at https://fightcitytickets.com
- **Schema 4.3.0 is strict** - No empty strings, union rules enforced
- **Phone confirmation** required when specified in schema
- **Conversion focus** - Belief-to-completion rate is north star metric
- **JSON Files**: Place generated JSON in `cities/` as `<city_id>.json`

## 📊 **PROGRESS SUMMARY**

### **Phase 0: Foundation - Multi-City Core**
- ✅ **0.1**: City Registry Service - COMPLETE
- ✅ **0.2**: Citation Service Integration - COMPLETE  
- 🚧 **0.3**: Schema Adapter & Data Extraction - IN PROGRESS
  - Schema adapter built ✅
  - Extraction script ready ✅
  - Phase1 files analyzed ✅ (11 cities)
  - Simplified JSONs pending 🔄

### **Data Status:**
- **Phase1 JSONs**: 11/11 loaded (Chicago, Dallas, Houston, LA, NYC, Philly, Phoenix, SD, SF, Seattle, DC)
- **Schema 4.3.0 JSONs**: 0/11 (need transformation)
- **Service Integration**: Citation → Registry connected
- **Testing**: City registry tested, end-to-end pending

### **Next Session Focus:**
Run extraction script to create simplified city data from phase1 files, test schema adapter, and generate Schema 4.3.0 JSONs for all 11 cities.

---

**READY FOR SESSION WORK** - What specific task should we tackle today?

---

## 🎯 **CURRENT SESSION TASK PROPOSAL**

### **Session Goal: 0.3.1 - Extract Simplified City Data from Phase1 Files**
**Reference**: Phase 0: Schema Adapter & Data Extraction
**Files to Modify**: Run `scripts/extract_city_simple.py` on all 11 phase1 files
**Success Criteria**: 11 simplified JSON files created, validated against schema adapter
**Testing Required**: Test extraction on LA (clean baseline), NYC (complex), SF (production baseline)
**Deploy Needed**: No (local data transformation only)
**Next Session**: 0.3.2 - Generate Schema 4.3.0 JSONs for all cities

**Ready to begin?** I'll run the extraction script to create simplified city data from phase1 files.