# FightSFTickets - Service Integration Checklist

**Purpose:** Ensure all external services are properly configured and integrated  
**Version:** 1.0.0  
**Last Updated:** 2025-01-09

---

## Pre-Integration Checklist

Before starting integration, ensure you have:

- [ ] Access to all service dashboards
- [ ] API keys documented and stored securely
- [ ] Test mode enabled for all services
- [ ] Credit card/billing set up for paid services
- [ ] Server deployed and accessible
- [ ] `.env` file created on server

---

## 1. Stripe Integration

### Setup Steps

- [ ] **Create Stripe Account**
  - URL: https://stripe.com
  - Verify email address
  - Complete business information

- [ ] **Get API Keys**
  - Navigate to: https://dashboard.stripe.com/apikeys
  - Copy "Secret key" (starts with `sk_test_` for test mode)
  - Save to `.env` as `STRIPE_SECRET_KEY`

- [ ] **Create Webhook**
  - Navigate to: https://dashboard.stripe.com/webhooks
  - Click "Add endpoint"
  - URL: `https://your-domain.com/api/webhooks/stripe`
  - Select events:
    - [x] `checkout.session.completed`
    - [x] `payment_intent.succeeded`
    - [x] `payment_intent.payment_failed`
  - Copy "Signing secret" (starts with `whsec_`)
  - Save to `.env` as `STRIPE_WEBHOOK_SECRET`

- [ ] **Configure Products** (Optional)
  - Create product for "Parking Ticket Appeal"
  - Set pricing (e.g., $29.99 standard, $49.99 certified)
  - Note product IDs for backend configuration

### Testing

- [ ] Test payment flow with test card: `4242 4242 4242 4242`
- [ ] Verify payment appears in Stripe Dashboard
- [ ] Check webhook events are received (Dashboard → Events)
- [ ] Confirm payment success page loads
- [ ] Verify database records created correctly

### Production Activation

- [ ] Switch to live mode in Stripe Dashboard
- [ ] Get live API keys (starts with `sk_live_`)
- [ ] Update `.env` with live keys
- [ ] Update webhook URL to production domain
- [ ] Test with real card (small amount)
- [ ] Set up email receipts in Stripe settings

### Status: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## 2. Lob Integration

### Setup Steps

- [ ] **Create Lob Account**
  - URL: https://www.lob.com
  - Sign up for account
  - Verify email and identity

- [ ] **Get API Key**
  - Navigate to: https://dashboard.lob.com/settings/keys
  - Copy "Test Secret Key" (starts with `test_`)
  - Save to `.env` as `LOB_API_KEY`

- [ ] **Verify Address Format**
  - Ensure return address is configured
  - Test address validation API
  - Configure address book if needed

- [ ] **Review Pricing**
  - Standard mail: ~$0.60 per letter
  - Certified mail: ~$6.50 per letter
  - Understand billing cycle

### Testing

- [ ] Send test letter to your address
- [ ] Verify letter appears in Lob Dashboard
- [ ] Check letter status updates
- [ ] Confirm "Test Mode" indicator on letter
- [ ] Review PDF preview in dashboard

### Production Activation

- [ ] Add credit to Lob account
- [ ] Get live API key (starts with `live_`)
- [ ] Update `.env` with live key
- [ ] Send real test letter to verify quality
- [ ] Set up billing alerts
- [ ] Configure postcard/letter templates (if custom)

### Status: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## 3. OpenAI Integration

### Setup Steps

- [ ] **Create OpenAI Account**
  - URL: https://platform.openai.com
  - Sign up and verify email
  - Add payment method

- [ ] **Get API Key**
  - Navigate to: https://platform.openai.com/api-keys
  - Click "Create new secret key"
  - Copy key (starts with `sk-`)
  - Save to `.env` as `OPENAI_API_KEY`

- [ ] **Set Usage Limits** (Recommended)
  - Navigate to: https://platform.openai.com/account/billing/limits
  - Set monthly budget limit (e.g., $50)
  - Set up email notifications

- [ ] **Add Credit**
  - Navigate to: https://platform.openai.com/account/billing
  - Add initial credit (minimum $5)

### Testing

- [ ] Test audio transcription endpoint
- [ ] Upload sample audio file (1-2 minutes)
- [ ] Verify transcription accuracy
- [ ] Check usage in OpenAI dashboard
- [ ] Monitor API response times

### Production Monitoring

- [ ] Set up usage alerts
- [ ] Monitor costs daily for first week
- [ ] Review transcription quality regularly
- [ ] Adjust budget limits as needed
- [ ] Keep backup API key secure

### Status: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## 4. DeepSeek Integration

### Setup Steps

- [ ] **Create DeepSeek Account**
  - URL: https://platform.deepseek.com
  - Sign up and verify email
  - Complete account setup

