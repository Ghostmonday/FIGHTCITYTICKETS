# Setting Up Your Domain

## Quick Setup

To use your domain instead of localhost, set these environment variables:

### For Development (Local)
Create or update `.env` file in the project root:

```bash
# Your Domain Configuration
APP_URL=http://localhost:3000
API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE=http://localhost:8000
CORS_ORIGINS=http://localhost:3000
```

### For Production (Your Domain)
```bash
# Replace 'provethat.io' with your actual domain
APP_URL=https://provethat.io
API_URL=https://provethat.io/api
NEXT_PUBLIC_API_BASE=https://provethat.io/api
CORS_ORIGINS=https://provethat.io,https://www.provethat.io
```

## Steps to Configure

1. **Set your domain in `.env`**:
   ```bash
   APP_URL=https://yourdomain.com
   API_URL=https://yourdomain.com/api
   NEXT_PUBLIC_API_BASE=https://yourdomain.com/api
   ```

2. **Restart services**:
   ```bash
   # If using Docker
   docker-compose down
   docker-compose up -d
   
   # If running manually
   # Stop and restart backend and frontend
   ```

3. **Update DNS** to point your domain to your server IP

4. **Set up SSL** (for production):
   ```bash
   certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

## Current Configuration

- **Backend**: Reads from `APP_URL` and `API_URL` environment variables
- **Frontend**: Reads from `NEXT_PUBLIC_API_BASE` environment variable
- **CORS**: Configured via `CORS_ORIGINS` environment variable

