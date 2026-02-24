# 🎯 Complete Stripe Setup Guide for FightCityTickets

## Overview

This guide walks you through creating a Stripe account, configuring products, setting up webhooks, and storing credentials securely.

## ⚠️ Important: I Cannot Create the Account For You

Stripe account creation requires:
- Email verification
- Business information
- Identity verification (ID upload)
- Bank account details
- Real-time verification

**You must complete these steps manually**, but I'll guide you through everything.

## 📋 Step-by-Step Setup

### Step 1: Create Stripe Account

1. **Go to:** https://dashboard.stripe.com/register
2. **Enter:**
   - Email address (use your business email)
   - Create a password
   - Business name: "FightCityTickets" or your legal name
   - Country: United States
3. **Verify email** (check your inbox)
4. **Complete business information:**
   - Business type: Individual/Sole Proprietor or Business
   - Business address
   - Tax ID (EIN or SSN for sole proprietor)
   - Phone number

### Step 2: Activate Account

1. **Add Bank Account:**
   - Go to: Settings → Bank accounts and scheduling
   - Add your business bank account
   - Wait for verification (2-3 business days)

2. **Complete Identity Verification:**
   - Upload government-issued ID
   - May require additional documents
   - Usually approved within 24-48 hours

3. **Activate Account:**
   - Go to: Settings → Account → Activate account
   - Complete all required fields
   - Submit for review

### Step 3: Get API Keys

1. **Go to:** Developers → API keys
2. **Copy these keys:**
   - **Secret Key:** `sk_live_...` (click "Reveal test key" if needed, but use LIVE)
   - **Publishable Key:** `pk_live_...`
3. ⚠️ **IMPORTANT:** Use **LIVE** keys (not test keys) for production

### Step 4: Create Product & Price

**Create "Certified Mail" Product:**

1. **Go to:** Products → Add product
2. **Product Details:**
   - Name: `Certified Mail Appeal Service`
   - Description: `Parking ticket appeal with certified mail delivery via Lob`
3. **Pricing:**
   - Price: `$19.89`
   - Billing: `One-time`
   - Currency: `USD`
4. **Save** and copy the **Price ID** (starts with `price_...`)

**Note:** This is your `STRIPE_PRICE_CERTIFIED` value.

### Step 5: Set Up Webhook Endpoint

**CRITICAL - Required for payment processing:**

1. **Go to:** Developers → Webhooks → Add endpoint
2. **Endpoint URL:** 
   ```
   https://fightcitytickets.com/api/webhook/stripe
   ```
   (Use your actual domain - update after deployment)
3. **Events to listen for:**
   - ✅ `checkout.session.completed` (REQUIRED)
   - Optional: `payment_intent.succeeded`
   - Optional: `payment_intent.payment_failed`
4. **Click "Add endpoint"**
5. **Copy the Signing Secret:**
   - Click on your new webhook endpoint
   - Copy the "Signing secret" (starts with `whsec_...`)
   - This is your `STRIPE_WEBHOOK_SECRET`

### Step 6: Store Credentials

**Run the credential storage script:**

```bash
cd /home/evan/Documents/FightCityTickets
python3 scripts/store_stripe_credentials.py
```

This will:
- Prompt for all credentials
- Validate format
- Store in ProtonPass JSON format
- Update your `.env` file automatically
- Create a backup

**To import into ProtonPass:**
1. Open ProtonPass
2. Go to: Settings → Import
3. Select: "Generic CSV" or "JSON"
4. Upload: `/home/evan/Documents/ProtonPass/stripe_credentials.json`

## 📋 Credentials Checklist

After completing setup, verify you have:

- [ ] `STRIPE_SECRET_KEY` = `sk_live_...` (not sk_test_)
- [ ] `STRIPE_PUBLISHABLE_KEY` = `pk_live_...` (not pk_test_)
- [ ] `STRIPE_WEBHOOK_SECRET` = `whsec_...`
- [ ] `STRIPE_PRICE_CERTIFIED` = `price_...`
- [ ] Bank account added and verified
- [ ] Account activated (can accept payments)

## 🧪 Testing

**Test Stripe Connection:**
```bash
python3 scripts/stripe_setup.py
```

**Test Webhook (after deployment):**
1. Go to: Dashboard → Developers → Webhooks
2. Click on your endpoint
3. Click "Send test webhook"
4. Select: `checkout.session.completed`
5. Check your server logs for webhook receipt

## ⚠️ Important Notes

### Test Mode vs Live Mode

- **Test Keys:** Start with `sk_test_` and `pk_test_`
  - Use for development/testing
  - No real charges
  
- **Live Keys:** Start with `sk_live_` and `pk_live_`
  - Use for production
  - Real charges processed
  - **Required for production deployment**

### Webhook Security

- Webhook secret is critical for security
- Never commit webhook secret to git
- Webhook endpoint must be HTTPS in production
- Stripe will verify webhook signature

### Account Activation

- Payments won't process until account is activated
- Activation requires:
  - Bank account verification (2-3 days)
  - Identity verification (1-2 days)
  - Business information completion

### Payout Schedule

- Default: 2-day rolling payouts
- Can be changed in: Settings → Payouts
- First payout may take longer

## 🔗 Useful Links

- **Stripe Dashboard:** https://dashboard.stripe.com
- **API Documentation:** https://stripe.com/docs/api
- **Webhook Testing:** https://dashboard.stripe.com/test/webhooks
- **Support:** https://support.stripe.com
- **Pricing:** https://stripe.com/pricing (2.9% + 30¢ per transaction)

## 🆘 Troubleshooting

**Account not activated:**
- Check: Settings → Account → Activation status
- Complete missing information
- Verify bank account

**Webhook not receiving events:**
- Verify endpoint URL is correct
- Check SSL certificate is valid
- Verify webhook secret matches
- Check server logs for errors

**API keys not working:**
- Verify you're using LIVE keys (not test)
- Check key hasn't been revoked
- Ensure account is activated

## 📝 Quick Reference

**Where to find things in Stripe Dashboard:**

| Item | Location |
|------|----------|
| API Keys | Developers → API keys |
| Webhooks | Developers → Webhooks |
| Products | Products → [Your Product] |
| Price IDs | Products → [Product] → Pricing → Price ID |
| Webhook Secret | Developers → Webhooks → [Endpoint] → Signing secret |
| Account Status | Settings → Account → Activation |
| Bank Account | Settings → Bank accounts and scheduling |
