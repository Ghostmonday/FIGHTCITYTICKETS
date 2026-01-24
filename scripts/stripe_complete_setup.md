# 🎯 Complete Stripe Account Setup Guide

## Step-by-Step Stripe Account Creation

### 1. Create Stripe Account

**Go to:** https://dashboard.stripe.com/register

**Required Information:**
- Email address (use your business email)
- Business name: "FightCityTickets" or your legal business name
- Business type: Individual/Sole Proprietor or Business
- Country: United States
- Business address
- Tax ID (EIN or SSN for sole proprietor)

**After Registration:**
- Verify your email
- Complete identity verification (may require ID upload)
- Add bank account for payouts (takes 2-3 business days)

### 2. Activate Account

**In Stripe Dashboard:**
1. Go to: Settings → Account → Activate account
2. Complete business information
3. Add bank account details
4. Wait for verification (usually 1-2 days)

### 3. Get API Keys

**In Stripe Dashboard:**
1. Go to: Developers → API keys
2. **Secret Key:** Copy `sk_live_...` (starts with sk_live_)
3. **Publishable Key:** Copy `pk_live_...` (starts with pk_live_)
4. ⚠️ **IMPORTANT:** Use LIVE keys, not test keys for production

### 4. Create Products & Prices

**Create "Certified Mail" Product:**

1. Go to: Products → Add product
2. Name: "Certified Mail Appeal Service"
3. Description: "Parking ticket appeal with certified mail delivery"
4. Pricing:
   - Price: $19.89
   - Billing: One-time
   - Currency: USD
5. Save and copy the **Price ID** (starts with `price_`)

**Note:** Standard Mail product is archived, only Certified Mail is active.

### 5. Set Up Webhook Endpoint

**CRITICAL for payment processing:**

1. Go to: Developers → Webhooks → Add endpoint
2. Endpoint URL: `https://fightcitytickets.com/api/webhook/stripe`
3. **Events to listen for:**
   - `checkout.session.completed` ✅ (REQUIRED)
   - `payment_intent.succeeded` (optional)
   - `payment_intent.payment_failed` (optional)
4. Click "Add endpoint"
5. **Copy the Signing Secret** (starts with `whsec_`)
   - This is your `STRIPE_WEBHOOK_SECRET`

### 6. Store Credentials

After completing setup, run:
```bash
python3 /home/evan/Documents/FightCityTickets/scripts/store_stripe_credentials.py
```

This will:
- Prompt for all Stripe credentials
- Store them in ProtonPass format
- Update your `.env` file
- Create a backup file

## 📋 Credentials Checklist

After setup, you should have:

- [ ] `STRIPE_SECRET_KEY` = `sk_live_...`
- [ ] `STRIPE_PUBLISHABLE_KEY` = `pk_live_...`
- [ ] `STRIPE_WEBHOOK_SECRET` = `whsec_...`
- [ ] `STRIPE_PRICE_CERTIFIED` = `price_...`
- [ ] Bank account added and verified
- [ ] Account activated

## ⚠️ Important Notes

1. **Test Mode vs Live Mode:**
   - Test keys start with `sk_test_` and `pk_test_`
   - Live keys start with `sk_live_` and `pk_live_`
   - **Use LIVE keys for production**

2. **Webhook Security:**
   - Webhook secret is critical for security
   - Never share or commit webhook secret
   - Webhook endpoint must be HTTPS in production

3. **Account Activation:**
   - Payments won't process until account is activated
   - Activation requires bank account verification
   - May take 1-3 business days

4. **Payout Schedule:**
   - Default: 2-day rolling payouts
   - Can be changed in Settings → Payouts

## 🔗 Useful Links

- Stripe Dashboard: https://dashboard.stripe.com
- API Documentation: https://stripe.com/docs/api
- Webhook Testing: https://dashboard.stripe.com/test/webhooks
- Support: https://support.stripe.com
