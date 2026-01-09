# FIGHTSFTICKETS RUNBOOK

## PROJECT OVERVIEW
FightSFTickets.com is a production SaaS application that automates San Francisco parking ticket appeals via physical mail. Users submit evidence, record their story, receive AI-drafted appeal letters, and the system mails them via Lob API.

**Production Status**: Live with Stripe payments and Lob mailing integration
**Technology Stack**: Next.js 14 (frontend), FastAPI (backend), PostgreSQL (optional), Docker

## QUICK START

### Option 1: Docker (Recommended)
```bash
# Clone and navigate to project
cd FightSFTickets_Starter_Kit

# Copy environment template
cp .env.template .env
# Edit .env with your API keys (see Configuration section)

# Start all services
docker compose up --build

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - PostgreSQL: localhost:5432
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

## SERVICE PORTS & URLs

| Service | Port | Local URL | Production URL | Purpose |
|---------|------|-----------|----------------|---------|
| Frontend | 3000 | http://localhost:3000 | https://fightsftickets.com | Next.js web app |
| Backend API | 8000 | http://localhost:8000 | https://fightsftickets.com/api | FastAPI backend |
| PostgreSQL | 5432 | localhost:5432 | N/A (server only) | Database |
| Health Check | 8000 | http://localhost:8000/health | https://fightsftickets.com/health | Service health |

## DOCKER COMPOSE COMMANDS

### Basic Operations
```bash
# Start all services in foreground
docker compose up

# Start in background (detached mode)
docker compose up -d

# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes data)
docker compose down -v

# Rebuild images
docker compose up --build

# View logs
docker compose logs
docker compose logs -f  # Follow logs
docker compose logs api  # Specific service
```

### Service Management
```bash
# Start specific service
docker compose up api

# Restart service
docker compose restart api

# Execute command in running container
docker compose exec api python --version
docker compose exec db psql -U postgres -d fightsf

# View container status
docker compose ps
```

### Development Commands
```bash
# Run tests
docker compose exec api pytest

# Access database shell
docker compose exec db psql -U postgres -d fightsf

# Rebuild single service
docker compose up --build api
```

## CONFIGURATION

### Environment Variables (.env)
Create `.env` file from template:
```bash
cp .env.template .env
```

Required variables:
```env
# API Keys (get from respective dashboards)
STRIPE_SECRET_KEY=sk_test_placeholder_key_do_not_use_in_production  # Stripe test key
STRIPE_WEBHOOK_SECRET=whsec_placeholder_secret_do_not_use_in_production
LOB_API_KEY=test_...           # Lob test key
DEEPSEEK_API_KEY=sk-...        # DeepSeek API key
OPENAI_API_KEY=sk-...          # OpenAI for Whisper transcription

# Application Settings
APP_ENV=development            # development, staging, production
APP_URL=http://localhost:3000
API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Database (for Docker setup)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fightsf
DATABASE_URL=postgresql://postgres:postgres@db:5432/fightsf
```

### Test Credentials
```bash
# Stripe Test Card: 4242424242424242
# Expiry: Any future date
# CVC: Any 3 digits
# ZIP: Any 5 digits

# Lob Test Mode: No real mail sent when using test_ API key
```

## DEVELOPMENT WORKFLOW

### Backend Development
```bash
cd backend
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn src.app:app --reload --port 8000

# Run tests
pytest

# Check code quality
pytest --cov=src tests/
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Database Operations
```bash
# Using Docker Compose
docker compose exec db psql -U postgres -d fightsf

# Manual connection
psql -h localhost -p 5432 -U postgres -d fightsf

# Common SQL commands
\dt                         # List tables
\d+ table_name              # Describe table
\q                          # Quit
```

## API ENDPOINTS

### Health Check
```bash
GET /health
curl http://localhost:8000/health
```

### Ticket Processing
```bash
POST /tickets/validate
Content-Type: application/json
{
  "citation_number": "123456",
  "license_plate": "ABC123"
}

POST /tickets/draft
Content-Type: application/json
{
  "citation_number": "123456",
  "user_statement": "I was only parked for 5 minutes..."
}
```

### Checkout
```bash
POST /checkout/create-session
Content-Type: application/json
{
  "citation_number": "123456",
  "letter_text": "Appeal letter content...",
  "mail_type": "standard"  # or "certified"
}
```

## PRODUCTION DEPLOYMENT

### Server Requirements
- Ubuntu 22.04+ or similar Linux distribution
- Docker and Docker Compose installed
- Git for deployment
- Nginx for reverse proxy (optional)