- [ ] **Get API Key**
  - Navigate to: https://platform.deepseek.com/api-keys
  - Generate new API key
  - Copy key (starts with `sk-`)
  - Save to `.env` as `DEEPSEEK_API_KEY`

- [ ] **Review Pricing**
  - Understand token costs
  - Review rate limits
  - Add initial credit if required

- [ ] **Test API Access**
  - Make test API call
  - Verify rate limits
  - Check response quality

### Testing

- [ ] Test statement refinement feature
- [ ] Enter sample user statement
- [ ] Click "Polish with AI" button
- [ ] Verify improved output
- [ ] Check response time acceptable (<3 seconds)

### Production Monitoring

- [ ] Monitor API usage
- [ ] Review output quality
- [ ] Set up alerts for high usage
- [ ] Keep track of costs
- [ ] Have fallback option if service unavailable

### Status: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## 5. Database (PostgreSQL)

### Setup Steps

- [ ] **Verify Database Running**
  ```bash
  docker-compose -f docker-compose.prod.yml ps db
  ```

- [ ] **Check Database Connection**
  ```bash
  docker-compose -f docker-compose.prod.yml exec db pg_isready
  ```

- [ ] **Run Initial Migrations**
  ```bash
  docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
  ```

- [ ] **Verify Tables Created**
  ```bash
  docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d fightsf -c "\dt"
  ```

### Testing

- [ ] Create test database entry
- [ ] Verify data persistence after restart
- [ ] Test database backup procedure
- [ ] Test database restore procedure
- [ ] Check query performance

### Production Configuration

- [ ] Set strong database password
- [ ] Configure automatic backups (daily)
- [ ] Set up backup retention policy
- [ ] Test backup restoration
- [ ] Monitor database size and performance

### Status: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## 6. Email (Optional - Future Enhancement)

### Setup Steps

- [ ] **Choose Email Provider**
  - SendGrid
  - AWS SES
  - Mailgun
  - Resend

- [ ] **Get API Credentials**
  - Sign up for service
  - Get API key or SMTP credentials
  - Verify domain ownership

- [ ] **Configure Email Templates**
  - Receipt confirmation
  - Appeal submitted confirmation
  - Letter mailed notification

### Testing

- [ ] Send test emails
- [ ] Verify deliverability
- [ ] Check spam scores
- [ ] Test all templates
- [ ] Verify links work

### Status: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Environment Variables Verification

Use this checklist to verify all required environment variables are set:

```bash
# Check environment variables are set
cat .env
```

### Required Variables

- [ ] `APP_ENV=production`
- [ ] `APP_URL` set to your domain
- [ ] `API_URL` set to your API endpoint
- [ ] `CORS_ORIGINS` includes your domain
- [ ] `DATABASE_URL` configured correctly
- [ ] `POSTGRES_USER` set
- [ ] `POSTGRES_PASSWORD` set (strong password)
- [ ] `POSTGRES_DB=fightsf`
- [ ] `STRIPE_SECRET_KEY` set (sk_test_ or sk_live_)
- [ ] `STRIPE_WEBHOOK_SECRET` set (whsec_)
- [ ] `LOB_API_KEY` set (test_ or live_)
- [ ] `OPENAI_API_KEY` set (sk-)
- [ ] `DEEPSEEK_API_KEY` set (sk-)
- [ ] `SECRET_KEY` set (random string)
- [ ] `NEXT_PUBLIC_API_BASE` set to API URL

### Security Check

- [ ] `.env` file has 600 permissions (`chmod 600 .env`)
- [ ] `.env` is in `.gitignore`
- [ ] No API keys in version control
- [ ] Passwords are strong and unique
- [ ] API keys are kept in password manager

---

## Integration Testing

### End-to-End Flow Test

- [ ] **Step 1: Citation Entry**
  - Enter valid citation number
  - Verify validation works
  - Check data saved to session

- [ ] **Step 2: Photo Upload**
  - Upload evidence photos
  - Verify upload completes
  - Check images stored correctly

- [ ] **Step 3: Voice Recording**
  - Record audio statement
  - Verify transcription works (OpenAI)
  - Check transcription accuracy

- [ ] **Step 4: Statement Refinement**
  - Click "Polish with AI"
  - Verify DeepSeek response
  - Check improved statement quality

- [ ] **Step 5: Review**
  - Review generated letter
  - Verify all details correct
  - Check letter formatting

- [ ] **Step 6: Signature**
  - Draw signature
  - Verify signature captured
  - Check signature appears on letter

- [ ] **Step 7: Payment**
  - Enter user details
  - Complete Stripe payment
  - Verify payment success

- [ ] **Step 8: Confirmation**
  - Check success page loads
  - Verify confirmation details
  - Check email sent (if configured)

