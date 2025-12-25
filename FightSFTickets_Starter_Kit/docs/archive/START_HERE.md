# 🚀 START HERE - Deploy FightSFTickets to Hetzner Cloud

**Welcome!** Your FightSFTickets application is 100% ready for production deployment.

---

## ⚡ Deploy in 3 Commands (15 minutes)

```bash
# 1. Set your Hetzner API token
export HETZNER_API_TOKEN="YOUR_HETZNER_API_TOKEN"

# 2. Navigate to project
cd FightSFTickets_Starter_Kit

# 3. Run deployment script
chmod +x scripts/deploy_hetzner.sh
./scripts/deploy_hetzner.sh
```

**That's it!** ☕ The script handles everything automatically.

---

## 🔑 API Keys Needed

Have these ready before starting (the script will prompt you):

### 1. Stripe (Payment Processing)
- Sign up: https://stripe.com
- Get key: https://dashboard.stripe.com/apikeys
- Copy: **Secret Key** (starts with `sk_test_`)

### 2. Lob (Physical Mail Delivery)
- Sign up: https://www.lob.com
- Get key: https://dashboard.lob.com/settings/keys
- Copy: **Test Secret Key** (starts with `test_`)

### 3. OpenAI (Audio Transcription)
- Sign up: https://platform.openai.com
- Add $5 credit: https://platform.openai.com/account/billing
- Get key: https://platform.openai.com/api-keys
- Copy: **API Key** (starts with `sk-`)

### 4. DeepSeek (AI Statement Refinement)
- Sign up: https://platform.deepseek.com
- Get key: https://platform.deepseek.com/api-keys
- Copy: **API Key** (starts with `sk-`)

**Tip:** Open all these tabs before running the deployment script.

---

## 📊 What Gets Deployed

### Infrastructure
- **Server:** Hetzner CX21 (2 vCPU, 4GB RAM, 40GB SSD)
- **Location:** Ashburn, VA (configurable)
- **OS:** Ubuntu 22.04 LTS
- **Cost:** ~$7/month

### Application
- **Frontend:** Next.js 14 (modern React app)
- **Backend:** FastAPI (Python REST API)
- **Database:** PostgreSQL 16
- **Proxy:** Nginx + SSL support

