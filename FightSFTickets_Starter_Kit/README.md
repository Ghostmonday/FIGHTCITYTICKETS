# FightCityTickets - Multi-City Parking Ticket Appeal System

**Status**: 🚀 **PRODUCTION READY** | **Version**: 1.0.0 | **Last Updated**: 2025-01-09

**🤖 AI Assistant Note**: For AI assistants working on this project, please read `AI_START_HERE.md` first - it contains the complete consolidated project context and serves as the single source of truth.

## 🎉 Project Overview

FightCityTickets.com is a complete, production-ready SaaS application that automates parking ticket appeals for 15+ cities via physical mail. The system provides an end-to-end solution for users to submit evidence, record their story, receive AI-drafted appeal letters, and have them professionally printed and mailed via Lob API.

### ✨ Key Features
- **Complete Appeal Flow**: Citation entry → Photo upload → Voice recording → Letter review → Signature → Payment → Success
- **State Management**: Persistent multi-step form with session storage
- **Real Payment Processing**: Stripe integration with database-first architecture
- **Physical Mailing**: Lob API integration for professional letter printing and mailing
- **AI Integration**: Audio transcription and statement refinement
- **Legal Compliance**: UPL-compliant with complete Terms of Service and Privacy Policy
- **Professional UI**: Modern, responsive design with Tailwind CSS

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  External       │
│   Next.js 14    │◄──►│   FastAPI       │◄──►│  Services       │
│   TypeScript    │    │   Python        │    │                 │
│   Tailwind CSS  │    │   SQLAlchemy    │    │  • Stripe       │
│   React 18      │    │   Alembic       │    │  • Lob          │
└─────────────────┘    └─────────────────┘    │  • AI Services  │
                                              └─────────────────┘
```

## 🚀 DEPLOY NOW - Hetzner Cloud (Recommended)

### Automated Deployment (15 minutes)

Your application is ready for immediate deployment to Hetzner Cloud:

```bash
# Step 1: Set your Hetzner API token
export HETZNER_API_TOKEN="YOUR_HETZNER_API_TOKEN"

# Step 2: Optional - Set your domain
export DOMAIN="yourdomain.com"

# Step 3: Run deployment script
cd FightSFTickets_Starter_Kit
chmod +x scripts/deploy_hetzner.sh
./scripts/deploy_hetzner.sh
```

**The script will automatically:**
- ✅ Create Hetzner Cloud server (CX21: 2 vCPU, 4GB RAM)
- ✅ Install Docker and all dependencies
- ✅ Configure firewall and security
- ✅ Deploy your application
- ✅ Start all services (frontend, backend, database, nginx)
- ✅ Run database migrations

**You'll need these API keys (get them ready):**
- Stripe: https://dashboard.stripe.com/apikeys
- Lob: https://dashboard.lob.com/settings/keys
- OpenAI: https://platform.openai.com/api-keys
- DeepSeek: https://platform.deepseek.com/api-keys

**📚 Deployment Guides:**
- **Quick Start:** `DEPLOY_NOW.md` ⭐ Start here!
- **Complete Guide:** `docs/DEPLOYMENT_GUIDE.md`
- **Service Integration:** `docs/SERVICE_INTEGRATION_CHECKLIST.md`
- **Archived Guides:** See `docs/archive/` for historical documentation

---

## 🚀 Alternative: Manual Setup

### Option 1: Docker (Recommended for Development & Production)
```bash
# Clone and navigate to project
cd FightSFTickets_Starter_Kit

# Copy environment templates
cp .env.template .env
# Edit .env with your API keys (see Configuration section)

# Start all services
docker compose up --build

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - Health Check: http://localhost:8000/health
```

### Option 2: Manual Setup
```bash
# Backend Setup
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend Setup
cd ../frontend
npm install

# Start Backend (in one terminal)
cd backend
uvicorn src.app:app --reload --port 8000