### Deployment Steps
```bash
# 1. Clone repository on server
git clone <repository-url> /var/www/fightsftickets.com
cd /var/www/fightsftickets.com

# 2. Set up environment
cp .env.template .env
# Edit .env with PRODUCTION keys (not test keys!)

# 3. Start services
docker compose -f docker-compose.prod.yml up -d

# 4. Set up Nginx (example config in nginx_carticket.conf)
sudo cp nginx_carticket.conf /etc/nginx/sites-available/fightsftickets
sudo ln -s /etc/nginx/sites-available/fightsftickets /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 5. Set up SSL (Let's Encrypt)
sudo certbot --nginx -d fightsftickets.com -d www.fightsftickets.com
```

### Monitoring
```bash
# Check service status
docker compose ps
docker compose logs --tail=50

# Health checks
curl https://fightsftickets.com/health

# Database backup
docker compose exec db pg_dump -U postgres fightsf > backup_$(date +%Y%m%d).sql
```

## TROUBLESHOOTING

### Common Issues

1. **Port already in use**
```bash
# Find process using port
sudo lsof -i :3000
sudo lsof -i :8000
sudo lsof -i :5432

# Kill process
sudo kill -9 <PID>
```

2. **Docker build failures**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker compose build --no-cache
```

3. **Database connection issues**
```bash
# Check if database is running
docker compose ps db

# Check logs
docker compose logs db

# Reset database (WARNING: deletes data)
docker compose down -v
docker compose up -d
```

4. **CORS errors**
- Ensure `CORS_ORIGINS` in .env includes frontend URL
- Check browser console for exact error
- Verify backend is running on correct port

### Logs Inspection
```bash
# View all logs
docker compose logs

# Follow logs in real-time
docker compose logs -f

# Service-specific logs
docker compose logs api
docker compose logs web
docker compose logs db

# Check for errors
docker compose logs | grep -i error
docker compose logs | grep -i exception
```

## TESTING

### Smoke Test Commands
```bash
# 1. Check if services are running
docker compose ps
# Should show: api, web, db all as "Up"

# 2. Test backend health
curl http://localhost:8000/health
# Expected: {"status":"healthy","timestamp":"..."}

# 3. Test frontend accessibility
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK

# 4. Test database connection
docker compose exec db pg_isready -U postgres
# Expected: /var/run/postgresql:5432 - accepting connections

# 5. Test API endpoints
curl -X POST http://localhost:8000/tickets/validate \
  -H "Content-Type: application/json" \
  -d '{"citation_number":"123456","license_plate":"ABC123"}'
# Expected: JSON response with validation result
```

### Automated Tests
```bash
# Run all tests
docker compose exec api pytest

# Run specific test file
docker compose exec api pytest tests/test_health.py

# Run with coverage
docker compose exec api pytest --cov=src tests/

# Run in watch mode (development)
docker compose exec api ptw --runner "pytest tests/"
```

## MAINTENANCE

### Regular Tasks
```bash
# Update dependencies
cd backend && pip install -r requirements.txt --upgrade
cd ../frontend && npm update

# Backup database
docker compose exec db pg_dump -U postgres fightsf > backup_$(date +%Y%m%d_%H%M%S).sql

# Clean up Docker
docker system prune -f

# Check for security updates
npm audit
pip-audit
```

### Performance Monitoring
```bash
# Check resource usage
docker stats

# Check logs for slow queries
docker compose logs api | grep -i "slow"

# Monitor API response times
curl -w "\nTime: %{time_total}s\n" http://localhost:8000/health
```

## SECURITY NOTES

1. **Never commit `.env` file** - Contains API keys and secrets
2. **Use test keys in development** - Stripe test keys, Lob test keys
3. **Enable CORS properly** - Restrict to known origins in production
4. **Regular updates** - Keep dependencies updated for security patches
5. **Database backups** - Regular backups to prevent data loss
6. **Monitor logs** - Watch for suspicious activity

## SUPPORT & RESOURCES

- **Stripe Dashboard**: https://dashboard.stripe.com/test/dashboard
- **Lob Dashboard**: https://dashboard.lob.com/
- **DeepSeek API**: https://platform.deepseek.com/api-docs/
- **OpenAI API**: https://platform.openai.com/docs/api-reference
- **Docker Docs**: https://docs.docker.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs

## EMERGENCY PROCEDURES

### Service Down
1. Check logs: `docker compose logs`
2. Restart services: `docker compose restart`
3. Check disk space: `df -h`
4. Check memory: `free -h`

### Data Loss
1. Restore from latest backup
2. Check database volume: `docker volume ls`
3. Contact support if backup unavailable

### Security Breach
1. Rotate all API keys immediately
2. Check logs for unauthorized access
3. Update all passwords
4. Audit user accounts and permissions

---

*Last Updated: $(date)*
*Version: 1.0.0*