### Security
- ✅ Firewall configured
- ✅ SSL ready (Let's Encrypt)
- ✅ Rate limiting enabled
- ✅ Secure environment variables

---

## ⏱️ Deployment Timeline

1. **Prerequisites Check** (1 min)
   - Verify Hetzner token
   - Check required tools

2. **Server Creation** (3 min)
   - Provision CX21 server
   - Wait for server boot

3. **Dependency Installation** (3 min)
   - Install Docker & Docker Compose
   - Install Nginx & Certbot
   - Configure firewall

4. **Application Deployment** (3 min)
   - Copy project files
   - Configure environment
   - Set up Docker Compose

5. **Service Startup** (3 min)
   - Build Docker images
   - Start all containers
   - Run database migrations

6. **Verification** (2 min)
   - Check service health
   - Display server details
   - Show next steps

**Total:** ~15 minutes (mostly automated)

---

## 🎉 After Deployment

You'll see your server IP address:

```
========================================
✅ Deployment Complete!
========================================

Server IP: xxx.xxx.xxx.xxx
```

### Next Steps:

### 1. Configure DNS (5 minutes)
Point your domain to the server IP:
```
Type    Name    Value               TTL
A       @       xxx.xxx.xxx.xxx     3600
A       www     xxx.xxx.xxx.xxx     3600
```

### 2. Set Up SSL (2 minutes)
After DNS propagates:
```bash
ssh root@xxx.xxx.xxx.xxx
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. Configure Stripe Webhook (2 minutes)
1. Go to: https://dashboard.stripe.com/webhooks
2. Add endpoint: `https://yourdomain.com/api/webhooks/stripe`
3. Select events: `checkout.session.completed`, `payment_intent.succeeded`
4. Update webhook secret in `.env` on server

### 4. Test Everything (5 minutes)
- Visit: https://yourdomain.com
- Complete test appeal
- Use test card: `4242 4242 4242 4242`
- Verify in Stripe and Lob dashboards

---

## 📚 Documentation Guide

### Quick Start
- **`START_HERE.md`** (this file) - Quick overview ⭐
- **`DEPLOY_NOW.md`** - Detailed quick start guide

### Complete Guides
- **`DEPLOYMENT_COMPLETE.md`** - Everything about deployment
- **`DEPLOYMENT_SUMMARY.md`** - Technical summary and costs
- **`docs/DEPLOYMENT_GUIDE.md`** - Complete step-by-step guide
- **`docs/SERVICE_INTEGRATION_CHECKLIST.md`** - API integration

### Operations
- **`RUNBOOK.md`** - Day-to-day operations manual
- **`scripts/README.md`** - All deployment scripts explained
- **`README.md`** - Project overview and features

### Reference
- **`IMPLEMENTATION_STATUS.md`** - Feature completion status
- **`docker-compose.yml`** - Docker configuration

---

## 🔄 Common Tasks

### View Application Logs
```bash
ssh root@xxx.xxx.xxx.xxx
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml logs -f
```

### Restart a Service
```bash
ssh root@xxx.xxx.xxx.xxx
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml restart api
```

### Update Deployment (After Code Changes)
```bash
SERVER_IP=xxx.xxx.xxx.xxx ./scripts/update_deployment.sh
```

### Check Service Health
```bash
curl https://yourdomain.com/health
```

### Backup Database
```bash
ssh root@xxx.xxx.xxx.xxx
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres fightsf | gzip > backup.sql.gz
```

---

## 💰 Cost Breakdown

### Fixed Monthly Costs
- Hetzner Server: ~$7/month
- Domain (if purchased): ~$1/month
- SSL Certificate: FREE
- **Total Fixed:** ~$8/month

### Variable Costs (Per Appeal)
- Stripe: 2.9% + $0.30
- Lob Standard Mail: ~$0.60
- Lob Certified Mail: ~$6.50
- OpenAI: ~$0.012
- DeepSeek: ~$0.02
- **Total Variable:** ~$0.93 - $6.83 per appeal

### Example Revenue (100 Appeals @ $29.99)
- Revenue: $2,999/month
- Costs: ~$188/month
- **Profit: ~$2,811/month** 💰

---

## 🚨 Troubleshooting

### "Services not starting"
```bash
ssh root@xxx.xxx.xxx.xxx
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml logs
docker-compose -f docker-compose.prod.yml restart
```

### "Can't connect to server"
- Check DNS has propagated: https://dnschecker.org
- Try IP address instead: http://xxx.xxx.xxx.xxx
- Verify firewall: ports 80 and 443 should be open

### "Payment not working"
- Verify Stripe keys in `.env`
- Check webhook configured correctly
- Use test card: 4242 4242 4242 4242
- Check Stripe Dashboard for errors

### "SSL certificate issues"
```bash
ssh root@xxx.xxx.xxx.xxx
certbot renew
systemctl restart nginx
```

---

## 🎯 Success Checklist

Your deployment is successful when:

- ✅ All Docker containers running: `docker ps`
- ✅ Health check passes: `curl http://server-ip/health`
- ✅ Frontend loads in browser
- ✅ Can complete full appeal flow
- ✅ Test payment processes successfully
- ✅ Stripe receives payment
- ✅ Lob receives mailing job
- ✅ No errors in logs

---

## 📞 Need Help?

### Check These Resources
1. **Quick Issues:** See troubleshooting section above
2. **Detailed Guide:** Read `DEPLOYMENT_GUIDE.md`
3. **Service Integration:** Check `SERVICE_INTEGRATION_CHECKLIST.md`
4. **Operations:** Review `RUNBOOK.md`

### Service Support
- **Stripe:** https://support.stripe.com
- **Lob:** https://support.lob.com
- **OpenAI:** https://help.openai.com
- **Hetzner:** https://docs.hetzner.com/cloud

### Quick Commands
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs | grep -i error

# Restart everything
docker-compose -f docker-compose.prod.yml restart

# Check resource usage
docker stats

# Check disk space
df -h
```

---

## ✅ Pre-Deployment Checklist

Before you start:

- [ ] Have Hetzner token ready (you already have this!)
- [ ] Have all API keys ready (Stripe, Lob, OpenAI, DeepSeek)
- [ ] Have 15-20 minutes available
- [ ] Have coffee/tea ready ☕
- [ ] Read through this document
- [ ] Open all service dashboards in browser tabs

---

## 🎓 What's Next?

### Immediate (After Deployment)
1. ✅ Run deployment script (15 min)
2. ⏳ Configure DNS (5 min)
3. ⏳ Set up SSL certificate (2 min)
4. ⏳ Configure Stripe webhook (2 min)
5. ⏳ Test complete flow (5 min)

### First Week
- Monitor application daily
- Review service costs
- Test with real users
- Keep API keys in test mode
- Document any issues

### Going Live
- Switch to live Stripe keys (`sk_live_`)
- Switch to live Lob keys (`live_`)
- Set up automated backups
- Configure monitoring alerts
- Announce your service!

---

## 💡 Pro Tips

1. **Start with test keys** - Don't use live keys until fully tested
2. **Test thoroughly** - Complete several full flows before announcing
3. **Set spending limits** - In all service dashboards
4. **Monitor daily** - Especially first week
5. **Backup regularly** - Database backups are critical
6. **Keep keys secure** - Never commit to git
7. **Stay updated** - Check for security updates monthly

---

## 🎉 Ready to Deploy!

You have everything you need:

✅ **Hetzner Token:** Ready  
✅ **Deployment Script:** Ready  
✅ **Documentation:** Complete  
✅ **Application Code:** Production-ready  
✅ **Service Integrations:** Configured  

**Just run:**

```bash
export HETZNER_API_TOKEN="YOUR_HETZNER_API_TOKEN"
cd FightSFTickets_Starter_Kit
./scripts/deploy_hetzner.sh
```

**And you're live in 15 minutes! 🚀**

---

## 🌟 You're Helping People!

Remember: You're building a service that helps people fight unfair parking tickets. You're making a real difference in people's lives by:

- Saving them money on unfair fines
- Providing affordable legal document preparation
- Making the appeal process accessible
- Automating tedious paperwork

**That's awesome! Let's deploy! 🎊**

---

**Version:** 1.0.0  
**Created:** 2025-01-09  
**Status:** Ready for Production Deployment  
**Estimated Time:** 15 minutes  
**Difficulty:** ⭐ Easy

**Good luck! You've got this! 💪**