- [ ] **Step 9: Backend Processing**
  - Verify database records created
  - Check Lob API called
  - Confirm letter queued for mailing
  - Verify webhook received from Stripe

### Performance Testing

- [ ] Test with slow internet connection
- [ ] Test with multiple concurrent users
- [ ] Verify rate limiting works
- [ ] Check API response times (<500ms)
- [ ] Test file upload with large images

### Error Handling Testing

- [ ] Test with invalid API keys
- [ ] Test with expired payment method
- [ ] Test with network timeouts
- [ ] Verify error messages are user-friendly
- [ ] Check errors logged properly

---

## Post-Integration Monitoring

### Daily Checks (First Week)

- [ ] Check application health endpoint
- [ ] Review error logs
- [ ] Monitor API usage for all services
- [ ] Check payment processing success rate
- [ ] Verify mail delivery status in Lob

### Weekly Checks (Ongoing)

- [ ] Review service costs
- [ ] Check for failed payments
- [ ] Monitor API rate limits
- [ ] Review database backup success
- [ ] Check SSL certificate expiry

### Monthly Checks

- [ ] Review all service invoices
- [ ] Analyze usage patterns
- [ ] Optimize API calls if needed
- [ ] Update dependencies
- [ ] Review and rotate API keys

---

## Troubleshooting Integration Issues

### Stripe Issues

**Problem:** Webhook not receiving events
- Check webhook URL is correct
- Verify webhook secret is correct
- Check firewall allows Stripe IPs
- Review webhook logs in Stripe Dashboard

**Problem:** Payment fails
- Verify API keys are correct
- Check Stripe Dashboard for errors
- Ensure test mode matches API keys
- Review backend logs for Stripe errors

### Lob Issues

**Problem:** Letters not sending
- Verify API key is correct
- Check account has sufficient balance
- Ensure addresses are formatted correctly
- Review Lob Dashboard for errors

**Problem:** Letters in test mode
- Switch to live API key
- Verify `live_` prefix on API key
- Check environment variable updated

### OpenAI Issues

**Problem:** Transcription fails
- Verify API key is valid
- Check account has credit
- Ensure audio file format supported
- Review rate limits not exceeded

**Problem:** Slow transcription
- Check audio file size (optimize if >10MB)
- Verify network connectivity
- Consider caching results

### DeepSeek Issues

**Problem:** AI refinement not working
- Verify API key is correct
- Check service status
- Review rate limits
- Test API directly with curl

**Problem:** Poor quality responses
- Adjust prompt in backend code
- Review input statement quality
- Consider alternative AI service

---

## Final Verification

Before going live, complete this final checklist:

- [ ] All services tested end-to-end
- [ ] All API keys switched to production mode
- [ ] All environment variables verified
- [ ] Backups configured and tested
- [ ] Monitoring and alerts set up
- [ ] SSL certificate installed and valid
- [ ] DNS configured correctly
- [ ] Payment flow tested with real card
- [ ] Physical letter received and verified
- [ ] Error handling tested
- [ ] Performance acceptable under load
- [ ] Security best practices followed
- [ ] Documentation updated
- [ ] Team trained on operations
- [ ] Support procedures in place

---

## Service Status Dashboard

| Service | Status | Test Mode | Production Mode | Notes |
|---------|--------|-----------|-----------------|-------|
| Stripe | ⬜ | ⬜ | ⬜ | Payment processing |
| Lob | ⬜ | ⬜ | ⬜ | Physical mail delivery |
| OpenAI | ⬜ | ⬜ | ⬜ | Audio transcription |
| DeepSeek | ⬜ | ⬜ | ⬜ | AI statement refinement |
| Database | ⬜ | N/A | ⬜ | PostgreSQL |
| SSL | ⬜ | N/A | ⬜ | HTTPS certificate |
| DNS | ⬜ | N/A | ⬜ | Domain configuration |

**Legend:**
- ⬜ Not Started
- ⏳ In Progress  
- ✅ Complete
- ❌ Failed/Issues

---

## Contact Information

### Service Support

- **Stripe:** https://support.stripe.com
- **Lob:** https://support.lob.com
- **OpenAI:** https://help.openai.com
- **DeepSeek:** https://platform.deepseek.com/support
- **Hetzner:** https://docs.hetzner.com/cloud

### Emergency Procedures

1. **Service outage:** Check status pages first
2. **Payment issues:** Contact Stripe support immediately
3. **Mail delivery problems:** Contact Lob support
4. **Security incident:** Rotate all API keys immediately

---

**Document Version:** 1.0.0  
**Last Review Date:** 2025-01-09  
**Next Review Date:** 2025-02-09  
**Owner:** DevOps Team

---

*Keep this checklist updated as services are integrated and configurations change.*