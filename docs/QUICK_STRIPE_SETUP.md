# ⚡ Quick Stripe Setup

## 🎯 What You Need to Do

I **cannot** create the Stripe account for you (requires email verification, ID upload, bank account), but I'll guide you through everything and help store the credentials.

## 📋 5-Minute Setup Process

### 1. Create Account (5 minutes)
- Go to: https://dashboard.stripe.com/register
- Enter email, password, business info
- Verify email

### 2. Get API Keys (1 minute)
- Dashboard → Developers → API keys
- Copy: `sk_live_...` and `pk_live_...`

### 3. Create Product (2 minutes)
- Products → Add product
- Name: "Certified Mail Appeal Service"
- Price: $19.89
- Copy Price ID: `price_...`

### 4. Set Up Webhook (2 minutes)
- Developers → Webhooks → Add endpoint
- URL: `https://fightcitytickets.com/api/webhook/stripe`
- Event: `checkout.session.completed`
- Copy Secret: `whsec_...`

### 5. Store Credentials (1 minute)
```bash
cd /home/evan/Documents/FightCityTickets
python3 scripts/store_stripe_credentials.py
```

This script will:
- ✅ Prompt for all credentials
- ✅ Validate format
- ✅ Save to ProtonPass JSON format
- ✅ Update your .env file
- ✅ Create backup

### 6. Import to ProtonPass
1. Open ProtonPass app
2. Settings → Import
3. Select: "Generic CSV" or "JSON"
4. Upload: `/home/evan/Documents/ProtonPass/stripe_credentials.json`

## 📝 What You'll Need

Before running the script, have ready:
- Stripe Secret Key (`sk_live_...`)
- Stripe Publishable Key (`pk_live_...`)
- Webhook Secret (`whsec_...`)
- Certified Mail Price ID (`price_...`)
- Account email (optional)

## 🚀 After Setup

Test your configuration:
```bash
python3 scripts/stripe_setup.py
```

## 📚 Full Guide

See `STRIPE_SETUP_GUIDE.md` for detailed instructions.
