# Deploy FightCityTickets.com

## Domain Configuration

Set these environment variables for production deployment:

```bash
# Domain Configuration
DOMAIN=fightcitytickets.com
APP_URL=https://fightcitytickets.com
API_URL=https://fightcitytickets.com/api
NEXT_PUBLIC_API_BASE=https://fightcitytickets.com/api
CORS_ORIGINS=https://fightcitytickets.com,https://www.fightcitytickets.com
```

## City Routing

The application now supports city-based routing with uppercase slugs:

- `/SF` - San Francisco
- `/SD` - San Diego  
- `/NYC` - New York City
- `/LA` - Los Angeles
- `/SJ` - San Jose
- `/CHI` - Chicago
- `/SEA` - Seattle
- `/PHX` - Phoenix
- `/DEN` - Denver
- `/DAL` - Dallas
- `/HOU` - Houston
- `/PHI` - Philadelphia
- `/LV` - Las Vegas
- `/PDX` - Portland
- `/SLC` - Salt Lake City
- `/DC` - Washington DC

## Geolocation Auto-Redirect

The homepage automatically detects user location and redirects to the appropriate city page:
- Uses IP geolocation API (ipapi.co)
- Redirects after 2 seconds if city detected
- Users can skip redirect by selecting a city manually

## Deployment Steps

1. **Set environment variables**:
   ```bash
   export DOMAIN="fightcitytickets.com"
   export APP_URL="https://fightcitytickets.com"
   export API_URL="https://fightcitytickets.com/api"
   export NEXT_PUBLIC_API_BASE="https://fightcitytickets.com/api"
   ```

2. **Update .env file** with production values

3. **Deploy using existing scripts**:
   ```bash
   ./scripts/deploy_hetzner.sh
   ```

4. **Configure DNS** to point fightcitytickets.com to your server IP

5. **Set up SSL**:
   ```bash
   certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com
   ```

## Testing City Routes

After deployment, test:
- https://fightcitytickets.com/SF
- https://fightcitytickets.com/SD
- https://fightcitytickets.com/NYC
- https://fightcitytickets.com (should auto-detect and redirect)

