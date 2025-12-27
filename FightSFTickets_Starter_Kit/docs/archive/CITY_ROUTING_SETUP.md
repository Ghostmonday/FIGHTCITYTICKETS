# City Routing Setup - FightCityTickets.com

## ✅ Completed Implementation

### 1. City Slug Routing
- **Uppercase slugs**: `/SF`, `/SD`, `/NYC`, `/LA`, `/SJ`, `/CHI`, `/SEA`, `/PHX`, `/DEN`, `/DAL`, `/HOU`, `/PHI`, `/LV`, `/PDX`, `/SLC`, `/DC`
- **City mapping**: Created `frontend/app/lib/city-routing.ts` with complete city slug mappings
- **Dynamic routes**: Updated `frontend/app/[city]/page.tsx` to handle uppercase slugs

### 2. Geolocation Auto-Redirect
- **IP-based detection**: Uses ipapi.co to detect user location
- **Auto-redirect**: Redirects to appropriate city page after 2 seconds
- **User control**: Users can skip redirect by manually selecting a city
- **Visual feedback**: Shows detected city notification on homepage

### 3. Domain Configuration
- **Domain**: FightCityTickets.com
- **Environment variables**: Updated `.env` template with production domain
- **Deployment script**: Updated `scripts/deploy_hetzner.sh` default domain

## City Routes Available

| Slug | City | URL |
|------|------|-----|
| SF | San Francisco | `/SF` |
| SD | San Diego | `/SD` |
| NYC | New York City | `/NYC` |
| LA | Los Angeles | `/LA` |
| SJ | San Jose | `/SJ` |
| CHI | Chicago | `/CHI` |
| SEA | Seattle | `/SEA` |
| PHX | Phoenix | `/PHX` |
| DEN | Denver | `/DEN` |
| DAL | Dallas | `/DAL` |
| HOU | Houston | `/HOU` |
| PHI | Philadelphia | `/PHI` |
| LV | Las Vegas | `/LV` |
| PDX | Portland | `/PDX` |
| SLC | Salt Lake City | `/SLC` |
| DC | Washington DC | `/DC` |

## How It Works

1. **Homepage (`/`)**: 
   - Detects user location via IP geolocation
   - Shows notification if city detected
   - Auto-redirects to city page after 2 seconds
   - Users can manually select city or enter citation

2. **City Pages (`/SF`, `/SD`, etc.)**:
   - City-specific landing page
   - Citation validation form
   - City-specific information and requirements
   - Links to other cities

3. **Citation Validation**:
   - Validates citation format for detected city
   - Routes to appeal flow with city context
   - Maintains city context throughout appeal process

## Deployment

To deploy with city routing:

```bash
# Set domain
export DOMAIN="fightcitytickets.com"

# Deploy
./scripts/deploy_hetzner.sh

# Configure DNS
# Point fightcitytickets.com to server IP

# Set up SSL
certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com
```

## Testing

After deployment, test:
- `https://fightcitytickets.com` - Should auto-detect and redirect
- `https://fightcitytickets.com/SF` - San Francisco page
- `https://fightcitytickets.com/SD` - San Diego page
- `https://fightcitytickets.com/NYC` - New York City page

## Files Modified

1. `frontend/app/lib/city-routing.ts` - City slug mapping and geolocation utilities
2. `frontend/app/page.tsx` - Added geolocation detection and redirect
3. `frontend/app/[city]/page.tsx` - Updated to handle uppercase slugs
4. `scripts/deploy_hetzner.sh` - Updated default domain
5. `.env` - Added domain configuration

## Next Steps

1. Deploy to production server
2. Configure DNS for fightcitytickets.com
3. Set up SSL certificates
4. Test geolocation redirects from different locations
5. Monitor city routing analytics

