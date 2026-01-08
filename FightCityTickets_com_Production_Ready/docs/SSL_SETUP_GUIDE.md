# SSL Certificate Setup Guide

This guide will help you set up SSL (HTTPS) for fightcitytickets.com using Let's Encrypt (free SSL certificates).

## Prerequisites

1. ✅ DNS must be configured and pointing to `178.156.215.100`
2. ✅ Domain must be accessible via HTTP first
3. ✅ Nginx must be installed and running on your server
4. ✅ Ports 80 and 443 must be open in your firewall

## Quick Setup (Automated)

### Option 1: Run the Setup Script

```bash
# From your local machine
chmod +x scripts/setup_ssl.sh
./scripts/setup_ssl.sh
```

This will:
- SSH into your server
- Install Certbot
- Configure Nginx (if needed)
- Obtain SSL certificate
- Set up auto-renewal

### Option 2: Manual Setup

SSH into your server and run:

```bash
ssh root@178.156.215.100

# Install Certbot
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com
```

Follow the prompts:
- Enter your email address
- Agree to terms of service
- Choose option 2 (Redirect HTTP to HTTPS) - **Recommended**

## Verify SSL Setup

### Check Certificate

```bash
# On your server
certbot certificates
```

You should see your certificate listed with expiration date.

### Test Auto-Renewal

```bash
# Test that auto-renewal will work
certbot renew --dry-run
```

### Test Your Site

1. Visit: `https://fightcitytickets.com`
2. Visit: `https://www.fightcitytickets.com`
3. Check SSL rating: https://www.ssllabs.com/ssltest/analyze.html?d=fightcitytickets.com

## Update Application Configuration

After SSL is set up, update your `.env` file:

```bash
# Update CORS to allow HTTPS
CORS_ORIGINS=https://fightcitytickets.com,https://www.fightcitytickets.com

# Update application URLs
APP_URL=https://fightcitytickets.com
API_URL=https://fightcitytickets.com
```

Then restart your services:

```bash
docker-compose restart
```

## Nginx Configuration

Certbot will automatically update your Nginx configuration. Your config should look like:

```nginx
server {
    listen 80;
    server_name fightcitytickets.com www.fightcitytickets.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name fightcitytickets.com www.fightcitytickets.com;

    ssl_certificate /etc/letsencrypt/live/fightcitytickets.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fightcitytickets.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Auto-Renewal

Let's Encrypt certificates expire every 90 days. Certbot sets up auto-renewal automatically.

### Check Auto-Renewal Status

```bash
systemctl status certbot.timer
```

### Manual Renewal (if needed)

```bash
certbot renew
systemctl reload nginx
```

## Troubleshooting

### Certificate Not Issued

**Problem**: Certbot can't verify domain ownership

**Solutions**:
1. Verify DNS is pointing to your server:
   ```bash
   nslookup fightcitytickets.com
   # Should return: 178.156.215.100
   ```

2. Ensure port 80 is open:
   ```bash
   # Check firewall
   ufw status
   # Allow HTTP if needed
   ufw allow 80/tcp
   ```

3. Ensure Nginx is running:
   ```bash
   systemctl status nginx
   ```

### Mixed Content Warnings

**Problem**: Site loads over HTTPS but some resources load over HTTP

**Solution**: Update all URLs in your application to use HTTPS:
- Update `APP_URL` and `API_URL` in `.env`
- Update any hardcoded HTTP URLs in code
- Ensure API calls use HTTPS

### Certificate Expired

**Problem**: Certificate expired and auto-renewal didn't work

**Solution**:
```bash
# Renew manually
certbot renew
systemctl reload nginx

# Check renewal status
certbot certificates
```

### Nginx Configuration Errors

**Problem**: Nginx fails to reload after certificate installation

**Solution**:
```bash
# Test Nginx configuration
nginx -t

# Check for errors
tail -f /var/log/nginx/error.log

# Fix configuration and reload
systemctl reload nginx
```

## Security Best Practices

1. ✅ **Always use HTTPS** - Redirect all HTTP to HTTPS
2. ✅ **Enable HSTS** - Add to Nginx config:
   ```nginx
   add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
   ```
3. ✅ **Keep Certbot updated**:
   ```bash
   apt-get update && apt-get upgrade certbot
   ```
4. ✅ **Monitor certificate expiration**:
   ```bash
   certbot certificates
   ```

## Next Steps

After SSL is configured:

1. ✅ Test your site: https://fightcitytickets.com
2. ✅ Update application configuration
3. ✅ Test all functionality over HTTPS
4. ✅ Set up monitoring for certificate expiration
5. ✅ Update any external services (Stripe webhooks, etc.) to use HTTPS URLs

## Support

- Let's Encrypt Docs: https://letsencrypt.org/docs/
- Certbot Docs: https://certbot.eff.org/
- SSL Test: https://www.ssllabs.com/ssltest/

---

**Domain**: fightcitytickets.com  
**Server IP**: 178.156.215.100  
**Last Updated**: 2025-01-09

