# 🚀 DEPLOY NOW - Quick Start Guide

**Ready to deploy FightSFTickets to production?**  
This guide will get your application running in ~15 minutes.

---

## ⚡ Prerequisites (5 minutes)

You already have your Hetzner API token. Now get these:

### 1. Stripe Account (2 minutes)
- Sign up: https://stripe.com
- Get keys: https://dashboard.stripe.com/apikeys
- Copy your `Secret key` (starts with `sk_test_`)

### 2. Lob Account (2 minutes)
- Sign up: https://www.lob.com
- Get key: https://dashboard.lob.com/settings/keys
- Copy your `Test Secret Key` (starts with `test_`)

### 3. OpenAI Account (1 minute)
- Sign up: https://platform.openai.com
- Add $5 credit: https://platform.openai.com/account/billing
- Get key: https://platform.openai.com/api-keys
- Copy your API key (starts with `sk-`)

### 4. DeepSeek Account (1 minute)
- Sign up: https://platform.deepseek.com
- Get key: https://platform.deepseek.com/api-keys
- Copy your API key (starts with `sk-`)

---

## 🎯 Deploy in 3 Commands

### Step 1: Set Your Hetzner Token

```bash
export HETZNER_API_TOKEN="YOUR_HETZNER_API_TOKEN"
```

### Step 2: Configure Your Domain (Optional)

```bash
export DOMAIN="fightsftickets.com"  # Change to your domain
```

If you don't have a domain yet, skip this. You can access via IP address.

### Step 3: Run Deployment Script

```bash
cd FightSFTickets_Starter_Kit
chmod +x scripts/deploy_hetzner.sh
./scripts/deploy_hetzner.sh
```

### Step 4: Enter API Keys When Prompted

The script will ask for:
- Stripe Secret Key
- Stripe Webhook Secret (press Enter to skip for now)
- Lob API Key
- OpenAI API Key
- DeepSeek API Key

**Paste each key when prompted and press Enter.**

---

## ⏰ What Happens Next? (10-15 minutes)

The deployment script will automatically:

1. ✅ Create SSH key if needed
2. ✅ Upload SSH key to Hetzner
3. ✅ Create server (CX21: 2 vCPU, 4GB RAM)
4. ✅ Wait for server to be ready
5. ✅ Install Docker and dependencies
6. ✅ Configure firewall
7. ✅ Deploy your application
8. ✅ Start all services
9. ✅ Run database migrations

**Grab a coffee while it works! ☕**

---

## 🎉 After Deployment

The script will display:

```
========================================
Deployment Complete!
========================================

Server Details:
  IP Address: xxx.xxx.xxx.xxx
  Domain: fightsftickets.com
  Deploy Path: /var/www/fightsftickets

Services:
  Frontend: http://xxx.xxx.xxx.xxx:80
  Backend API: http://xxx.xxx.xxx.xxx/api
  Health Check: http://xxx.xxx.xxx.xxx/health
```

---

## 🔧 Configure DNS (5 minutes)

### If You Have a Domain:

1. Go to your domain registrar (GoDaddy, Namecheap, etc.)
2. Add these DNS records:

```
Type    Name    Value                   TTL
A       @       xxx.xxx.xxx.xxx         3600
A       www     xxx.xxx.xxx.xxx         3600
```

Replace `xxx.xxx.xxx.xxx` with your server IP.

3. Wait 5-60 minutes for DNS propagation

4. Test: Open http://yourdomain.com in browser

### No Domain Yet?

Just use the IP address: http://xxx.xxx.xxx.xxx

---

## 🔒 Setup SSL (5 minutes)

**After DNS is working:**

```bash
ssh root@xxx.xxx.xxx.xxx
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow prompts:
- Enter your email
- Agree to terms (Y)
- Choose redirect to HTTPS (2)

**Done! Your site is now HTTPS! 🎉**

---

## 🎯 Setup Stripe Webhooks (2 minutes)

1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter: `https://yourdomain.com/api/webhooks/stripe`
4. Select events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Click "Add endpoint"
6. Copy the "Signing secret" (starts with `whsec_`)

7. Update on server:

```bash
ssh root@xxx.xxx.xxx.xxx
nano /var/www/fightsftickets/.env
```

Find `STRIPE_WEBHOOK_SECRET` and paste your secret, then:

```bash
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml restart api
```

---

## ✅ Test Your Deployment

### 1. Check Health
```bash
curl http://your-ip-or-domain/health
```

Should return: `{"status":"healthy",...}`

### 2. Test Frontend
Open in browser: http://your-ip-or-domain

Should see the FightSFTickets homepage.

### 3. Test Payment Flow

1. Go through appeal flow
2. Use test card: `4242 4242 4242 4242`
3. Any future expiry date
4. Any 3-digit CVC
5. Any 5-digit ZIP

