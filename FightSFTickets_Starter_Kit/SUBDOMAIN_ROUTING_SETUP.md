# Subdomain Routing Setup - Complete! ✅

## What's Configured

### 1. DNS Configuration ✅
- **Wildcard DNS** configured for:
  - `*.fightsftickets.com` → `178.156.215.100`
  - `*.fightcitytickets.city` → `178.156.215.100`

### 2. Next.js Middleware ✅
- Created `frontend/middleware.ts`
- Detects subdomains and rewrites to city routes
- Handles: `sf.fightcitytickets.com` → `/SF` route

### 3. City Page Subdomain Detection ✅
- Updated `frontend/app/[city]/page.tsx`
- Client-side subdomain detection
- Falls back to URL path if no subdomain

## How It Works

### Subdomain Mapping
| Subdomain | City | Full URL |
|-----------|------|----------|
| `sf` | San Francisco | `sf.fightsftickets.com` |
| `sd` | San Diego | `sd.fightsftickets.com` |
| `nyc` | New York City | `nyc.fightsftickets.com` |
| `la` | Los Angeles | `la.fightsftickets.com` |
| `sj` | San Jose | `sj.fightsftickets.com` |
| `chi` | Chicago | `chi.fightsftickets.com` |
| `sea` | Seattle | `sea.fightsftickets.com` |
| `phx` | Phoenix | `phx.fightsftickets.com` |
| `den` | Denver | `den.fightsftickets.com` |
| `dal` | Dallas | `dal.fightsftickets.com` |
| `hou` | Houston | `hou.fightsftickets.com` |
| `phi` | Philadelphia | `phi.fightsftickets.com` |
| `lv` | Las Vegas | `lv.fightsftickets.com` |
| `pdx` | Portland | `pdx.fightsftickets.com` |
| `slc` | Salt Lake City | `slc.fightsftickets.com` |
| `dc` | Washington DC | `dc.fightsftickets.com` |

### Alternative Names
- `sanfrancisco` → `SF`
- `sandiego` → `SD`
- `newyork` → `NYC`
- `losangeles` → `LA`
- `chicago` → `CHI`
- etc.

## Testing

### Local Testing (with hosts file)
Add to `/etc/hosts` (Mac/Linux) or `C:\Windows\System32\drivers\etc\hosts` (Windows):
```
127.0.0.1 sf.localhost
127.0.0.1 nyc.localhost
127.0.0.1 sd.localhost
```

Then visit:
- `http://sf.localhost:3000`
- `http://nyc.localhost:3000`

### Production Testing
After DNS propagates (5-30 minutes):
- `https://sf.fightsftickets.com`
- `https://nyc.fightsftickets.com`
- `https://sd.fightsftickets.com`

## How Middleware Works

1. **Request comes in** with hostname `sf.fightsftickets.com`
2. **Middleware extracts** subdomain: `sf`
3. **Maps to city slug**: `SF`
4. **Rewrites URL** to `/SF` (if on root `/`)
5. **City page renders** with San Francisco content

## Files Modified

1. ✅ `frontend/middleware.ts` - Subdomain detection and routing
2. ✅ `frontend/app/[city]/page.tsx` - Client-side subdomain detection
3. ✅ `frontend/next.config.js` - Next.js config updated
4. ✅ DNS configured via `scripts/configure_subdomain_dns.py`

## Next Steps

1. **Wait for DNS propagation** (5-30 minutes)
2. **Deploy code** to production server
3. **Configure Nginx** to handle subdomains (if needed)
4. **Test subdomains** after deployment

## Nginx Configuration (if needed)

If your server needs Nginx config for subdomains:

```nginx
server {
    listen 80;
    server_name *.fightsftickets.com *.fightcitytickets.city;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Status

✅ **DNS Configured** - Wildcard subdomains point to server  
✅ **Middleware Created** - Detects and routes subdomains  
✅ **City Page Updated** - Handles subdomain detection  
✅ **Ready for Deployment** - Code is complete


