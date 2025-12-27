# 🚀 Deployment Steps - FightCityTickets.com

## Pre-Deployment Checklist

- [x] Server accessible via SSH (178.156.215.100)
- [ ] Project directory located on server
- [ ] Zombie processes checked
- [ ] Memory usage verified
- [ ] Deployment package created
- [ ] Application deployed
- [ ] Services verified running
- [ ] DNS configured
- [ ] SSL certificate installed

## Step-by-Step Deployment

### Step 1: Locate Project Directory on Server

**SSH into server:**
```bash
ssh root@178.156.215.100
```

**Find project directory:**
```bash
find / -name "docker-compose.yml" -o -name "docker-compose.prod.yml" 2>/dev/null
```

**Expected locations:**
- `/var/www/fightsftickets` (most likely)
- `/root/fightsftickets`
- `/opt/fightsftickets`

**Action:** Note the directory path found.

### Step 2: Create Deployment Package (Local Machine)

**From your local machine (Windows Git Bash):**
```bash
cd C:/Comapnyfiles/provethat.io/FightSFTickets_Starter_Kit

# Create deployment package
tar -czf deploy.tar.gz \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='.env' \
  --exclude='venv' \
  --exclude='*.log' \
  .
```

### Step 3: Upload to Server

**From local machine:**
```bash
# Upload using scp (works on Windows Git Bash)
scp deploy.tar.gz root@178.156.215.100:/tmp/
```

### Step 4: Deploy on Server

**SSH into server:**
```bash
ssh root@178.156.215.100
```

**Navigate to project directory (use path from Step 1):**
```bash
cd /var/www/fightsftickets  # Replace with actual path found
```

**Backup current deployment:**
```bash
mkdir -p backup
cp docker-compose*.yml backup/ 2>/dev/null || true
cp .env backup/ 2>/dev/null || true
```

**Stop containers (clears zombies and frees memory):**
```bash
docker-compose down 2>/dev/null || docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
```

**Wait for cleanup:**
```bash
sleep 5
```

**Extract new deployment:**
```bash
tar -xzf /tmp/deploy.tar.gz -C . --strip-components=1 || tar -xzf /tmp/deploy.tar.gz -C .
rm /tmp/deploy.tar.gz
```

**Ensure .env exists:**
```bash
if [ ! -f .env ]; then
  cat > .env << 'EOF'
APP_ENV=production
APP_URL=https://fightcitytickets.com
API_URL=https://fightcitytickets.com/api
NEXT_PUBLIC_API_BASE=https://fightcitytickets.com/api
CORS_ORIGINS=https://fightcitytickets.com,https://www.fightcitytickets.com
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_DB=fightsf
DATABASE_URL=postgresql+psycopg://postgres:changeme@db:5432/fightsf
EOF
fi
```

**Build and start services:**
```bash
COMPOSE_FILE="docker-compose.prod.yml"
if [ ! -f "$COMPOSE_FILE" ]; then
    COMPOSE_FILE="docker-compose.yml"
fi

docker-compose -f "$COMPOSE_FILE" up -d --build --force-recreate
```

**Wait for services:**
```bash
sleep 30
```

### Step 5: Verify Deployment

**Check service status:**
```bash
docker-compose -f "$COMPOSE_FILE" ps
```

**Check for zombies (should be cleared):**
```bash
ps aux | grep '<defunct>' | wc -l
# Should be 0 or very low
```

**Check memory usage:**
```bash
free -m
# Should be < 80% after restart
```

**Check logs:**
```bash
docker-compose -f "$COMPOSE_FILE" logs --tail=50
```

**Test endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

### Step 6: Configure DNS

**At your domain registrar:**
1. Log into account
2. Go to DNS Management for `fightcitytickets.com`
3. Add A records:
   ```
   Type: A
   Name: @
   Value: 178.156.215.100
   TTL: 3600
   
   Type: A
   Name: www
   Value: 178.156.215.100
   TTL: 3600
   ```
4. Save and wait 5-30 minutes

**Verify DNS:**
```bash
nslookup fightcitytickets.com
# Should return: 178.156.215.100
```

### Step 7: Set Up SSL

**After DNS propagates:**
```bash
ssh root@178.156.215.100
certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com
```

**Restart nginx:**
```bash
cd /var/www/fightsftickets
docker-compose restart nginx
# Or if using system nginx:
systemctl reload nginx
```

### Step 8: Final Verification

**Test domain:**
```bash
curl http://fightcitytickets.com
curl https://fightcitytickets.com
```

**In browser:**
- Open: https://fightcitytickets.com
- Should see homepage
- Test city routes: /SF, /NYC, /LA

## Automated Deployment Script

**Use the automated script (from Git Bash):**
```bash
cd C:/Comapnyfiles/provethat.io/FightSFTickets_Starter_Kit
export SERVER_IP=178.156.215.100
bash scripts/deploy_manual.sh
```

This script will:
- ✅ Locate project directory automatically
- ✅ Check for zombie processes
- ✅ Monitor memory usage
- ✅ Create deployment package
- ✅ Upload via scp (no rsync needed)
- ✅ Deploy and restart services
- ✅ Verify deployment

## Troubleshooting

### Zombie Processes Persist
```bash
# Check what's creating zombies
ps aux | grep '<defunct>'

# Restart Docker daemon (last resort)
systemctl restart docker

# Restart containers
docker-compose restart
```

### High Memory Usage
```bash
# Check memory by container
docker stats --no-stream

# Restart memory-heavy containers
docker-compose restart api

# Check for memory leaks
docker-compose logs api | grep -i "memory\|oom"
```

### Services Won't Start
```bash
# Check logs
docker-compose logs api
docker-compose logs web
docker-compose logs db

# Check .env file
cat .env

# Verify docker-compose file
docker-compose config
```

### Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :80
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Stop conflicting services or change ports in docker-compose.yml
```

## Post-Deployment Monitoring

**Monitor for 24 hours:**
```bash
# Watch logs
docker-compose logs -f

# Monitor resources
docker stats

# Check for zombies periodically
watch -n 60 'ps aux | grep defunct | wc -l'
```

## Success Criteria

- ✅ All containers running (docker-compose ps shows "Up")
- ✅ No zombie processes (ps aux | grep defunct = 0)
- ✅ Memory usage < 80%
- ✅ Health endpoint responds: curl http://178.156.215.100/health
- ✅ Frontend loads: curl http://178.156.215.100
- ✅ DNS configured and propagating
- ✅ SSL certificate installed
- ✅ HTTPS redirects working
- ✅ City routes working (/SF, /NYC, etc.)


