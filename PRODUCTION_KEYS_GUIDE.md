# 🔄 Switching from Test to Production API Keys

## Overview
Your application is currently configured with **TEST** keys for Stripe and Lob. When you're ready to go live, you'll need to switch to **PRODUCTION** keys.

## ⚠️ Important Notes

1. **Test keys are safe** - They don't process real payments or send real mail
2. **Production keys are live** - They process real payments and send real mail
3. **Never mix test and live keys** - Always use matching pairs
4. **Update both local `.env` and server `.env`** - Keep them in sync

## 📅 Timeline

- **Lob Production Keys**: Can be obtained today (no bank account needed)
- **Stripe Production Keys**: Wait until bank account is connected (estimated: Monday)
- **You can switch Lob to production independently** - It doesn't require Stripe to be live

---

## 📍 Where to Update Keys

### 1. **Local Development** (Your Computer)
File: `/home/evan/Documents/FightCityTickets/.env`

### 2. **Production Server** (Kamatera)
File: `/var/www/fightcitytickets/.env` on server `199.244.50.152`

---

## 🚀 Quick Start: Switch Lob to Production Today

**You can switch Lob to production keys immediately** (no bank account needed):

1. **Get Lob Live Keys**:
   - Go to: https://dashboard.lob.com/settings/api-keys
   - Copy your **Live API Key** (`live_...`)
   - Copy your **Live Publishable Key** (`live_pub_...`)

2. **Update Server `.env`**:
   ```bash
   ssh root@199.244.50.152
   cd /var/www/fightcitytickets
   nano .env
   ```
   
   Change these lines:
   ```env
   # From:
   LOB_API_KEY=test_xxxxxxxxxxxx
   LOB_PUBLISHABLE_KEY=test_pub_xxxxxxxx
   LOB_MODE=test
   
   # To:
   LOB_API_KEY=live_YOUR_LIVE_KEY_HERE
   LOB_PUBLISHABLE_KEY=live_pub_YOUR_LIVE_PUBLISHABLE_KEY_HERE
   LOB_MODE=live
   ```

3. **Also update** `NEXT_PUBLIC_LOB_PUBLISHABLE_KEY`:
   ```env
   NEXT_PUBLIC_LOB_PUBLISHABLE_KEY=live_pub_YOUR_LIVE_PUBLISHABLE_KEY_HERE
   ```

4. **Restart Services**:
   ```bash
   docker-compose restart api web
   ```

5. **Verify**: Check Lob dashboard - mail should now be sent for real!

**Note**: Stripe will remain in test mode until bank account is connected (Monday).

---

## 🔑 Step-by-Step: Switching to Production Keys (Full Guide)

### **Step 1: Get Your Production Keys**

#### Stripe Production Keys:
1. Go to: https://dashboard.stripe.com/apikeys
2. **Toggle to "Live mode"** (top right)
3. Copy your **Secret key** (starts with `sk_live_...`)
4. Copy your **Publishable key** (starts with `pk_live_...`)
5. Create a webhook endpoint and copy the **Webhook secret** (starts with `whsec_...`)
6. Get your **Live Price IDs** from Products → Your Products → Live Mode

#### Lob Production Keys:
1. Go to: https://dashboard.lob.com/settings/api-keys
2. **Toggle to "Live mode"** (if available, or use the live keys section)
3. Copy your **Live API Key** (starts with `live_...`)
4. Copy your **Live Publishable Key** (starts with `live_pub_...`)
5. **Note**: Lob production keys can be obtained immediately - no bank account connection needed!

---

### **Step 2: Update Local `.env` File**

1. Open `/home/evan/Documents/FightCityTickets/.env`
2. **Comment out** the TEST keys section (lines 37-47):
   ```env
   # ⚠️  TEST KEYS (Currently Active) ⚠️
   # STRIPE_SECRET_KEY=sk_test_...
   # STRIPE_PUBLISHABLE_KEY=pk_test_...
   # ... etc
   ```

