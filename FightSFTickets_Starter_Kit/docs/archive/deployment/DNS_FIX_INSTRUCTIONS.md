# 🚨 DNS Configuration for fightcitytickets.com

## Problem
The domain `fightcitytickets.com` is **NOT** in your Namecheap account.

## Solutions

### Option 1: Register the Domain (RECOMMENDED)
1. Go to Namecheap: https://www.namecheap.com/domains/registration/results/?domain=fightcitytickets.com
2. Register `fightcitytickets.com` if available
3. After registration, run: `python scripts/fix_dns_now.py`

### Option 2: Configure DNS at Current Registrar
If the domain is registered elsewhere:

1. **Log into your domain registrar** (GoDaddy, Google Domains, etc.)
2. **Find DNS Management** section
3. **Add these A records:**
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
4. **Save changes**
5. **Wait 5-30 minutes** for DNS to propagate

### Option 3: Transfer Domain to Namecheap
1. Go to: https://www.namecheap.com/domains/transfer/
2. Transfer `fightcitytickets.com` to Namecheap
3. After transfer completes, run: `python scripts/fix_dns_now.py`

## Quick Manual DNS Setup (Any Registrar)

**If domain is registered anywhere:**

1. Log into your registrar
2. Go to DNS Management / DNS Settings
3. Add these records:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 178.156.215.100 | 3600 |
| A | www | 178.156.215.100 | 3600 |

4. Save and wait 5-30 minutes

## Verify DNS After Setup

```bash
# Check DNS resolution
nslookup fightcitytickets.com
nslookup www.fightcitytickets.com

# Should show: 178.156.215.100
```

## Next Steps After DNS Works

1. **Deploy code to server** (if not already deployed)
2. **Set up SSL certificate:**
   ```bash
   ssh root@178.156.215.100
   certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com
   ```
3. **Test the site:** https://fightcitytickets.com

## Need Help?

- Check which registrar has the domain: https://whois.net/
- Namecheap DNS guide: https://www.namecheap.com/support/knowledgebase/article.aspx/319/2237/


