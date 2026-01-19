# 🎫 Fight SF Tickets - Parking Ticket Appeal SaaS Platform

<div align="center">

**Production-Ready Multi-City Parking Ticket Appeal System**

[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com)

*Database-first parking ticket appeal system with AI-powered statement generation, Stripe payments, and physical mail delivery via Lob API.*

[Features](#-features) • [Architecture](#-architecture) • [Deployment](#-deployment) • [API](#-api-documentation)

</div>

---

## 📖 Overview

**Fight SF Tickets** is a production-ready SaaS platform that helps users appeal parking tickets across multiple cities. The system combines AI-powered statement generation, secure payment processing, and automated physical mail delivery to create a seamless appeal experience.

### Key Highlights

- 🎯 **Multi-City Support**: Handles parking ticket appeals for 15+ major cities
- 🤖 **AI-Powered**: OpenAI transcription and DeepSeek reasoning for statement refinement
- 💳 **Stripe Integration**: Secure payment processing with webhook handling
- 📮 **Physical Mail**: Automated letter delivery via Lob API
- 🐳 **Docker Deployment**: Production-ready containerized architecture
- 🔒 **Legal Compliance**: UPL-compliant architecture (not a law firm)

---

## ✨ Features

### Core Functionality

- **Multi-Step Appeal Flow**: Guided process from ticket upload to letter delivery
  - Camera/Photo upload for ticket documentation
  - Voice recording for appeal statement
  - AI-powered statement refinement
  - Signature capture
  - Payment processing
  - Automated letter generation and mailing

- **Citation Validation**: Database-first validation for 15+ cities including:
  - San Francisco
  - Los Angeles
  - New York
  - Chicago
  - Austin
  - Seattle
  - And more...

- **AI Statement Generation**: 
  - Voice transcription via OpenAI Whisper
  - Statement refinement using DeepSeek
  - Legal compliance checks
  - Personalized appeal letters

- **Payment Processing**:
  - Stripe integration for secure payments
  - Webhook handling for payment events
  - Multiple payment methods support

- **Physical Mail Delivery**:
  - Automated letter generation
  - Lob API integration for mail delivery
  - Delivery tracking and confirmation

### Technical Features

- **Database-First Architecture**: PostgreSQL with SQLAlchemy ORM
- **Modern Frontend**: Next.js 15 with React 19 and TypeScript
- **RESTful API**: FastAPI backend with comprehensive error handling
- **Docker Deployment**: Complete containerization with Docker Compose
- **Nginx Reverse Proxy**: Production-ready load balancing and SSL termination
- **Rate Limiting**: API protection against abuse
- **CORS Configuration**: Secure cross-origin resource sharing

---

## 🏗️ Architecture

### Technology Stack

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

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Server                         │
│                    143.198.131.213                          │
┌─────────────────────────────────────────────────────────────┐
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐  │
│  │  Nginx  │  │   Web   │  │   API   │  │     DB      │  │
│  │ :80,443 │  │ :3000   │  │ :8000   │  │   :5432     │  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────┘  │
│       │              │              │             │          │
│       └──────────────┴──────────────┴─────────────┘          │
│                     Docker Network                            │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         v                    v                    v
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │ Stripe  │         │   Lob   │         │ OpenAI  │
    │Payments │         │  Mail   │         │   AI    │
    └─────────┘         └─────────┘         └─────────┘
```

### Project Structure

```
FightSFTickets/
├── README.md                    # This file
├── .env.example                 # Environment template
├── docker-compose.yml           # Production Docker orchestration
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

## 🚀 Deployment

### Production Server Access

| Property | Value |
|----------|-------|
| **Droplet IP** | 143.198.131.213 |
| **SSH User** | root |
| **SSH Key** | `/c/Users/Amirp/.ssh/do_deploy_key` |
| **Region** | sfo3 (San Francisco) |
| **Specs** | 2 vCPU, 4GB RAM, 80GB Disk |

### Quick Deploy

```bash
# Connect to production server
ssh -i /c/Users/Amirp/.ssh/do_deploy_key root@143.198.131.213

# On server:
cd /var/www/fightcitytickets
git pull
docker compose down
docker compose up -d --build
curl http://localhost/api/health
```

### Environment Configuration

Required API Keys:

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

## 🛠️ Development

### Local Setup

```bash
# Clone and enter
git clone https://github.com/Ghostmonday/FightSFTickets.git
cd FightSFTickets

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

## 📡 API Documentation

### Service Endpoints

| Service | Port | Endpoint | Health Check |
|---------|------|----------|--------------|
| Nginx | 80, 443 | http://143.198.131.213 | - |
| Frontend | 3000 | http://143.198.131.213/ | / |
| API | 8000 | http://143.198.131.213/api/ | /health |
| Database | 5432 | db:5432 (internal) | - |

### Key API Routes

- `POST /api/tickets/validate` - Validate parking ticket citation
- `POST /api/transcribe` - Transcribe voice recording
- `POST /api/statement/refine` - AI-powered statement refinement
- `POST /api/checkout` - Create Stripe payment session
- `POST /api/webhooks/stripe` - Handle Stripe webhooks
- `POST /api/mail/send` - Send appeal letter via Lob

---

## 🗄️ Database

### Schema Overview

- **Citations**: Parking ticket information and validation
- **Appeals**: Appeal requests and status tracking
- **Payments**: Stripe payment records
- **Statements**: AI-generated appeal statements
- **Users**: User accounts and preferences

### Migrations

```bash
# Run migrations
docker compose exec api alembic upgrade head

# Create new migration
docker compose exec api alembic revision --autogenerate -m "Description"
```

---

## 🔒 Legal Compliance

**Fight SF Tickets is NOT a law firm.**

- Document preparation service only
- No legal advice provided
- Users make all decisions
- UPL-compliant architecture implemented

See `CIVIL_SHIELD_COMPLIANCE_AUDIT.md` for details.

---

## 🧪 Testing

### Running Tests

```bash
# Backend tests
docker compose exec api pytest

# Frontend tests
cd frontend
npm test

# Integration tests
docker compose exec api pytest tests/integration/
```

---

## 📊 Monitoring & Logs

### View Logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f api

# Frontend only
docker compose logs -f web

# Database
docker compose logs -f db
```

### Health Checks

```bash
# API health
curl http://localhost/api/health

# Database connection
docker compose exec db pg_isready -U postgres
```

---

## 🔧 Common Commands

```bash
# Restart service
docker compose restart api
docker compose restart web

# Rebuild after code change
docker compose up -d --build

# Database backup
docker compose exec db pg_dump -U postgres fightsf > backup_$(date +%Y%m%d).sql

# Database restore
docker compose exec -T db psql -U postgres fightsf < backup_20240101.sql

# SSH into container
docker compose exec api /bin/bash
docker compose exec web /bin/sh
```

---

## 🐛 Troubleshooting

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

## 📊 Technical Achievements

- ✅ **Production Deployment**: Live system handling real appeals
- ✅ **Multi-Service Architecture**: Docker Compose orchestration
- ✅ **AI Integration**: OpenAI + DeepSeek for statement generation
- ✅ **Payment Processing**: Stripe integration with webhooks
- ✅ **Physical Mail**: Automated letter delivery via Lob API
- ✅ **Database-First Design**: PostgreSQL with proper migrations
- ✅ **Legal Compliance**: UPL-compliant architecture

---

## 🤝 Contributing

This is a production system. For development inquiries, please contact the repository owner.

---

## 📄 License

Proprietary. See `LICENSE` file for details.

---

## 🙏 Acknowledgments

- Built for users fighting unfair parking tickets
- Designed with legal compliance in mind
- Production-ready architecture for scale

---

<div align="center">

**Last Updated**: January 2026  
**Status**: Production Ready  
**Version**: 1.0.0

[⬆ Back to Top](#-fight-sf-tickets---parking-ticket-appeal-saas-platform)

</div>
