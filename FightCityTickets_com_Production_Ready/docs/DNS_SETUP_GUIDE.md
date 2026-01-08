# DNS Setup Guide for fightcitytickets.com

This guide will help you configure your domain to point to your server at `178.156.215.100`.

## Quick Setup (Namecheap Dashboard)

### Step 1: Access Namecheap DNS Settings

1. Log in to Namecheap: https://ap.www.namecheap.com/
2. Go to **Domain List**: https://ap.www.namecheap.com/domains/list/
3. Click **Manage** next to `fightcitytickets.com`
4. Navigate to the **Advanced DNS** tab

### Step 2: Configure DNS Records

You need to add/update these DNS records:

#### A Record (Root Domain)
- **Type**: A Record
- **Host**: `@` (or leave blank)
- **Value**: `178.156.215.100`
- **TTL**: Automatic (or 1800 seconds)

#### A Record (WWW Subdomain)
- **Type**: A Record
- **Host**: `www`
- **Value**: `178.156.215.100`
- **TTL**: Automatic (or 1800 seconds)

### Step 3: Remove Conflicting Records

If you see any existing A records pointing to different IPs, **delete them** or update them to `178.156.215.100`.

### Step 4: Verify Configuration

Your DNS records should look like this:

```
Type    Host    Value              TTL
A       @       178.156.215.100    Automatic
A       www     178.156.215.100    Automatic
```

## DNS Propagation

After saving your DNS records:

1. **Wait 5-30 minutes** for DNS propagation
2. DNS changes can take up to 48 hours globally, but usually work within 30 minutes

## Testing DNS Configuration

### Test from Command Line

```bash
# Check if DNS is pointing to your server
nslookup fightcitytickets.com

# Should return: 178.156.215.100

# Check www subdomain
nslookup www.fightcitytickets.com

# Should return: 178.156.215.100
```

### Test from Browser

1. Wait 10-30 minutes after DNS changes
2. Visit: `http://fightcitytickets.com` (should load your site)
3. Visit: `http://www.fightcitytickets.com` (should also load)

### Online DNS Checkers

Use these tools to verify DNS propagation globally:
- https://www.whatsmydns.net/#A/fightcitytickets.com
- https://dnschecker.org/#A/fightcitytickets.com

## Server Configuration

Make sure your server is configured to accept requests for this domain:

### Nginx Configuration (if using)

Your server should have Nginx configured to:
- Listen on port 80 (HTTP) and 443 (HTTPS)
- Serve requests for `fightcitytickets.com` and `www.fightcitytickets.com`
- Redirect HTTP to HTTPS (recommended)

### Docker Configuration

Your `docker-compose.yml` should expose:
- Port 80 for HTTP
- Port 443 for HTTPS (if SSL is configured)

## SSL Certificate Setup (Recommended)

After DNS is configured, set up SSL:

```bash
# SSH into your server
ssh root@178.156.215.100

# Install certbot
apt-get update
apt-get install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com

# Follow the prompts to complete SSL setup
```

## Troubleshooting

### DNS Not Resolving

1. **Check DNS records** in Namecheap dashboard
2. **Wait longer** - DNS can take time to propagate
3. **Clear DNS cache** on your local machine:
   ```bash
   # Windows
   ipconfig /flushdns
   
   # Mac/Linux
   sudo dscacheutil -flushcache
   ```

### Site Not Loading After DNS Resolves

1. **Check server is running**:
   ```bash
   ssh root@178.156.215.100 "docker-compose ps"
   ```

2. **Check Nginx is running**:
   ```bash
   ssh root@178.156.215.100 "systemctl status nginx"
   ```

3. **Check server logs**:
   ```bash
   ssh root@178.156.215.100 "docker-compose logs -f"
   ```

### Wrong IP Address

If DNS is pointing to the wrong IP:
1. Go back to Namecheap Advanced DNS
2. Update the A record value to `178.156.215.100`
3. Wait for propagation

## Security Notes

⚠️ **Important**: 
- Never commit API credentials to git
- Store credentials securely
- Use environment variables for sensitive data
- Rotate API keys regularly

## Next Steps

After DNS is configured:

1. ✅ Test domain resolution
2. ✅ Set up SSL certificate (Let's Encrypt)
3. ✅ Update application configuration if needed
4. ✅ Test full application flow
5. ✅ Monitor server logs

## Support

If you encounter issues:
- Check Namecheap documentation: https://www.namecheap.com/support/
- Verify server is accessible: `curl http://178.156.215.100`
- Check server firewall allows port 80/443

---

**Domain**: fightcitytickets.com  
**Server IP**: 178.156.215.100  
**Last Updated**: 2025-01-09

