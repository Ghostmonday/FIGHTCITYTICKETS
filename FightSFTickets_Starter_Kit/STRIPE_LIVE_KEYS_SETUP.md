# Stripe Live Keys Setup

## ⚠️ IMPORTANT: Production Configuration

The codebase has been updated to use **live Stripe keys by default**. You MUST set your production Stripe keys in the `.env` file.

## Required Environment Variables

Add these to your `.env` file:

```bash
# Stripe Live Keys (REQUIRED for production)
STRIPE_SECRET_KEY=sk_live_YOUR_LIVE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_LIVE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET

# Stripe Live Price IDs (REQUIRED for production)
# Get these from: https://dashboard.stripe.com/products
STRIPE_PRICE_STANDARD=price_YOUR_STANDARD_PRICE_ID
STRIPE_PRICE_CERTIFIED=price_YOUR_CERTIFIED_PRICE_ID
```

## How to Get Live Stripe Keys

1. **Log into Stripe Dashboard**: https://dashboard.stripe.com
2. **Switch to Live Mode** (toggle in top right)
3. **Get API Keys**:
   - Go to: https://dashboard.stripe.com/apikeys
   - Copy **Publishable key** (starts with `pk_live_`)
   - Copy **Secret key** (starts with `sk_live_`) - click "Reveal"

4. **Get Webhook Secret**:
   - Go to: https://dashboard.stripe.com/webhooks
   - Create webhook endpoint: `https://fightcitytickets.com/api/webhook/stripe`
   - Copy **Signing secret** (starts with `whsec_`)

5. **Get Price IDs**:
   - Go to: https://dashboard.stripe.com/products
   - Create products for Standard ($9.89) and Certified ($19.89) appeals
   - Copy the **Price ID** for each (starts with `price_`)

## Security Notes

- ✅ **Never commit** `.env` file to git (already in .gitignore)
- ✅ **Never share** live keys publicly
- ✅ **Rotate keys** if accidentally exposed
- ✅ **Use test keys** for development/testing

## Verification

After setting live keys, verify:
```bash
# Check config loads correctly
python -c "from backend.src.config import settings; print('Stripe mode:', 'LIVE' if settings.stripe_secret_key.startswith('sk_live_') else 'TEST')"
```

## Testing

Before going live:
1. Test with Stripe test keys first
2. Use Stripe test cards: https://stripe.com/docs/testing
3. Verify webhook endpoint works
4. Then switch to live keys


