# FightCityTickets - Parking Ticket Appeal SaaS Platform

**Production-Ready Multi-City Parking Ticket Appeal System**

---

## Quick Start for AI Assistants

### Connect to Production Server

```bash
ssh -i /c/Users/Amirp/.ssh/do_deploy_key root@143.198.131.213
```

### Deploy Updates

```bash
# On server
cd /var/www/fightcitytickets
git pull
docker compose down
docker compose up -d --build
curl http://localhost/api/health
```

---

## Server Access

| Property | Value |
|----------|-------|
| **Droplet IP** | 143.198.131.213 |
| **SSH User** | root |
| **SSH Key** | `/c/Users/Amirp/.ssh/do_deploy_key` |
| **Region** | sfo3 (San Francisco) |
| **Specs** | 2 vCPU, 4GB RAM, 80GB Disk |

**DO Token**: Configure via `doctl auth init`

---

## Architecture

```
+--------------------------------------------------------------+
|                     Production Server                         |
|                    143.198.131.213                           |
+--------------------------------------------------------------+
|  +---------+   +---------+   +---------+   +-------------+   |
|  |  Nginx  |   |   Web   |   |   API   |   |     DB      |   |
|  |  :80,443|   | :3000   |   | :8000   |   |   :5432     |   |
|  +---------+   +---------+   +---------+   +-------------+   |
|       |              |              |             |          |
|       +--------------+--------------+-------------+          |
|                     Docker Network                            |
+--------------------------------------------------------------+
         |                    |                    |
         v                    v                    v
    +---------+         +---------+         +---------+
    | Stripe  |         |   Lob   |         | OpenAI  |
    |Payments |         |  Mail   |         |   AI    |
    +---------+         +---------+         +---------+
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS |
| **Backend** | FastAPI (Python 3.11+), SQLAlchemy 2.0, Alembic |
| **Database** | PostgreSQL 16 |
| **Reverse Proxy** | Nginx (Alpine) |
| **Containerization** | Docker, Docker Compose |
| **Payments** | Stripe API |
| **Physical Mail** | Lob API |
| **AI Services** | OpenAI (transcription), DeepSeek (reasoning) |

---

## Project Structure

```
provethat.io/
├── README.md                    # This file - START HERE
├── .env.example                 # Environment template (copy to .env)
├── .gitignore
├── docker-compose.yml           # Production Docker orchestration
├── .git/                        # Git repository
│
├── frontend/                    # Next.js 15 frontend
│   ├── app/                     # App router pages
│   │   ├── appeal/              # Multi-step appeal flow
│   │   │   ├── camera/          # Photo upload
│   │   │   ├── checkout/        # Payment
│   │   │   ├── review/          # Letter review
│   │   │   ├── signature/       # Signature capture
│   │   │   └── voice/           # Voice recording
│   │   ├── lib/                 # API client, state management
│   │   └── components/          # Reusable UI components
│   ├── Dockerfile
│   ├── package.json
│   └── next.config.js
│
├── backend/                     # FastAPI backend
│   ├── src/
│   │   ├── routes/              # API endpoints
│   │   │   ├── checkout.py      # Stripe payments
│   │   │   ├── tickets.py       # Citation validation
│   │   │   ├── transcribe.py    # Audio transcription
│   │   │   ├── statement.py     # AI statement refinement
│   │   │   └── webhooks.py      # Stripe webhooks
│   │   ├── services/            # Business logic
│   │   │   ├── stripe_service.py
│   │   │   ├── mail.py          # Lob mailing
│   │   │   └── citation.py
│   │   ├── models/              # SQLAlchemy models
│   │   └── middleware/          # Rate limiting, security
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── nginx/                       # Nginx configuration
│   ├── nginx.conf               # Main config
│   └── conf.d/                  # Site configs
│
└── CIVIL_SHIELD_COMPLIANCE_AUDIT.md
```

---

## Environment Configuration

### Required API Keys

```bash
# Stripe (Payments)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Lob (Physical Mail)
LOB_API_KEY=...

# AI Services
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=...