# Start Frontend (in another terminal)
cd frontend
npm run dev
```

## 📁 Project Structure

```
FightSFTickets_Starter_Kit/
├── frontend/                    # Next.js 14 frontend application
│   ├── app/                     # App router directory
│   │   ├── appeal/              # Complete appeal flow pages
│   │   │   ├── camera/          # Photo upload page
│   │   │   ├── checkout/        # Payment page with user info
│   │   │   ├── review/          # Letter review & AI polish
│   │   │   ├── signature/       # Signature capture
│   │   │   └── voice/           # Voice recording & transcription
│   │   ├── terms/               # Terms of Service page
│   │   ├── privacy/             # Privacy Policy page (CCPA compliant)
│   │   ├── success/             # Success confirmation page
│   │   ├── lib/                 # Utilities & hooks
│   │   │   ├── api.ts           # Complete API client library
│   │   │   └── appeal-context.tsx # State management with session storage
│   │   └── components/          # Reusable components
├── backend/                     # FastAPI backend service
│   ├── src/
│   │   ├── routes/              # API endpoints
│   │   │   ├── checkout.py      # Payment processing with database-first flow
│   │   │   ├── tickets.py       # Citation validation
│   │   │   ├── transcribe.py    # Audio transcription
│   │   │   ├── statement.py     # AI statement refinement
│   │   │   └── webhooks.py      # Stripe webhook handling
│   │   ├── services/            # Business logic
│   │   │   ├── stripe_service.py # Stripe integration
│   │   │   ├── mail.py          # Lob mailing service
│   │   │   ├── citation.py      # Citation validation logic
│   │   │   └── webhook_errors.py # Dead-letter queue system
│   │   ├── models/              # Database models
│   │   └── middleware/          # Rate limiting & security
│   ├── alembic/                 # Database migrations
│   └── tests/                   # Comprehensive test suite
├── scripts/                     # Deployment & utility scripts
│   └── deploy_prod.sh           # Production deployment script
├── credentials/                 # Service account credentials
├── docs/                        # Project documentation
└── docker-compose.yml           # Docker orchestration
```

## ⚙️ Configuration

### Required API Keys
1. **Stripe** - Payment processing
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET`

2. **Lob** - Physical letter mailing
   - `LOB_API_KEY`

3. **AI Services** - Transcription & refinement
   - `OPENAI_API_KEY` (or alternative)

4. **Database** - PostgreSQL (optional, SQLite for development)
   - `DATABASE_URL`

### Environment Setup
```bash
# Development and Production
cp .env.template .env
# Edit .env with your API keys for your environment
```

## 🔧 Development

### Running Tests
```bash
# Backend tests
cd backend
pytest tests/ -v --cov=src

# Frontend development
cd frontend
npm run dev
```

### Database Migrations
```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🚀 Deployment

### Recommended: Automated Hetzner Cloud Deployment ⭐

**Ready to deploy in 3 commands:**
```bash
export HETZNER_API_TOKEN="YOUR_HETZNER_API_TOKEN"
cd FightSFTickets_Starter_Kit
./scripts/deploy_hetzner.sh
```

**Time:** ~15 minutes | **Cost:** ~$7/month | **Difficulty:** ⭐ Easy

See `DEPLOY_NOW.md` for complete quick start guide.

### Alternative: Manual Deployment

For other hosting providers:
```bash
# Using the provided deployment script
cd FightSFTickets_Starter_Kit
./scripts/deploy_prod.sh

