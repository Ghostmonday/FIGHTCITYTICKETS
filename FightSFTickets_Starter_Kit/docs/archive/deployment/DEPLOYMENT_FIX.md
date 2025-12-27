# 🚨 FIX: www.fightcitytickets.com Not Working

## Problem Identified
The main issue is that **nginx is missing from docker-compose.yml**. Without nginx, there's no reverse proxy to route traffic from ports 80/443 to your web and API containers.

## What Was Fixed

1. ✅ Added nginx service to `docker-compose.yml`
2. ✅ Created nginx configuration files
3. ✅ Updated ports - web and api now use `expose` instead of `ports` (nginx handles external access)
4. ✅ Created deployment fix script

## Quick Fix Steps

### Option 1: Use the Fix Script (Recommended)

**On your local machine:**
```bash
cd FightSFTickets_Starter_Kit/FightSFTickets_Starter_Kit
chmod +x scripts/fix_deployment.sh
```

**SSH to server and run:**
```bash
ssh root@178.156.215.100
cd /var/www/fightsftickets
# Copy the updated files or pull from git
bash scripts/fix_deployment.sh
```

### Option 2: Manual Fix

**1. SSH to your server:**
```bash
ssh root@178.156.215.100
cd /var/www/fightsftickets
```

**2. Update docker-compose.yml** (copy the updated version from this repo)

**3. Create nginx directory:**
```bash
mkdir -p nginx/conf.d
```

**4. Copy nginx config files:**
- Copy `nginx/nginx.conf` to the server
- Copy `nginx/conf.d/fightcitytickets.conf` to the server

**5. Restart services:**
```bash
docker-compose down
docker-compose up -d --build
```

**6. Verify it's working:**
```bash
# Check containers are running
docker-compose ps

# Test HTTP endpoint
curl http://localhost/health

# Check logs
docker-compose logs nginx
docker-compose logs web
docker-compose logs api
```

## Verify DNS Configuration

Make sure DNS is pointing to your server IP:

```bash
# Check DNS resolution
nslookup fightcitytickets.com
nslookup www.fightcitytickets.com

# Should return: 178.156.215.100
```

If DNS is not configured:
1. Go to your domain registrar (Namecheap, GoDaddy, etc.)
2. Add A records:
   - `@` → `178.156.215.100`
   - `www` → `178.156.215.100`
3. Wait 5-30 minutes for DNS propagation

## Set Up SSL Certificate

Once nginx is running and DNS is configured:

```bash
ssh root@178.156.215.100
cd /var/www/fightsftickets

# Install certbot if not installed
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com

# Certbot will automatically update nginx config
```

## Troubleshooting

### Containers won't start
```bash
# Check logs
docker-compose logs

# Check if ports are in use
netstat -tulpn | grep :80
netstat -tulpn | grep :443

# Stop conflicting services
systemctl stop apache2  # if running
systemctl stop nginx    # if system nginx is running
```

### nginx can't connect to web/api
```bash
# Check if containers are on same network
docker network ls
docker network inspect fightsftickets_default

# Check container names match nginx config
docker-compose ps
# Should see: api, web, nginx, db
```

### SSL certificate issues
```bash
# Test certificate
certbot certificates

# Renew manually if needed
certbot renew --dry-run
```

### Still not working?
1. Check firewall:
   ```bash
   ufw status
   ufw allow 80/tcp
   ufw allow 443/tcp
   ```

2. Check nginx config syntax:
   ```bash
   docker-compose exec nginx nginx -t
   ```

3. View real-time logs:
   ```bash
   docker-compose logs -f nginx web api
   ```

## What Changed

### docker-compose.yml
- ✅ Added `nginx` service
- ✅ Changed `api` ports from `8000:8000` to `expose: 8000`
- ✅ Changed `web` ports from `3000:3000` to `expose: 3000`
- ✅ nginx now handles ports 80 and 443

### New Files
- ✅ `nginx/nginx.conf` - Main nginx configuration
- ✅ `nginx/conf.d/fightcitytickets.conf` - Domain-specific config
- ✅ `scripts/fix_deployment.sh` - Automated fix script

## After Fix

Your site should be accessible at:
- http://fightcitytickets.com (redirects to HTTPS)
- https://fightcitytickets.com (after SSL setup)
- https://www.fightcitytickets.com (after SSL setup)

Test endpoints:
- `https://fightcitytickets.com/health` - Health check
- `https://fightcitytickets.com/api/health` - API health
- `https://fightcitytickets.com` - Frontend

