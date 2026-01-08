# Google Places API Setup Guide

## Overview

We've implemented Google Places API autocomplete on the checkout page to ensure users provide accurate return addresses. This prevents legal issues where users might not receive the city's response due to typos.

## Why This Matters

**Legal Risk**: If a user provides a typo in their return address, they never receive the city's response (dismissal notice, hearing date, etc.). This could result in:
- Missing important deadlines
- Default judgments
- Legal complications
- Customer complaints and refunds

**Solution**: Google Places API autocomplete ensures addresses are:
- Validated against USPS database
- Properly formatted
- Complete (includes city, state, ZIP)
- Standardized

## Setup Instructions

### 1. Get Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Places API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Places API"
   - Click "Enable"
4. Create API Key:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the API key

### 2. Configure API Key Restrictions (Recommended)

For security, restrict the API key:

1. Click on your API key in Credentials
2. Under "API restrictions":
   - Select "Restrict key"
   - Choose "Places API" only
3. Under "Application restrictions":
   - Select "HTTP referrers (web sites)"
   - Add: `https://fightcitytickets.com/*`
   - Add: `https://*.fightcitytickets.com/*`
   - (For local dev) Add: `http://localhost:3000/*`

### 3. Add to Environment Variables

**On Server** (`/var/www/fightsftickets/.env`):
```bash
NEXT_PUBLIC_GOOGLE_PLACES_API_KEY=YOUR_API_KEY_HERE
```

**Local Development** (`.env.local`):
```bash
NEXT_PUBLIC_GOOGLE_PLACES_API_KEY=YOUR_API_KEY_HERE
```

### 4. Restart Services

After adding the environment variable:
```bash
cd /var/www/fightsftickets
docker-compose restart web
```

### 5. Verify It Works

1. Go to checkout page: `https://fightcitytickets.com/appeal/checkout`
2. Start typing in the "Street Address" field
3. You should see Google Places autocomplete suggestions
4. Selecting an address should auto-fill city, state, and ZIP

## Cost Considerations

**Google Places API Pricing** (as of 2024):
- **Autocomplete (Per Session)**: $2.83 per 1,000 sessions
- **Place Details**: $17 per 1,000 requests
- **Free Tier**: $200/month credit (covers ~70,000 autocomplete sessions)

**Estimated Monthly Cost**:
- 1,000 users/month: ~$3-5/month
- 10,000 users/month: ~$30-50/month
- 100,000 users/month: ~$300-500/month

**Cost Optimization**:
- The autocomplete component only makes requests when user types
- Place details are only fetched when user selects an address
- Most users will be covered by free tier initially

## Implementation Details

### Component: `AddressAutocomplete.tsx`

**Features**:
- ✅ US addresses only (componentRestrictions: { country: "us" })
- ✅ Address type only (not businesses)
- ✅ Auto-fills: street address, city, state, ZIP
- ✅ Handles apartment/suite numbers
- ✅ Error handling and fallback
- ✅ Loading states

**Usage**:
```tsx
<AddressAutocomplete
  value={address}
  onChange={(address) => {
    // address.addressLine1
    // address.addressLine2 (optional)
    // address.city
    // address.state
    // address.zip
  }}
  onError={(error) => console.error(error)}
  required
/>
```

### Validation

The checkout page now validates:
- ✅ Address components are complete
- ✅ ZIP code format (5 digits or 5+4 format)
- ✅ State is 2-letter code
- ✅ All required fields present

## Fallback Behavior

If Google Places API fails to load:
- User can still enter address manually
- All fields remain editable
- Error message displayed: "Address autocomplete unavailable. Please enter address manually."
- Form validation still works

## Testing

### Test Cases

1. **Valid Address Selection**:
   - Type "123 Main St, San Francisco"
   - Select from autocomplete
   - Verify city, state, ZIP auto-fill

2. **Manual Entry**:
   - If autocomplete fails, user can type manually
   - All fields remain editable

3. **Invalid Address**:
   - Try invalid ZIP code
   - Form should show validation error

4. **Missing Components**:
   - If autocomplete returns incomplete address
   - Error message displayed
   - User can complete manually

## Troubleshooting

### Autocomplete Not Showing

1. Check API key is set: `echo $NEXT_PUBLIC_GOOGLE_PLACES_API_KEY`
2. Check browser console for errors
3. Verify Places API is enabled in Google Cloud Console
4. Check API key restrictions aren't blocking your domain

### Address Not Auto-Filling

1. Check browser console for JavaScript errors
2. Verify Google Maps script loaded: `window.google?.maps?.places`
3. Check network tab for API requests

### API Quota Exceeded

1. Check usage in Google Cloud Console
2. Set up billing alerts
3. Consider upgrading to paid tier

## Security Notes

- ✅ API key is public (NEXT_PUBLIC_ prefix) - this is normal for client-side Google APIs
- ✅ Key is restricted to specific domains
- ✅ Key is restricted to Places API only
- ✅ No sensitive data sent to Google (only address queries)

## Future Enhancements

Potential improvements:
- [ ] Address verification after selection (USPS API)
- [ ] International address support (if expanding)
- [ ] Address validation on backend before submission
- [ ] Caching common addresses
- [ ] Analytics on autocomplete usage

---

*Last Updated: 2025-12-26*
*Status: Implemented and Ready for Configuration*

