# 🎫 FIGHTCITYTICKETS

<div align="center">

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗██╗ ██████╗ ██╗  ██╗████████╗     ██████╗██╗████████╗██╗   ██╗ ║
║   ██╔════╝██║██╔════╝ ██║  ██║╚══██╔══╝    ██╔════╝██║╚══██╔══╝╚██╗ ██╔╝ ║
║   █████╗  ██║██║  ███╗███████║   ██║       ██║     ██║   ██║    ╚████╔╝  ║
║   ██╔══╝  ██║██║   ██║██╔══██║   ██║       ██║     ██║   ██║     ╚██╔╝   ║
║   ██║     ██║╚██████╔╝██║  ██║   ██║       ╚██████╗██║   ██║      ██║    ║
║   ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝        ╚═════╝╚═╝   ╚═╝      ╚═╝    ║
║                                                              ║
║              P A R K I N G   A P P E A L S                  ║
║                  A U T O M A T E D                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**FIGHTCITYTICKETS.com**  
*Procedural compliance, not legal advice.*

[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com)

**Production Ready** • **Version 1.0.0** • **January 2026**

[Quick Start](#-quick-start) • [Architecture](#-architecture) • [Deployment](#-deployment) • [API](#-api)

</div>

---

## ✨ Overview

**FIGHTCITYTICKETS** is a production-ready SaaS platform that automates parking ticket appeals across 15+ major cities. Built with a database-first architecture, AI-powered statement refinement, and automated physical mail delivery.

### Key Features

- 🎯 **Multi-City Support** - San Francisco, Los Angeles, New York, Chicago, and more
- 🤖 **AI-Powered** - OpenAI transcription + DeepSeek statement refinement
- 💳 **Secure Payments** - Stripe integration with webhook handling
- 📮 **Physical Mail** - Automated letter delivery via Lob API
- 🧱 **Database-First** - All data persisted before payment
- 🔒 **UPL-Compliant** - Document preparation only, no legal advice

---

## ⚡ Quick Start

```bash
# Clone repository
git clone https://github.com/Ghostmonday/FightSFTickets.git
cd FightSFTickets

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker compose up --build
```

**Local URLs:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs

---

## 🏗️ Architecture

### Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS |
| **Backend** | FastAPI (Python 3.12), SQLAlchemy 2.0, Alembic |
| **Database** | PostgreSQL 16 |
| **Reverse Proxy** | Nginx (Alpine) |
| **Orchestration** | Docker, Docker Compose |
| **Payments** | Stripe API |
| **Physical Mail** | Lob API |
| **AI Services** | OpenAI (transcription), DeepSeek (reasoning) |

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Server                         │
│                  (Your Server IP/Domain)                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐   │
│  │  Nginx  │→ │   Web   │  │   API   │→ │     DB      │   │
│  │ :80,443 │  │ :3000   │  │ :8000   │  │   :5432     │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         v                    v                    v
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │ Stripe  │         │   Lob   │         │ OpenAI  │
    │Payments │         │  Mail   │         │   AI    │
    └─────────┘         └─────────┘         └─────────┘
```

---

## 🚀 Deployment

### First-Time Deployment

The application is designed to be deployed on any Linux server with Docker support.

**Minimum Requirements:**
- 2 vCPU, 4GB RAM, 20GB Disk
- Docker and Docker Compose installed
- Domain name (optional, for SSL)

### Deploy Commands

```bash
# Set deployment variables
export SERVER_IP="your-server-ip"
export SSH_USER="root"
export SSH_KEY="~/.ssh/your_key"
export DOMAIN="yourdomain.com"  # Optional
export EMAIL="your@email.com"   # For SSL certificates

# Run deployment script
./scripts/deploy-fightcity.sh

# Or deploy manually
ssh user@your-server-ip
cd /var/www/fightcitytickets
git clone https://github.com/Ghostmonday/FightSFTickets.git .
cp .env.example .env
# Edit .env with your API keys
docker compose up -d --build
```

### Environment Variables

Required in `.env`:

```bash
# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Lob
LOB_API_KEY=live_...
LOB_MODE=live

# AI Services
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...

# Database
DATABASE_URL=postgresql+psycopg://postgres:password@db:5432/fightsf
```

---

## 📡 API

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tickets/validate` | Validate citation number |
| `POST` | `/statement/refine` | AI-powered statement refinement |
| `POST` | `/checkout/create-session` | Create Stripe checkout |
| `POST` | `/webhook/stripe` | Stripe webhook handler |
| `GET` | `/health` | Health check |
| `GET` | `/status` | Detailed status |

**Full API Documentation:** http://localhost:8000/docs

---

## 🧪 Testing

```bash
# Backend tests
docker compose exec api pytest

# Integration tests
docker compose exec api pytest tests/test_e2e_integration.py

# Frontend tests
cd frontend && npm test
```

---

## 🛠️ Operations

### Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f web
docker compose logs -f db
```

### Common Commands

```bash
# Restart services
docker compose restart api
docker compose restart web

# Rebuild after changes
docker compose up -d --build

# Database backup
docker compose exec db pg_dump -U postgres fightsf > backup_$(date +%Y%m%d).sql

# Database restore
docker compose exec -T db psql -U postgres fightsf < backup.sql
```

### Health Checks

```bash
# API health
curl http://localhost/api/health

# Database
docker compose exec db pg_isready -U postgres
```

---

## 🧰 Diagnostics (Local Connectivity)

Use these tools when the browser shows `ERR_CONNECTION_RESET` for
`http://localhost` or `http://127.0.0.1:3000` and containers appear healthy.

### Tools

- `scripts/diagnostics/debug_connection.py`
  - Full diagnostic run (TCP/HTTP checks, container networking, nginx logs).
- `scripts/diagnostics/test_connection.sh`
  - Quick smoke test for listener and nginx ↔ web reachability.

### Usage

```bash
sudo python3 /home/evan/Documents/Projects/FightSFTickets/scripts/diagnostics/debug_connection.py
```

```bash
sudo bash /home/evan/Documents/Projects/FightSFTickets/scripts/diagnostics/test_connection.sh
```

### Notes for AI operators

- Clear `/home/evan/Documents/Projects/FightSFTickets/.cursor/debug.log` before each run.
- Do not log secrets or API keys.
- Keep instrumentation until a post-fix verification run succeeds.

---

## 🔒 Legal Compliance

**FIGHTCITYTICKETS is NOT a law firm.**

- Document preparation service only
- No legal advice provided
- Users make all decisions
- UPL-compliant architecture

See `CIVIL_SHIELD_COMPLIANCE_AUDIT.md` for full compliance details.

---

## 📊 Project Structure

```
FightSFTickets/
├── frontend/          # Next.js 15 frontend
│   ├── app/           # App router pages
│   └── components/    # React components
├── backend/           # FastAPI backend
│   ├── src/
│   │   ├── routes/    # API endpoints
│   │   ├── services/  # Business logic
│   │   └── models/    # SQLAlchemy models
│   └── alembic/       # Database migrations
├── nginx/             # Nginx configuration
└── docker-compose.yml # Production orchestration
```

---

## 🛡️ Resilience & Failover

This section describes the system's resilience features and failover behavior.

### Health Check Endpoints

| Endpoint | Purpose | Checks |
|----------|---------|--------|
| `/health` | Liveness | Service is running (no dependency check) |
| `/health/ready` | Readiness | Database connectivity (traffic gate) |
| `/health/detailed` | Diagnostics | Full service status including optional dependencies |

**Validation:**
```bash
# Liveness check
curl http://localhost/health
# {"status":"ok","timestamp":"..."}

# Readiness check (fails if DB unavailable)
curl http://localhost/health/ready
# {"status":"ready","timestamp":"..."}

# Detailed status
curl http://localhost/health/detailed
```

### Fallback Behavior

| Layer | Fallback | Trigger |
|-------|----------|---------|
| **Frontend** | Error boundary UI with recovery options | Route errors, API failures |
| **Backend API** | Degraded responses, graceful third-party degradation | Stripe/Lob/AI unavailable |
| **Nginx** | Maintenance HTML / API JSON fallback | 502, 503, 504 errors |
| **Docker** | Container restart on health check failure | Readiness check fails |

### External Service Resilience

- **Stripe**: 3 retries with exponential backoff, 30s timeout
- **Lob**: 3 retries with exponential backoff, 30s timeout  
- **DeepSeek AI**: 3 retries with exponential backoff, 60s timeout, local fallback

### Test Plan

1. **Health checks:**
   ```bash
   curl http://localhost/health && curl http://localhost/health/ready
   ```

2. **API outage simulation:**
   ```bash
   docker compose stop api
   # Verify nginx serves maintenance.html
   # Verify API fallback JSON is served
   ```

3. **Frontend error boundary:**
   - Trigger an API error and verify the error UI renders

---

## 📄 License

Proprietary. See `LICENSE` file for details.

---

<div align="center">

```
┌──────────────────────────────────────────────────────────────┐
│  Built for speed. Engineered for compliance. Designed to win  │
└──────────────────────────────────────────────────────────────┘
```

**FIGHTCITYTICKETS.com** • [⬆ Back to Top](#-fightcitytickets)

</div>