# Or manually
docker compose -f docker-compose.prod.yml up --build -d
```

### Update Existing Deployment

When you make code changes:
```bash
SERVER_IP=xxx.xxx.xxx.xxx ./scripts/update_deployment.sh
```

### Deployment Documentation

- **Quick Start:** `DEPLOY_NOW.md` - Deploy in 15 minutes
- **Complete Guide:** `docs/DEPLOYMENT_GUIDE.md` - Step-by-step instructions
- **Service Integration:** `docs/SERVICE_INTEGRATION_CHECKLIST.md` - API setup
- **Scripts Guide:** `scripts/README.md` - All deployment scripts
- **Deployment Summary:** `DEPLOYMENT_SUMMARY.md` - Overview and costs
- **Ready Status:** `DEPLOYMENT_COMPLETE.md` - Everything you need

### Deployment Checklist
- [ ] Have Hetzner API token ready
- [ ] Get API keys: Stripe, Lob, OpenAI, DeepSeek
- [ ] Run: `./scripts/deploy_hetzner.sh`
- [ ] Configure DNS to point to server IP
- [ ] Set up SSL: `certbot --nginx -d yourdomain.com`
- [ ] Configure Stripe webhook
- [ ] Test complete payment flow
- [ ] Switch to live API keys when ready

## 📊 Monitoring & Maintenance

### Health Checks
- **API Health**: `GET /health`
- **Database Connection**: Automatic health check
- **External Services**: Stripe & Lob connectivity checks

### Logging
- Structured JSON logging for production
- Request ID tracking for debugging
- Error aggregation and alerting

### Performance Monitoring
- Rate limiting metrics
- Response time tracking
- Error rate monitoring

## 🔒 Security

### Implemented Security Measures
- **Rate Limiting**: Protection against abuse
- **Input Validation**: Pydantic models for all endpoints
- **Webhook Security**: Stripe signature verification
- **Database Security**: SQL injection protection via SQLAlchemy
- **CORS Configuration**: Restricted origins
- **Environment Separation**: Development vs production configuration

### Compliance
- **UPL Compliance**: No legal advice, user makes all decisions
- **CCPA Compliance**: Privacy policy with California user rights
- **Payment Compliance**: PCI DSS via Stripe
- **Data Protection**: Secure storage and transmission

## 📈 Scaling Considerations

### Horizontal Scaling
- Stateless backend services
- Database connection pooling
- Redis for session storage (if needed)
- Load balancer configuration

### Performance Optimization
- Database indexing on frequently queried fields
- Query optimization and caching
- CDN for static assets
- Image optimization and compression

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify `DATABASE_URL` in environment variables
   - Check database service is running
   - Run migrations: `alembic upgrade head`

2. **Payment Processing Failures**
   - Verify Stripe API keys are correct
   - Check webhook endpoint configuration
   - Test with Stripe test mode

3. **Frontend Build Errors**
   - Clear Next.js cache: `rm -rf .next`
   - Reinstall dependencies: `npm install`
   - Check TypeScript compilation

### Getting Help
- Check the `docs/` directory for detailed documentation
- Review `IMPLEMENTATION_STATUS.md` for current status
- Examine logs for error details

## 📄 License & Legal

### Important Legal Notice
FightCityTickets is not a law firm and does not provide legal advice. We are a document preparation service that helps you format and submit your own appeal. We do not recommend specific evidence, promise outcomes, or provide legal representation. You are responsible for the content of your appeal.

### Compliance Documents
- [Terms of Service](/terms)
- [Privacy Policy](/privacy) (CCPA compliant)

## 🎯 Project Status

**Completion**: 100% ✅  
**Production Readiness**: Ready for deployment  
**Last Major Update**: Jules' implementation (2025-12-22)  
**Key Contributors**: AI-assisted development with critical contributions from Jules

### What Was Recently Completed (Jules' Work)
1. ✅ Complete state management with session storage
2. ✅ Real API integration across all frontend components
3. ✅ Database-first payment flow (Intake/Draft before Stripe)
4. ✅ Legal compliance pages (Terms & Privacy)
5. ✅ Production deployment scripts and configuration
6. ✅ Enhanced error handling and testing

---

## 🎯 Deployment Status

**The FightCityTickets application is 100% complete and ready for immediate production deployment.**

### ✅ What's Ready
- ✅ **Automated Hetzner Cloud deployment** - One command deploys everything
- ✅ **Complete documentation** - Quick start to advanced guides
- ✅ **Service integrations** - Stripe, Lob, OpenAI, DeepSeek ready
- ✅ **Update/rollback scripts** - Easy maintenance and recovery
- ✅ **Security configured** - Firewall, SSL, rate limiting
- ✅ **Production tested** - All critical paths verified

### 🚀 Deploy Now
```bash
export HETZNER_API_TOKEN="YOUR_HETZNER_API_TOKEN"
./scripts/deploy_hetzner.sh
```

**Time to deploy:** 15 minutes | **Monthly cost:** ~$7 + variable | **Difficulty:** ⭐ Easy

For deployment assistance, see:
- `DEPLOY_NOW.md` - Quick start guide ⭐
- `DEPLOYMENT_COMPLETE.md` - Everything you need
- `docs/DEPLOYMENT_GUIDE.md` - Complete instructions