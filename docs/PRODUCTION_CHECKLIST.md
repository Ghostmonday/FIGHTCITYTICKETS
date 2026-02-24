# 🚀 Production Deployment Checklist

## ✅ Completed

- [x] OpenAI integration removed
- [x] Voice-to-text/audio recording removed
- [x] Environment variables organized and documented
- [x] Security headers configured (nginx)
- [x] CORS configured
- [x] Rate limiting implemented
- [x] Error handling with Sentry support
- [x] Health check endpoints
- [x] Database migrations ready
- [x] Docker Compose configuration
- [x] Nginx reverse proxy configured

## ⚠️ REQUIRED Before Production Deployment

### 1. Environment Variables (.env)

**CRITICAL - Must be set before deployment:**

```bash
# Generate secure random secret key (32+ chars)
SECRET_KEY=<generate-random-32-char-string>

# Database password (strong password)
POSTGRES_PASSWORD=<strong-secure-password>

# Stripe LIVE keys (not test keys!)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Lob LIVE API key
LOB_API_KEY=live_...
LOB_MODE=live

# DeepSeek API key
DEEPSEEK_API_KEY=sk-...

# Google Places API key
NEXT_PUBLIC_GOOGLE_PLACES_API_KEY=...

# Update API URLs for production
API_URL=https://fightcitytickets.com/api
NEXT_PUBLIC_API_BASE=https://fightcitytickets.com/api
```

### 2. API URL Configuration

**FIX NEEDED:** Update these in `.env`:

```bash
# Current (WRONG for production):
API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE=http://localhost:8000

# Should be:
API_URL=https://fightcitytickets.com/api
NEXT_PUBLIC_API_BASE=https://fightcitytickets.com/api
```

### 3. Sentry Error Tracking (Optional but Recommended)

Add to `.env`:
```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 4. Database Migrations

**Run before first deployment:**
```bash
docker compose exec api python -m alembic upgrade head
```

### 5. Stripe Webhook Configuration

**CRITICAL:** Configure webhook endpoint in Stripe Dashboard:
- URL: `https://fightcitytickets.com/api/webhook/stripe`
- Events: `checkout.session.completed`
- Copy webhook secret to `.env`

### 6. SSL Certificate

**After DNS is configured:**
```bash
ssh root@your-server-ip
certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com
```

### 7. Domain DNS Configuration

Point DNS records to server IP:
- A record: `fightcitytickets.com` → `<server-ip>`
- A record: `www.fightcitytickets.com` → `<server-ip>`

## 🔍 Pre-Deployment Verification

Run validation script:
```bash
cd /home/evan/Documents/FightCityTickets
python3 scripts/validate_setup.py
```

Check health endpoints:
```bash
curl http://localhost/health
curl http://localhost/health/ready
curl http://localhost/status
```

## 📋 Deployment Steps

1. **Set all environment variables** in `.env`
2. **Update API URLs** to production domain
3. **Deploy to server** using Kamatera deployment commands
4. **Run database migrations**
5. **Configure Stripe webhook** endpoint
6. **Set up SSL** with certbot
7. **Test payment flow** end-to-end
8. **Monitor logs** for errors

## 🛡️ Security Checklist

- [ ] All API keys are LIVE keys (not test)
- [ ] Database password is strong and unique
- [ ] SECRET_KEY is random 32+ character string
- [ ] SSL certificate installed and working
- [ ] Firewall configured (ports 80, 443, 22 only)
- [ ] SSH key authentication enabled
- [ ] Root password disabled or very strong
- [ ] `.env` file is NOT committed to git
- [ ] CORS origins match production domain
- [ ] Rate limiting is active

## 📊 Monitoring Setup

- [ ] Sentry DSN configured (optional)
- [ ] Health check endpoints responding
- [ ] Log aggregation configured (optional)
- [ ] Uptime monitoring set up (optional)

## 🧪 Testing Checklist

- [ ] Citation validation works
- [ ] Statement refinement works
- [ ] Checkout session creation works
- [ ] Stripe webhook receives events
- [ ] Lob mail sending works
- [ ] Database persistence works
- [ ] Frontend loads correctly
- [ ] API endpoints respond correctly
- [ ] Error pages display correctly

## 🚨 Critical Issues to Fix

1. **API_URL** - Currently `localhost:8000`, must be production URL
2. **NEXT_PUBLIC_API_BASE** - Currently `localhost:8000`, must be production URL
3. **All placeholder values** in `.env` must be replaced with real credentials

## 📝 Post-Deployment

1. Test complete user flow
2. Verify Stripe webhook delivery
3. Test Lob mail sending
4. Monitor error logs
5. Check database for data persistence
6. Verify SSL certificate auto-renewal
