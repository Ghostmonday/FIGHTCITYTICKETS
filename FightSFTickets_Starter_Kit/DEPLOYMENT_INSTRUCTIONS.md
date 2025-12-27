# Deployment Instructions for FightCityTickets.com

## Current Status
- **Domain**: fightcitytickets.com
- **Server IP**: 178.156.215.100
- **Deployment Path**: /var/www/fightsftickets

## Quick Deployment Steps

### 1. Verify DNS Configuration

**Check if DNS is pointing correctly:**
```bash
nslookup fightcitytickets.com
# Should return: 178.156.215.100
```

**If DNS is not configured:**
1. Log into your domain registrar (Namecheap, GoDaddy, etc.)
2. Go to DNS Management
3. Add these A records:
   - Type: A, Name: @ (or blank), Value: 178.156.215.100, TTL: 3600
   - Type: A, Name: www, Value: 178.156.215.100, TTL: 3600
4. Wait 5-30 minutes for DNS propagation

### 2. Deploy Application

**Option A: Using update_deployment.sh (Recommended)**
```bash
cd FightSFTickets_Starter_Kit
export SERVER_IP=178.156.215.100
./scripts/update_deployment.sh
```

**Option B: Manual Deployment**
```bash
# Create deployment package
tar -czf deploy.tar.gz \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='.env' \
  .

# Upload to server
scp deploy.tar.gz root@178.156.215.100:/tmp/

# SSH and deploy
ssh root@178.156.215.100
cd /var/www/fightsftickets
tar -xzf /tmp/deploy.tar.gz
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate
```

### 3. Verify Deployment

**Check if services are running:**
```bash
ssh root@178.156.215.100
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml ps
```

**Check logs:**
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

**Test endpoints:**
```bash
# Health check
curl http://178.156.215.100/health

# Frontend
curl http://178.156.215.100

# API
curl http://178.156.215.100/api/health
```

### 4. Configure SSL (HTTPS)

**After DNS is configured:**
```bash
ssh root@178.156.215.100
certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com
```

**Restart nginx:**
```bash
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml restart nginx
```

### 5. Verify Page Loads

**Test domain:**
```bash
# HTTP
curl http://fightcitytickets.com

# HTTPS (after SSL setup)
curl https://fightcitytickets.com
```

**In browser:**
- Open: http://fightcitytickets.com (or https:// after SSL)
- Should see the homepage loading
- Test city routes: /SF, /NYC, /LA, etc.

## Troubleshooting

### DNS Not Resolving
- Wait 5-30 minutes for DNS propagation
- Check DNS records at your registrar
- Verify A records point to 178.156.215.100
- Use: https://www.whatsmydns.net/#A/fightcitytickets.com

### Server Not Responding
- Check Hetzner Cloud dashboard
- Verify server is running
- Check firewall: `ufw status`
- Test SSH: `ssh root@178.156.215.100`

### Services Not Starting
- Check logs: `docker-compose logs`
- Verify .env file exists and has correct values
- Check database connection
- Restart services: `docker-compose restart`

### Page Not Loading
- Check nginx configuration
- Verify containers are running: `docker ps`
- Check nginx logs: `docker-compose logs nginx`
- Test backend directly: `curl http://localhost:8000/health`

## Environment Variables

Ensure `.env` file on server has:
```bash
APP_ENV=production
APP_URL=https://fightcitytickets.com
API_URL=https://fightcitytickets.com/api
NEXT_PUBLIC_API_BASE=https://fightcitytickets.com/api
CORS_ORIGINS=https://fightcitytickets.com,https://www.fightcitytickets.com
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<secure-password>
POSTGRES_DB=fightsf
DATABASE_URL=postgresql+psycopg://postgres:<password>@db:5432/fightsf
STRIPE_SECRET_KEY=<your-stripe-key>
LOB_API_KEY=<your-lob-key>
DEEPSEEK_API_KEY=<your-deepseek-key>
```

## Post-Deployment Checklist

- [ ] DNS configured and propagating
- [ ] Application deployed successfully
- [ ] Docker containers running
- [ ] Health endpoints responding
- [ ] Frontend loads correctly
- [ ] API endpoints working
- [ ] SSL certificate installed
- [ ] HTTPS redirects working
- [ ] City routes working (/SF, /NYC, etc.)
- [ ] Stripe webhooks configured
- [ ] Email service (Lob) configured

## Support

For issues, check:
- Server logs: `docker-compose logs -f`
- Nginx logs: `docker-compose logs nginx`
- Backend logs: `docker-compose logs api`
- Frontend logs: `docker-compose logs web`



