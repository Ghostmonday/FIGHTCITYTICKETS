# 🚨 URGENT: Get FightCityTickets.com Live

## Current Status
- ❌ DNS not configured - domain doesn't resolve
- ❌ Server not responding (178.156.215.100)
- ✅ Code is ready to deploy

## Immediate Steps to Get Site Live

### Step 1: Check Domain Registration
1. Go to your domain registrar (Namecheap, GoDaddy, etc.)
2. Verify `fightcitytickets.com` is registered
3. If not registered, register it NOW

### Step 2: Configure DNS Records
Point your domain to server IP: `178.156.215.100`

**DNS Records Needed:**
```
Type: A
Name: @ (or blank)
Value: 178.156.215.100
TTL: 3600

Type: A  
Name: www
Value: 178.156.215.100
TTL: 3600
```

**Where to add:**
- Namecheap: https://ap.www.namecheap.com/domains/list/
- GoDaddy: DNS Management
- Other: Your registrar's DNS settings

### Step 3: Verify Server is Running
```bash
# Check if server responds
curl http://178.156.215.100

# SSH into server
ssh root@178.156.215.100

# Check if Docker containers are running
docker ps

# Check if services are up
systemctl status nginx
```

### Step 4: Deploy Latest Code
```bash
cd FightSFTickets_Starter_Kit

# Set domain
export DOMAIN="fightcitytickets.com"
export HETZNER_API_TOKEN="your_token"

# Deploy (if server is accessible)
./scripts/deploy_hetzner.sh

# OR manually deploy if server exists
# Create deployment package
tar -czf deploy.tar.gz \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='__pycache__' \
  --exclude='.env' \
  --exclude='.git' \
  .

# Upload to server
scp deploy.tar.gz root@178.156.215.100:/var/www/fightsftickets/

# SSH and extract
ssh root@178.156.215.100
cd /var/www/fightsftickets
tar -xzf deploy.tar.gz
docker-compose down
docker-compose up -d --build
```

### Step 5: Configure Nginx for Domain
```bash
# SSH into server
ssh root@178.156.215.100

# Edit nginx config
nano /etc/nginx/sites-available/fightcitytickets

# Add server block:
server {
    listen 80;
    server_name fightcitytickets.com www.fightcitytickets.com;
    
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

### Step 6: Set Up SSL
```bash
# On server
certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com
```

## Quick Test
After DNS propagates (can take 5 minutes to 48 hours):
```bash
# Test DNS
nslookup fightcitytickets.com

# Test site
curl https://fightcitytickets.com
```

## If Server is Down
If server doesn't respond, you may need to:
1. Check Hetzner Cloud dashboard
2. Restart server
3. Check firewall rules
4. Redeploy from scratch

## Need Help?
Check these files:
- `scripts/deploy_hetzner.sh` - Full deployment script
- `docs/DNS_SETUP_GUIDE.md` - DNS configuration
- `docs/SSL_SETUP_GUIDE.md` - SSL setup