### 4. Verify in Dashboards

- **Stripe:** https://dashboard.stripe.com/payments
- **Lob:** https://dashboard.lob.com
- **OpenAI:** https://platform.openai.com/usage

---

## 🚨 Common Issues

### "Services not starting"
```bash
ssh root@xxx.xxx.xxx.xxx
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml logs
```

### "Can't connect to server"
- Check firewall allows ports 80 and 443
- Verify DNS has propagated (use https://dnschecker.org)
- Try IP address instead of domain

### "Payment not working"
- Verify Stripe keys in `.env`
- Check webhook configured correctly
- Use test card: 4242 4242 4242 4242

### "SSL not working"
```bash
ssh root@xxx.xxx.xxx.xxx
certbot renew --dry-run
systemctl restart nginx
```

---

## 📊 View Logs

```bash
# SSH to server
ssh root@xxx.xxx.xxx.xxx

# View all logs
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml logs -f

# View specific service
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f web
```

---

## 🔄 Update Your Deployment

When you make code changes:

```bash
# From your local machine
SERVER_IP=xxx.xxx.xxx.xxx ./scripts/update_deployment.sh
```

This script:
- Creates automatic backup
- Updates code
- Rebuilds services
- Runs migrations
- Verifies deployment

---

## 📈 Monitor Your App

### Health Check
```bash
curl https://yourdomain.com/health
```

### Service Status
```bash
ssh root@xxx.xxx.xxx.xxx
docker ps
```

### Resource Usage
```bash
ssh root@xxx.xxx.xxx.xxx
docker stats
```

---

## 🎓 Next Steps

### 1. Go Live
- Switch to live Stripe keys (`sk_live_`)
- Switch to live Lob keys (`live_`)
- Update `.env` on server
- Restart services

### 2. Set Up Monitoring
- Configure uptime monitoring (UptimeRobot, Pingdom)
- Set up error alerts
- Monitor API usage and costs

### 3. Set Up Backups
```bash
# Add to crontab on server
0 2 * * * cd /var/www/fightsftickets && docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres fightsf | gzip > /var/backups/fightsftickets_$(date +\%Y\%m\%d).sql.gz
```

### 4. Optimize
- Add CDN for static assets
- Enable caching
- Optimize images
- Monitor performance

---

## 📚 Documentation

- **Full Deployment Guide:** `docs/DEPLOYMENT_GUIDE.md`
- **Service Integration:** `docs/SERVICE_INTEGRATION_CHECKLIST.md`
- **Operations Manual:** `RUNBOOK.md`
- **Project Overview:** `README.md`

---

## 🆘 Need Help?

### Check These First:
1. Health endpoint: `curl http://your-domain/health`
2. Service logs: `docker-compose logs`
3. Stripe dashboard for payment errors
4. Lob dashboard for mail status

### Emergency Commands:
```bash
# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart api

# View errors
docker-compose -f docker-compose.prod.yml logs | grep -i error

# Check disk space
df -h

# Check memory
free -h
```

---

## 🎉 You're Live!

Your FightSFTickets application is now deployed and ready to process parking ticket appeals!

**What's Working:**
- ✅ Frontend application
- ✅ Backend API
- ✅ Database (PostgreSQL)
- ✅ Payment processing (Stripe)
- ✅ Physical mail delivery (Lob)
- ✅ Audio transcription (OpenAI)
- ✅ AI statement refinement (DeepSeek)

**Your URLs:**
- Frontend: https://yourdomain.com
- API: https://yourdomain.com/api
- Health: https://yourdomain.com/health

---

## 💡 Pro Tips

1. **Keep test mode on** until you've verified everything works
2. **Test the full flow** yourself before announcing
3. **Set spending limits** in all service dashboards
4. **Monitor daily** for the first week
5. **Back up database** before any changes
6. **Keep API keys secure** - never commit to git
7. **Update dependencies** regularly
8. **Review logs** for errors

---

## 🔐 Security Checklist

- [ ] SSL certificate installed and working
- [ ] Firewall configured (only ports 80, 443, 22)
- [ ] Strong database password set
- [ ] API keys stored securely
- [ ] .env file has 600 permissions
- [ ] Backups configured
- [ ] Monitoring alerts set up
- [ ] Rate limiting enabled (Nginx)

---

## 📞 Service Contacts

- **Stripe Support:** https://support.stripe.com
- **Lob Support:** https://support.lob.com  
- **OpenAI Help:** https://help.openai.com
- **Hetzner Support:** https://docs.hetzner.com

---

**Congratulations! Your FightSFTickets platform is live! 🎊**

*Remember: You're helping people fight unfair parking tickets. That's awesome!*

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-09  
**Deployment Time:** ~15 minutes  
**Difficulty:** Easy ⭐

Made with ❤️ for justice seekers everywhere.