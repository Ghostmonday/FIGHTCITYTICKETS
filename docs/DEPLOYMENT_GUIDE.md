# FightSFTickets - Complete Deployment Guide

**Version:** 1.0.0  
**Last Updated:** 2025-01-09  
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Deployment Options](#deployment-options)
5. [Hetzner Cloud Deployment (Recommended)](#hetzner-cloud-deployment)
6. [Manual Deployment](#manual-deployment)
7. [Post-Deployment Configuration](#post-deployment-configuration)
8. [Service Integration](#service-integration)
9. [DNS and SSL Setup](#dns-and-ssl-setup)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)
11. [Troubleshooting](#troubleshooting)
12. [Rollback Procedures](#rollback-procedures)

---

## Overview

FightSFTickets is a production-ready SaaS application that requires several external services to function properly:

- **Stripe**: Payment processing
- **Lob**: Physical mail delivery
- **OpenAI**: Audio transcription (Whisper API)
- **DeepSeek**: AI statement refinement
- **PostgreSQL**: Database (included in Docker setup)
- **Nginx**: Reverse proxy and SSL termination

This guide covers complete deployment to a production server with all services integrated.

---

## Prerequisites

### Required Accounts and API Keys

1. **Hetzner Cloud Account** (if using Hetzner deployment)
   - Sign up at: https://www.hetzner.com/cloud
   - Generate API token from Cloud Console

2. **Stripe Account**
   - Sign up at: https://stripe.com
   - Get API keys from: https://dashboard.stripe.com/apikeys
   - Required: `Secret Key` and `Webhook Secret`

3. **Lob Account**
   - Sign up at: https://www.lob.com
   - Get API key from: https://dashboard.lob.com/settings/keys
   - Required: `API Key`

4. **OpenAI Account**
   - Sign up at: https://platform.openai.com
   - Get API key from: https://platform.openai.com/api-keys
   - Required: `API Key`

5. **DeepSeek Account**
   - Sign up at: https://platform.deepseek.com
   - Get API key from: https://platform.deepseek.com/api-keys
   - Required: `API Key`

### Local Requirements

- **Git**: For cloning repository
- **SSH**: For server access
- **Bash**: For running deployment scripts
- **curl** and **jq**: For API calls (auto-installed if missing)

### Server Requirements

- **OS**: Ubuntu 22.04 LTS (recommended) or similar
- **RAM**: Minimum 4GB (8GB recommended)
- **CPU**: 2+ vCPUs
- **Storage**: 20GB+ SSD
- **Network**: Public IP address with ports 80 and 443 open

---

## Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] All API keys from required services
- [ ] Domain name registered and ready to point to server
- [ ] SSH key generated (`ssh-keygen -t rsa -b 4096`)
- [ ] Hetzner API token (if using automated deployment)
- [ ] Project repository cloned locally
- [ ] All environment variables documented
- [ ] Stripe webhook endpoint URL prepared
- [ ] Test mode verified for all services

---

## Deployment Options

### Option 1: Automated Hetzner Cloud Deployment (Recommended)

**Pros:**
- Fully automated server provisioning
- One-command deployment
- Automatic firewall and security setup
- Built-in backup procedures

**Cons:**
- Requires Hetzner Cloud account
- Limited to Hetzner infrastructure

### Option 2: Manual Deployment (Any Server)

**Pros:**
- Works with any hosting provider
- More control over configuration
- Flexible infrastructure choices

**Cons:**
- More manual steps
- Requires server administration knowledge
- Security setup is manual

---

## Hetzner Cloud Deployment

### Step 1: Set Hetzner API Token

```bash
export HETZNER_API_TOKEN="your-hetzner-api-token-here"
```

### Step 2: Configure Deployment Settings (Optional)

```bash
# Server configuration (optional - defaults are provided)
export SERVER_TYPE="cx21"              # 2 vCPU, 4GB RAM
export SERVER_LOCATION="ash"           # Ashburn, VA
export DOMAIN="fightsftickets.com"     # Your domain
```

### Step 3: Run Deployment Script

```bash
cd FightSFTickets_Starter_Kit
chmod +x scripts/deploy_hetzner.sh
./scripts/deploy_hetzner.sh
```

### Step 4: Follow Interactive Prompts

The script will prompt you for:
- Stripe Secret Key
- Stripe Webhook Secret
- Lob API Key
- OpenAI API Key
- DeepSeek API Key
- Domain configuration confirmation

### Step 5: Note Server IP

The script will output:
```
Server IP: xxx.xxx.xxx.xxx
```

Save this IP address for DNS configuration.

### Step 6: Configure DNS

Point your domain to the server IP:

```
A Record:     fightsftickets.com    →  xxx.xxx.xxx.xxx
A Record:     www.fightsftickets.com →  xxx.xxx.xxx.xxx
```

Wait 5-60 minutes for DNS propagation.

### Step 7: Complete SSL Setup

After DNS propagation:

```bash
ssh root@xxx.xxx.xxx.xxx
certbot --nginx -d fightsftickets.com -d www.fightsftickets.com
```

### Step 8: Enable HTTPS in Nginx

```bash
cd /var/www/fightsftickets
nano nginx.conf
```

Uncomment the HTTPS server block, save, and restart:

```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## Manual Deployment

### Step 1: Provision Server

Create a server with:
- Ubuntu 22.04 LTS
- 4GB+ RAM
- 2+ vCPU cores
- Public IP address

### Step 2: Initial Server Setup

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    nginx \
    certbot \
    python3-certbot-nginx

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Step 3: Configure Firewall

```bash
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw reload
```

### Step 4: Clone Repository

```bash
mkdir -p /var/www
cd /var/www
git clone <your-repo-url> fightsftickets
cd fightsftickets
```

### Step 5: Configure Environment

```bash
cat > .env << 'EOF'
# Application Settings
APP_ENV=production
APP_URL=https://fightsftickets.com
API_URL=https://fightsftickets.com/api
CORS_ORIGINS=https://fightsftickets.com,https://www.fightsftickets.com

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_THIS_SECURE_PASSWORD
POSTGRES_DB=fightsf
DATABASE_URL=postgresql://postgres:CHANGE_THIS_SECURE_PASSWORD@db:5432/fightsf

# API Keys
STRIPE_SECRET_KEY=sk_live_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
LOB_API_KEY=live_your_lob_key
OPENAI_API_KEY=sk-your_openai_key
DEEPSEEK_API_KEY=sk-your_deepseek_key

# Security
SECRET_KEY=your_random_secret_key_here

# Frontend
NEXT_PUBLIC_API_BASE=https://fightsftickets.com/api
EOF

chmod 600 .env
```

**Important:** Replace all placeholder values with actual keys!

### Step 6: Create Production Docker Compose

```bash
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: backend/Dockerfile
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    restart: unless-stopped
    expose:
      - "8000"
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  web:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    env_file:
      - .env
    restart: unless-stopped
    expose:
      - "3000"
    depends_on:
      - api

  db:
    image: postgres:16
    env_file:
      - .env
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/www/certbot:/var/www/certbot:ro
    depends_on:
      - web
      - api

volumes:
  postgres_data:
    driver: local
EOF
```

### Step 7: Configure Nginx

Create `nginx.conf` - see the automated deployment script for the complete configuration.

### Step 8: Build and Start Services

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Step 9: Run Database Migrations

```bash
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### Step 10: Verify Deployment

```bash
# Check services
docker-compose -f docker-compose.prod.yml ps

# Check health
curl http://localhost:8000/health

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Post-Deployment Configuration

### 1. Verify All Services

```bash
# Check Docker containers
docker ps

# Test API health
curl https://fightsftickets.com/health

# Test frontend
curl -I https://fightsftickets.com
```

### 2. Configure Stripe Webhooks

1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter URL: `https://fightsftickets.com/api/webhooks/stripe`
4. Select events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Copy webhook signing secret
6. Update `.env` with `STRIPE_WEBHOOK_SECRET`
7. Restart API: `docker-compose -f docker-compose.prod.yml restart api`

### 3. Test Payment Flow

1. Visit: https://fightsftickets.com
2. Complete appeal flow with test data
3. Use Stripe test card: `4242 4242 4242 4242`
4. Verify payment completes successfully
5. Check Stripe dashboard for payment
6. Check server logs for Lob mailing confirmation

### 4. Enable Production Mode

Update `.env`:
```bash
# Switch from test keys to live keys
STRIPE_SECRET_KEY=sk_live_...  # Not sk_test_
LOB_API_KEY=live_...             # Not test_
```

Restart services:
```bash
docker-compose -f docker-compose.prod.yml restart
```

---

## Service Integration

### Stripe Integration

**Purpose:** Process payments for appeal service

**Configuration:**
1. Get keys from: https://dashboard.stripe.com/apikeys
2. Set environment variables:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET`
3. Configure webhook endpoint (see above)

**Testing:**
- Test Mode: Use `sk_test_` keys
- Test Card: `4242 4242 4242 4242`
- Expiry: Any future date
- CVC: Any 3 digits

**Production:**
- Switch to `sk_live_` keys
- Configure production webhook endpoint
- Monitor dashboard: https://dashboard.stripe.com

### Lob Integration

**Purpose:** Physical mail delivery of appeal letters

**Configuration:**
1. Get API key from: https://dashboard.lob.com/settings/keys
2. Set environment variable: `LOB_API_KEY`

**Testing:**
- Test Mode: Use `test_` keys - no physical mail sent
- Verify in dashboard: https://dashboard.lob.com

**Production:**
- Switch to `live_` keys
- Real mail will be sent
- Monitor in dashboard

### OpenAI Integration

**Purpose:** Audio transcription using Whisper API

**Configuration:**
1. Get API key from: https://platform.openai.com/api-keys
2. Set environment variable: `OPENAI_API_KEY`
3. Ensure account has credit

**Testing:**
- Upload audio in appeal flow
- Verify transcription appears

**Monitoring:**
- Usage: https://platform.openai.com/usage
- Billing: https://platform.openai.com/account/billing

### DeepSeek Integration

**Purpose:** AI-powered statement refinement

**Configuration:**
1. Get API key from: https://platform.deepseek.com/api-keys
2. Set environment variable: `DEEPSEEK_API_KEY`

**Testing:**
- Enter statement in appeal flow
- Click "Polish with AI"
- Verify refined statement appears

**Monitoring:**
- Dashboard: https://platform.deepseek.com/dashboard

---

## DNS and SSL Setup

### DNS Configuration

**A Records Required:**
```
Type    Host    Value               TTL
A       @       xxx.xxx.xxx.xxx     3600
A       www     xxx.xxx.xxx.xxx     3600
```

**Verification:**
```bash
# Check DNS propagation
dig fightsftickets.com +short
dig www.fightsftickets.com +short

# Or use online tools
# https://dnschecker.org
```

### SSL Certificate Setup

**Using Let's Encrypt (Free):**

```bash
# SSH to server
ssh root@your-server-ip

# Obtain certificate
certbot --nginx -d fightsftickets.com -d www.fightsftickets.com

# Follow prompts to:
# 1. Enter email address
# 2. Agree to terms
# 3. Choose redirect option (Yes)
```

**Auto-Renewal:**
```bash
# Test renewal
certbot renew --dry-run

# Renewal runs automatically via systemd timer
systemctl list-timers | grep certbot
```

**Verify SSL:**
```bash
# Test HTTPS
curl -I https://fightsftickets.com

# Check certificate
openssl s_client -connect fightsftickets.com:443 -servername fightsftickets.com
```

---

## Monitoring and Maintenance

### Health Checks

```bash
# API health check
curl https://fightsftickets.com/health

# Expected response:
# {"status":"healthy","timestamp":"2025-01-09T..."}
```

### Viewing Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f web

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Database Backups

**Manual Backup:**
```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec db \
    pg_dump -U postgres fightsf > backup_$(date +%Y%m%d_%H%M%S).sql

# Compress
gzip backup_*.sql
```

**Automated Backups (Cron):**
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * cd /var/www/fightsftickets && docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres fightsf | gzip > /var/backups/fightsftickets_$(date +\%Y\%m\%d).sql.gz
```

**Restore from Backup:**
```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore database
gunzip -c backup.sql.gz | docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres fightsf

# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

### Updating Deployment

**Option 1: Using Update Script**
```bash
# From local machine
SERVER_IP=xxx.xxx.xxx.xxx ./scripts/update_deployment.sh
```

**Option 2: Manual Update**
```bash
# SSH to server
ssh root@your-server-ip
cd /var/www/fightsftickets

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### Performance Monitoring

**System Resources:**
```bash
# Docker stats
docker stats

# Disk usage
df -h

# Memory usage
free -h

# CPU load
uptime
```

**Application Metrics:**
```bash
# Response time monitoring
curl -w "\nTime: %{time_total}s\n" https://fightsftickets.com/health

# Request rate (from logs)
docker-compose -f docker-compose.prod.yml logs --since=1h api | grep -c "GET\|POST"
```

---

## Troubleshooting

### Common Issues

#### 1. Services Not Starting

**Symptoms:**
- Docker containers in "Restarting" state
- Health checks failing

**Solutions:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check specific service
docker-compose -f docker-compose.prod.yml logs api

# Verify environment variables
docker-compose -f docker-compose.prod.yml config

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

#### 2. Database Connection Errors

**Symptoms:**
- API returns 500 errors
- "Connection refused" in logs

**Solutions:**
```bash
# Check database status
docker-compose -f docker-compose.prod.yml ps db

# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Verify database connectivity
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres

# Restart database
docker-compose -f docker-compose.prod.yml restart db
```

#### 3. SSL Certificate Issues

**Symptoms:**
- "Certificate not found" errors
- HTTPS not working

**Solutions:**
```bash
# Check certificate files
ls -la /etc/letsencrypt/live/fightsftickets.com/

# Renew certificate
certbot renew

# Test certificate
certbot certificates

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

#### 4. Payment Processing Failures

**Symptoms:**
- Stripe errors in logs
- Payments not completing

**Solutions:**
```bash
# Verify Stripe keys
echo $STRIPE_SECRET_KEY

# Check webhook configuration
curl https://dashboard.stripe.com/webhooks

# Test webhook endpoint
curl -X POST https://fightsftickets.com/api/webhooks/stripe

# Check API logs for Stripe errors
docker-compose -f docker-compose.prod.yml logs api | grep -i stripe
```

#### 5. High Memory Usage

**Symptoms:**
- Server becoming slow
- Out of memory errors

**Solutions:**
```bash
# Check memory usage
docker stats --no-stream

# Restart memory-intensive services
docker-compose -f docker-compose.prod.yml restart api web

# Clear Docker cache
docker system prune -af

# Upgrade server (if needed)
# Increase RAM to 8GB or more
```

### Debug Mode

**Enable verbose logging:**
```bash
# Edit .env
nano .env

# Add/modify:
LOG_LEVEL=DEBUG
APP_ENV=development

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

**Disable debug mode after troubleshooting!**

---

## Rollback Procedures

### Emergency Rollback

**If update causes critical issues:**

```bash
# SSH to server
ssh root@your-server-ip
cd /var/www/fightsftickets

# Find latest backup
ls -lt /var/backups/fightsftickets/

# Restore database
BACKUP_FILE="/var/backups/fightsftickets/fightsftickets_YYYYMMDD_db.sql.gz"
gunzip -c $BACKUP_FILE | docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres fightsf

# Restore code (if needed)
git reset --hard <previous-commit-hash>

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### Version Control Rollback

```bash
# View commit history
git log --oneline -10

# Rollback to specific version
git checkout <commit-hash>

# Rebuild services
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Security Best Practices

### 1. Secure Environment Variables

- Never commit `.env` to version control
- Use strong, random passwords
- Rotate keys regularly
- Store backups securely

### 2. Keep Software Updated

```bash
# Update system packages
apt-get update && apt-get upgrade -y

# Update Docker images
docker-compose -f docker-compose.prod.yml pull

# Rebuild with latest dependencies
docker-compose -f docker-compose.prod.yml build --no-cache
```

### 3. Monitor Access

```bash
# Review SSH login attempts
tail -f /var/log/auth.log

# Check application logs for suspicious activity
docker-compose -f docker-compose.prod.yml logs | grep -i "error\|unauthorized\|forbidden"
```

### 4. Regular Backups

- Daily database backups
- Weekly full system backups
- Test restore procedures monthly
- Store backups off-server

### 5. Rate Limiting

Nginx configuration includes rate limiting:
- API: 10 requests/second
- General: 100 requests/second

Adjust in `nginx.conf` if needed.

---

## Support and Resources

### Documentation
- Main README: `README.md`
- Runbook: `RUNBOOK.md`
- API Documentation: `/docs` directory

### External Services
- Stripe: https://dashboard.stripe.com
- Lob: https://dashboard.lob.com
- OpenAI: https://platform.openai.com
- DeepSeek: https://platform.deepseek.com
- Hetzner: https://console.hetzner.cloud

### Monitoring Dashboards
- Application Health: `https://fightsftickets.com/health`
- Server Stats: `ssh root@server-ip 'docker stats'`
- Database Stats: `docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_database;"`

### Emergency Contacts
- Document your team's contact information here
- Include on-call procedures
- List escalation paths

---

## Conclusion

This deployment guide provides complete instructions for deploying FightSFTickets to production. Follow the steps carefully, test thoroughly, and maintain regular backups.

For questions or issues not covered in this guide, refer to:
1. RUNBOOK.md for operational procedures
2. README.md for project overview
3. Individual service documentation

**Remember:** Always test in a staging environment before deploying to production!

---

*Last Updated: 2025-01-09*  
*Guide Version: 1.0.0*  
*Application Version: 1.0.0*