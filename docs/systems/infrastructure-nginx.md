# Infrastructure & Nginx

Purpose: document reverse proxy, SSL, and routing between frontend and backend.

## Responsibilities
- Terminate HTTP/HTTPS, route requests to web (Next.js) and api (FastAPI).
- Serve static assets and maintenance page when needed.
- Enforce admin IP allowlists if configured.

## Key files
- `nginx/nginx.conf` — base config.
- `nginx/conf.d/` — site configs:
  - `fightcitytickets.conf` — main routing.
  - `fightcitytickets.conf.production.disabled` — production variant.
  - `local.conf` — local dev example.
  - `admin_ips.conf` — allowlist snippet.
- `nginx/html/maintenance.html` — maintenance page.
- `nginx/html/api-fallback.json` — API fallback response.

## Routing (typical)
- `/:` to frontend container on port 3000.
- `/api` or specific prefixes proxied to backend on port 8000.
- Static assets cached with long max-age; HTML not cached.

## SSL
- Typically managed via certbot/Let’s Encrypt in deploy scripts; ensure `setup-ssl.sh` aligns with nginx server blocks.

## Rebuild checklist
- Mirror upstream/locations from `fightcitytickets.conf`; keep health routes proxied to api.
- Include gzip and security headers consistent with existing config.
- Provide maintenance mode switch by swapping server block to `maintenance.html`.