3. **Uncomment and fill in** the LIVE keys section (lines 49-57):
   ```env
   # 🔴 LIVE KEYS (For Production - NOW ACTIVE)
   STRIPE_SECRET_KEY=sk_live_YOUR_ACTUAL_LIVE_KEY
   STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_ACTUAL_LIVE_KEY
   STRIPE_WEBHOOK_SECRET=whsec_YOUR_ACTUAL_WEBHOOK_SECRET
   STRIPE_PRICE_CERTIFIED=price_YOUR_LIVE_PRICE_ID
   ```

4. **Do the same for Lob** (lines 62-72):
   ```env
   # 🔴 LIVE KEYS (For Production - NOW ACTIVE)
   LOB_API_KEY=live_YOUR_ACTUAL_LIVE_KEY
   LOB_PUBLISHABLE_KEY=live_pub_YOUR_ACTUAL_LIVE_KEY
   LOB_MODE=live
   ```

5. **Update the mode indicator** at the top (line 8):
   ```env
   # =============================================
   # ⚠️  CURRENT MODE: PRODUCTION ⚠️
   # =============================================
   ```

6. **Update APP_ENV** (line 19):
   ```env
   APP_ENV=production
   ```

---

### **Step 3: Update Production Server `.env`**

**Option A: SSH and Edit Directly**
```bash
ssh root@199.244.50.152
cd /var/www/fightcitytickets
nano .env
# Make the same changes as above
# Save and exit (Ctrl+X, Y, Enter)
```

**Option B: Copy Updated File from Local**
```bash
# After updating your local .env file:
scp /home/evan/Documents/FightCityTickets/.env root@199.244.50.152:/var/www/fightcitytickets/.env
```

**⚠️ IMPORTANT:** Make sure to update the server URLs in the production `.env`:
```env
APP_URL=http://199.244.50.152
FRONTEND_URL=http://199.244.50.152
API_URL=http://199.244.50.152/api
NEXT_PUBLIC_API_BASE=http://199.244.50.152/api
```

---

### **Step 4: Restart Services**

After updating the `.env` file on the server:

```bash
ssh root@199.244.50.152
cd /var/www/fightcitytickets
docker-compose restart api web
# Or rebuild if needed:
docker-compose up -d --build
```

---

### **Step 5: Verify Production Mode**

1. **Check Stripe Dashboard** - Toggle to "Live mode" and verify test charges don't appear
2. **Check Lob Dashboard** - Verify mail is being sent (not test mode)
3. **Test a small transaction** - Use a real card with a small amount to verify

---

## 🔐 Security Checklist

- [ ] Test keys are commented out or removed
- [ ] Live keys are active and correct
- [ ] Webhook endpoints are configured for production
- [ ] Price IDs match your live Stripe products
- [ ] `APP_ENV=production` is set
- [ ] Both local and server `.env` files are updated
- [ ] Services have been restarted
- [ ] Test transaction completed successfully

---

## 🆘 Rollback Plan

If something goes wrong, you can quickly rollback:

1. **Comment out** the LIVE keys
2. **Uncomment** the TEST keys
3. **Set** `APP_ENV=dev` or `APP_ENV=test`
4. **Restart** services: `docker-compose restart api web`

---

## 📝 Notes

- **DeepSeek API Key**: Same key works for both test and production (no separate keys)
- **Google Places API**: Same key works for both (just monitor usage/costs)
- **Database**: Production database is separate from test data
- **Webhooks**: Make sure to create new webhook endpoints for production URLs

---

## 🎯 Quick Reference

| Service | Test Key Prefix | Live Key Prefix | Where to Get |
|---------|----------------|-----------------|--------------|
| Stripe Secret | `sk_test_` | `sk_live_` | dashboard.stripe.com/apikeys |
| Stripe Publishable | `pk_test_` | `pk_live_` | dashboard.stripe.com/apikeys |
| Stripe Webhook | `whsec_` | `whsec_` | dashboard.stripe.com/webhooks |
| Lob API | `test_` | `live_` | dashboard.lob.com/settings/api-keys |
| Lob Publishable | `test_pub_` | `live_pub_` | dashboard.lob.com/settings/api-keys |

---

**Last Updated:** January 2026
**Current Status:** Using TEST keys ✅
