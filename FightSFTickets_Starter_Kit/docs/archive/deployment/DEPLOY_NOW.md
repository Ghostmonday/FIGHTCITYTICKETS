# 🚀 Deploy FightCityTickets.com NOW

## Current Status
- ✅ Server is reachable (178.156.215.100)
- ❌ HTTP not responding (services may not be running)
- ❌ DNS not configured (fightcitytickets.com)

## Quick Deployment Steps

### Step 1: Deploy Application to Server

**Using Git Bash or WSL (Recommended):**
```bash
cd FightSFTickets_Starter_Kit
export SERVER_IP=178.156.215.100
bash scripts/update_deployment.sh
```

**Or manually via SSH:**
```bash
# 1. Create deployment package
cd FightSFTickets_Starter_Kit
tar -czf deploy.tar.gz \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='.env' \
  --exclude='*.log' \
  .

# 2. Upload to server
scp deploy.tar.gz root@178.156.215.100:/tmp/

# 3. SSH and deploy
ssh root@178.156.215.100
cd /var/www/fightsftickets
tar -xzf /tmp/deploy.tar.gz
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate
```

### Step 2: Configure DNS

**At your domain registrar (Namecheap, GoDaddy, etc.):**

1. Log into your account
2. Go to DNS Management for `fightcitytickets.com`
3. Add these A records:
   ```
   Type: A
   Name: @ (or blank/root)
   Value: 178.156.215.100
   TTL: 3600

   Type: A
   Name: www
   Value: 178.156.215.100
   TTL: 3600
   ```
4. Save changes
5. Wait 5-30 minutes for DNS propagation

**Verify DNS:**
```bash
nslookup fightcitytickets.com
# Should return: 178.156.215.100
```

### Step 3: Verify Services Are Running

**SSH into server:**
```bash
ssh root@178.156.215.100
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml ps
```

**Check logs if services aren't running:**
```bash
docker-compose -f docker-compose.prod.yml logs
```

**Start services if needed:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Step 4: Configure Nginx (if not already configured)

**On server:**
```bash
ssh root@178.156.215.100
cd /var/www/fightsftickets

# Check if nginx config exists
cat nginx.conf

# If nginx isn't running in docker, configure system nginx:
# Edit nginx config
nano /etc/nginx/sites-available/fightcitytickets

# Add this configuration:
server {
    listen 80;
    server_name fightcitytickets.com www.fightcitytickets.com;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Enable site
ln -s /etc/nginx/sites-available/fightcitytickets /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Step 5: Set Up SSL (After DNS Works)

**Once DNS is configured:**
```bash
ssh root@178.156.215.100
certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com
```

### Step 6: Verify Everything Works

**Test endpoints:**
```bash
# Health check
curl http://178.156.215.100/health

# Frontend
curl http://178.156.215.100

# After DNS: Test domain
curl http://fightcitytickets.com
```

**In browser:**
- http://fightcitytickets.com (or https:// after SSL)
- Should see homepage
- Test city routes: /SF, /NYC, /LA

## Troubleshooting

### Services Not Starting
```bash
# Check logs
docker-compose logs api
docker-compose logs web
docker-compose logs db

# Check .env file exists
cat .env

# Restart services
docker-compose restart
```

### Port Already in Use
```bash
# Check what's using ports
netstat -tulpn | grep :80
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Stop conflicting services or change ports
```

### Database Issues
```bash
# Check database
docker-compose exec db psql -U postgres -d fightsf

# Run migrations
docker-compose exec api alembic upgrade head
```

## Environment Variables Needed

Create `.env` file on server with:
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
STRIPE_SECRET_KEY=<your-key>
LOB_API_KEY=<your-key>
DEEPSEEK_API_KEY=<your-key>
```

## Next Steps After Deployment

1. ✅ Deploy code to server
2. ✅ Configure DNS
3. ✅ Verify services running
4. ✅ Test HTTP endpoints
5. ✅ Set up SSL
6. ✅ Test HTTPS
7. ✅ Configure Stripe webhooks
8. ✅ Test full flow end-to-end