# Database (auto-configured in docker-compose.yml)
DATABASE_URL=postgresql://postgres:...@db:5432/fightsf
```

Copy `.env.example` to `.env` and fill in your values.

---

## Development

### Local Setup

```bash
# Clone and enter
git clone <repo>
cd provethat.io

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker compose up --build

# Available at:
# - Frontend: http://localhost:3000
# - API: http://localhost:8000
# - Health: http://localhost:8000/health
```

### Manual Development

```bash
# Backend
cd backend
python -m venv .venv
.venv/Scripts/activate  # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## Production Deployment

### Deploy to Existing Server

```bash
# From project root on local machine
ssh -i /c/Users/Amirp/.ssh/do_deploy_key root@143.198.131.213

# On server:
cd /var/www/fightcitytickets
git pull
docker compose down
docker compose up -d --build
docker compose ps

# Verify
curl http://localhost/api/health
```

### Fresh Server Setup

```bash
# 1. SSH to server
ssh -i /c/Users/Amirp/.ssh/do_deploy_key root@143.198.131.213

# 2. Install Docker
apt-get update
apt-get install -y docker.io docker-compose git
systemctl enable docker
systemctl start docker

# 3. Clone and deploy
git clone <repo> /var/www/fightcitytickets
cd /var/www/fightcitytickets
cp .env.example .env
# Edit .env with production API keys
docker compose up -d --build

# 4. Verify
curl http://localhost/api/health
```

---

## Service Endpoints

| Service | Port | Endpoint | Health Check |
|---------|------|----------|--------------|
| Nginx | 80, 443 | http://143.198.131.213 | - |
| Frontend | 3000 | http://143.198.131.213/ | / |
| API | 8000 | http://143.198.131.213/api/ | /health |
| Database | 5432 | db:5432 (internal) | - |

---

## Common Commands

```bash
# View logs
docker compose logs -f
docker compose logs -f api    # Backend only
docker compose logs -f web    # Frontend only

# Restart service
docker compose restart api
docker compose restart web

# Rebuild after code change
docker compose up -d --build

# Database migration
docker compose exec api alembic upgrade head

# Check disk usage
docker system df

# SSH into container
docker compose exec api /bin/bash
docker compose exec web /bin/sh
```

---

## Supported Cities

Currently supports parking ticket appeals for 15+ cities including:
- San Francisco
- Los Angeles
- New York
- Chicago
- Austin
- Seattle
- And more...

See `backend/src/services/citation.py` for validation patterns.

---

## Legal Compliance

**FightCityTickets is NOT a law firm.**

- Document preparation service only
- No legal advice provided
- Users make all decisions
- UPL-compliant architecture implemented

See `CIVIL_SHIELD_COMPLIANCE_AUDIT.md` for details.

---

## Troubleshooting

### Container won't start

```bash
docker compose logs api
docker compose logs web
```

### Database connection failed

```bash
docker compose restart db
docker compose exec db pg_isready -U postgres
```

### Frontend 502 Bad Gateway

```bash
docker compose logs nginx
docker compose restart web
```

### API returns 500

```bash
docker compose exec api cat /app/logs/app.log
```

---

## Backup & Recovery

```bash
# Backup database
docker compose exec db pg_dump -U postgres fightsf > backup_$(date +%Y%m%d).sql

# Restore database
docker compose exec -T db psql -U postgres fightsf < backup_20240101.sql
```

---

## Security Notes

- **NEVER** commit `.env` or API keys to git
- SSH key stored at `/c/Users/Amirp/.ssh/do_deploy_key` (keep safe!)
- Rate limiting enabled on all API endpoints
- CORS configured for production domain only
- Database not exposed externally (Docker network only)

---

## For Future AI Sessions

**START HERE.** Read this file first.

**To deploy updates:**

```bash
ssh -i /c/Users/Amirp/.ssh/do_deploy_key root@143.198.131.213
cd /var/www/fightcitytickets
git pull
docker compose down
docker compose up -d --build
curl http://localhost/api/health
```

**Required context:**
- Server IP: 143.198.131.213
- SSH key: `/c/Users/Amirp/.ssh/do_deploy_key`
- DO Token: Configured via `doctl auth init`
- All configs in `docker-compose.yml` and `.env`

---

**Last Updated**: January 10, 2026
**Status**: Production Ready