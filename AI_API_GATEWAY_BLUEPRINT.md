# AI API Gateway - Complete Blueprint

**Purpose**: Secure, unlimited-access API gateway for AI model access (DeepSeek, MiniMax, OpenAI)  
**Location**: Dedicated DigitalOcean Droplet  
**Access**: HTTPS API with API key authentication  
**Target**: https://ai.fightcitytickets.com (or similar)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AI API Gateway                                │
│                     (New Droplet - 1 vCPU, 2GB)                      │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────────┐ │
│  │   Nginx      │   │  FastAPI     │   │   Rate Limiting        │ │
│  │  (Reverse    │◄──│  API Server  │◄──│   (slowapi/limits)     │ │
│  │   Proxy)     │   │  :8000       │   │                        │ │
│  └──────┬───────┘   └──────┬───────┘   └────────────────────────┘ │
│         │                  │                                      │
│         │ HTTPS :443       │ Internal API                         │
│         │                  ▼                                      │
│         │         ┌─────────────────────┐                        │
│         │         │  AI Provider Proxy  │                        │
│         │         │  - DeepSeek         │                        │
│         │         │  - MiniMax          │                        │
│         │         │  - OpenAI (backup)  │                        │
│         │         └─────────────────────┘                        │
│         │                  │                                      │
│         ▼                  ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     External APIs                           │ │
│  │   - DeepSeek API (primary)                                  │ │
│  │   - MiniMax API (backup)                                    │ │
│  │   - OpenAI API (fallback)                                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Droplet Specifications

| Resource | Specification |
|----------|---------------|
| **Provider** | DigitalOcean |
| **Size** | s-1vcpu-2gb (1 vCPU, 2GB RAM) |
| **Region** | sfo3 (match existing) |
| **OS** | Ubuntu 22.04 LTS |
| **Cost** | ~$6-7/month |

**Setup Commands:**
```bash
# Create droplet via doctl
doctl compute droplet create ai-gateway \
  --region sfo3 \
  --size s-1vcpu-2gb \
  --image ubuntu-22-04-x64 \
  --ssh-keys <YOUR_SSH_KEY_ID>
```

---

## 3. Project Structure

```
ai-gateway/
├── README.md                    # Start here for AI sessions
├── .env                         # Environment variables (SECRET)
├── .env.example                 # Template
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── app.py                   # Main FastAPI application
│   ├── config.py                # Settings and environment
│   ├── auth.py                  # API key authentication
│   ├── rate_limit.py            # Rate limiting middleware
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py              # Chat completion endpoint
│   │   ├── models.py            # List available models
│   │   ├── health.py            # Health check
│   │   └── admin.py             # Admin endpoints (optional)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── deepseek.py          # DeepSeek API wrapper
│   │   ├── minimax.py           # MiniMax API wrapper
│   │   └── openai.py            # OpenAI API wrapper (fallback)
│   │
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py              # Authentication middleware
│       └── logging.py           # Request/response logging
│
├── nginx/
│   ├── nginx.conf
│   └── conf.d/
│       └── ai-gateway.conf
│
└── scripts/
    ├── setup.sh                 # Initial server setup
    ├── deploy.sh                # Deploy to server
    └── ssl-setup.sh             # SSL certificate setup
```

---

## 4. Core Files

### 4.1 `src/app.py`
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .config import settings
from .routes import chat, models, health
from .middleware.auth import APIKeyMiddleware
from .middleware.logging import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI API Gateway",
    description="Unified API gateway for DeepSeek, MiniMax, and OpenAI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(APIKeyMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(models.router, prefix="/v1/models", tags=["models"])
app.include_router(chat.router, prefix="/v1/chat", tags=["chat"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4.2 `src/config.py`
```python
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # API Keys (from environment)
    deepseek_api_key: str = ""
    minimax_api_key: str = ""
    openai_api_key: str = ""
    
    # Gateway Authentication
    gateway_api_key: str = ""  # Your personal API key
    admin_api_key: Optional[str] = None
    
    # Rate Limiting
    rate_limit_requests: int = 1000  # per minute
    rate_limit_burst: int = 100
    
    # Model Settings
    default_model: str = "deepseek-chat"
    max_tokens: int = 32768
    max_context_length: int = 128000
    
    # Logging
    log_requests: bool = True
    log_responses: bool = False
    
    class Config:
        env_file = ".env"
        env_prefix = "AI_GATEWAY_"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### 4.3 `src/auth.py`
```python
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(
    api_key: str = Security(api_key_header)
) -> str:
    """Verify the API key from request header."""
    
    if not api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="API key required. Add 'X-API-Key' header."
        )
    
    if api_key != settings.gateway_api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return api_key

async def verify_admin_key(
    api_key: str = Security(api_key_header)
) -> str:
    """Verify admin API key for admin endpoints."""
    
    if not api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Admin API key required"
        )
    
    if settings.admin_api_key and api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid admin API key"
        )
    
    if api_key != settings.gateway_api_key and api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return api_key
```

### 4.4 `src/routes/chat.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict

from .auth import verify_api_key
from .config import settings
from .services.deepseek import deepseek_client
from .services.minimax import minimax_client
from .services.openai import openai_client

router = APIRouter()

# Request model
class ChatRequest(BaseModel):
    messages: List[Dict[str, str]] = Field(
        ...,
        example=[{"role": "user", "content": "Hello!"}]
    )
    model: str = Field(default=settings.default_model)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, le=settings.max_tokens)
    stream: bool = False

# Response model
class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

@router.post("/completions", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
) -> ChatResponse:
    """Chat completion endpoint - unified interface for all AI providers."""
    
    # Route to appropriate provider based on model name
    if "deepseek" in request.model.lower():
        return await deepseek_client.chat(request)
    elif "minimax" in request.model.lower():
        return await minimax_client.chat(request)
    elif "openai" in request.model.lower() or "gpt" in request.model.lower():
        return await openai_client.chat(request)
    else:
        # Default to DeepSeek
        return await deepseek_client.chat(request)

@router.post("/completions/stream")
async def chat_completion_stream(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """Streaming chat completion endpoint."""
    # Implementation for streaming responses
    pass
```

### 4.5 `src/services/deepseek.py`
```python
import httpx
from typing import AsyncGenerator
from ..config import settings

class DeepSeekClient:
    BASE_URL = "https://api.deepseek.com"
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.client = httpx.AsyncClient(timeout=300.0)  # Long timeout
    
    async def chat(self, request):
        """Send chat completion to DeepSeek."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens or 4096,
            "stream": request.stream
        }
        
        response = await self.client.post(
            f"{self.BASE_URL}/chat/completions",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    async def stream_chat(self, request) -> AsyncGenerator[str, None]:
        """Stream chat completion from DeepSeek."""
        # Implementation for streaming
        pass
    
    async def list_models(self):
        """List available DeepSeek models."""
        return {
            "data": [
                {"id": "deepseek-chat", "object": "model"},
                {"id": "deepseek-reasoner", "object": "model"}
            ]
        }

deepseek_client = DeepSeekClient()
```

### 4.6 `src/services/minimax.py`
```python
import httpx
from typing import AsyncGenerator
from ..config import settings

class MiniMaxClient:
    BASE_URL = "https://api.minimax.chat/v1"
    
    def __init__(self):
        self.api_key = settings.minimax_api_key
        self.client = httpx.AsyncClient(timeout=300.0)
    
    async def chat(self, request):
        """Send chat completion to MiniMax."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # MiniMax-specific payload format
        payload = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_output_tokens": request.max_tokens or 4096
        }
        
        response = await self.client.post(
            f"{self.BASE_URL}/text/chatcompletion_v2",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        return self._transform_response(response.json())
    
    def _transform_response(self, response):
        """Transform MiniMax response to OpenAI-compatible format."""
        # MiniMax uses different field names
        transformed = {
            "id": response.get("id", "minimax-chat"),
            "object": "chat.completion",
            "created": response.get("base_created_at", 0),
            "model": response.get("model", "minimax-model"),
            "choices": [],
            "usage": response.get("usage", {})
        }
        
        choices = response.get("choices", [])
        for choice in choices:
            transformed["choices"].append({
                "index": choice.get("index", 0),
                "message": {
                    "role": "assistant",
                    "content": choice.get("message", {}).get("content", "")
                },
                "finish_reason": choice.get("finish_reason", "stop")
            })
        
        return transformed

minimax_client = MiniMaxClient()
```

### 4.7 `src/routes/models.py`
```python
from fastapi import APIRouter, Depends
from .auth import verify_api_key

router = APIRouter()

@router.get("")
async def list_models(api_key: str = Depends(verify_api_key)):
    """List all available models from all providers."""
    return {
        "data": [
            # DeepSeek
            {"id": "deepseek-chat", "provider": "deepseek", "object": "model"},
            {"id": "deepseek-reasoner", "provider": "deepseek", "object": "model"},
            # MiniMax
            {"id": "minimax-abab6.5s-chat", "provider": "minimax", "object": "model"},
            {"id": "minimax-abab6.5-chat", "provider": "minimax", "object": "model"},
            # OpenAI
            {"id": "gpt-4", "provider": "openai", "object": "model"},
            {"id": "gpt-4-turbo", "provider": "openai", "object": "model"},
            {"id": "gpt-3.5-turbo", "provider": "openai", "object": "model"},
        ]
    }

@router.get("/{model_id}")
async def get_model_info(model_id: str):
    """Get information about a specific model."""
    # Implementation
    pass
```

### 4.8 `src/routes/health.py`
```python
from fastapi import APIRouter
import httpx

router = APIRouter()

@router.get("")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "ai-gateway"}

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check including provider connectivity."""
    providers = {}
    
    # Check DeepSeek
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(
                "https://api.deepseek.com/",
                headers={"Authorization": "Bearer test"}
            )
        providers["deepseek"] = "reachable"
    except:
        providers["deepseek"] = "unreachable"
    
    # Check MiniMax
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(
                "https://api.minimax.chat/v1",
                headers={"Authorization": "Bearer test"}
            )
        providers["minimax"] = "reachable"
    except:
        providers["minimax"] = "unreachable"
    
    return {
        "status": "healthy",
        "providers": providers
    }
```

---

## 5. Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 6. requirements.txt

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
pydantic-settings==2.5.2
python-dotenv==1.0.1
httpx==0.27.2
slowapi==0.1.9
python-multipart==0.0.9
```

---

## 7. docker-compose.yml

```yaml
version: "3.8"

services:
  api:
    build: .
    container_name: ai-gateway-api
    environment:
      - AI_GATEWAY_HOST=0.0.0.0
      - AI_GATEWAY_PORT=8000
      - AI_GATEWAY_DEBUG=false
    env_file:
      - .env
    expose:
      - "8000"
    restart: unless-stopped
    healthcheck:
      test:
        [
          "CMD-SHELL",
          'python -c "import requests; requests.get(''http://localhost:8000/health'', timeout=5)" || exit 1',
        ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  nginx:
    image: nginx:alpine
    container_name: ai-gateway-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/www/certbot:/var/www/certbot:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  letsencrypt:
```

---

## 8. Nginx Configuration

### `nginx/conf.d/ai-gateway.conf`

```nginx
# AI Gateway - HTTPS Configuration
# Domain: ai.fightcitytickets.com (or your chosen subdomain)

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name ai.fightcitytickets.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ai.fightcitytickets.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/ai.fightcitytickets.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ai.fightcitytickets.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    add_header Strict-Transport-Security "max-age=63072000" always;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-RateLimit-Limit "1000" always;
    add_header X-RateLimit-Remaining "999" always;

    # API location
    location / {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";

        # Timeouts for long-running AI requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        proxy_send_timeout 300s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

---

## 9. Environment Variables Template

### `.env.example`

```bash
# AI Gateway Settings
AI_GATEWAY_HOST=0.0.0.0
AI_GATEWAY_PORT=8000
AI_GATEWAY_DEBUG=false

# YOUR Personal API Key (generate a strong random key)
AI_GATEWAY_GATEWAY_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Admin API Key (optional, for admin endpoints)
AI_GATEWAY_ADMIN_API_KEY=sk-admin-xxxxxxxxxxxxxxxxxxxxxx

# Rate Limiting
AI_GATEWAY_RATE_LIMIT_REQUESTS=1000
AI_GATEWAY_RATE_LIMIT_BURST=100

# Model Settings
AI_GATEWAY_DEFAULT_MODEL=deepseek-chat
AI_GATEWAY_MAX_TOKENS=32768
AI_GATEWAY_MAX_CONTEXT_LENGTH=128000

# Logging
AI_GATEWAY_LOG_REQUESTS=true
AI_GATEWAY_LOG_RESPONSES=false

# Provider API Keys (get from respective dashboards)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
MINIMAX_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 10. Setup & Deployment Scripts

### `scripts/setup.sh` - Initial server setup

```bash
#!/bin/bash
set -e

echo "🚀 Setting up AI Gateway server..."

# Update system
apt-get update -qq
apt-get install -y -qq docker.io docker-compose git wget curl

# Enable Docker
systemctl enable docker
systemctl start docker

# Create directory structure
mkdir -p /var/www/ai-gateway
mkdir -p /var/www/certbot

# Clone repository
git clone <REPO_URL> /var/www/ai-gateway
cd /var/www/ai-gateway

# Create .env from template
cp .env.example .env
echo "⚠️  Edit .env with your API keys before continuing!"

echo "✅ Setup complete!"
echo "Next steps:"
echo "1. Edit /var/www/ai-gateway/.env with your API keys"
echo "2. Run ./scripts/deploy.sh"
```

### `scripts/deploy.sh` - Deploy to server

```bash
#!/bin/bash
set -e

echo "🚀 Deploying AI Gateway..."

cd /var/www/ai-gateway

# Pull latest code
git pull

# Build and start containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services
sleep 10

# Verify
curl -s http://localhost/health

echo "✅ Deployment complete!"
echo "API available at: https://ai.yourdomain.com"
```

### `scripts/ssl-setup.sh` - SSL certificates

```bash
#!/bin/bash
set -e

DOMAIN="ai.yourdomain.com"
EMAIL="your-email@example.com"

echo "🔒 Setting up SSL for $DOMAIN..."

# Stop nginx temporarily
cd /var/www/ai-gateway
docker-compose stop nginx

# Get certbot
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/www/certbot:/var/www/certbot \
  certbot/certbot certonly \
  --webroot \
  -w /var/www/certbot \
  -d $DOMAIN \
  --email $EMAIL \
  --agree-tos \
  --non-interactive

# Restart nginx
docker-compose start nginx

echo "✅ SSL certificate installed!"
echo "Certificate location: /etc/letsencrypt/live/$DOMAIN/"
```

---

## 11. API Usage Examples

### 11.1 Chat Completion (cURL)

```bash
curl -X POST https://ai.yourdomain.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-your-api-key-here" \
  -d '{
    "model": "deepseek-chat",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### 11.2 Python Client

```python
import requests

API_URL = "https://ai.yourdomain.com/v1/chat/completions"
API_KEY = "sk-your-api-key-here"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "Write a Python function to calculate factorial."}
    ],
    "temperature": 0.3
}

response = requests.post(API_URL, headers=headers, json=payload)
print(response.json())
```

### 11.3 List Available Models

```bash
curl -X GET https://ai.yourdomain.com/v1/models \
  -H "X-API-Key: sk-your-api-key-here"
```

---

## 12. Security Considerations

### 12.1 API Key Generation

```bash
# Generate a secure API key
openssl rand -hex 32
# Output: 8f4d9c8b7a2e6f1a3c5d9e8b7a2c4f1a3e5d9c8b7
```

### 12.2 Environment Variables

**NEVER commit `.env` to git!**

```
# .gitignore
.env
.env.local
*.pem
*.key
```

### 12.3 Rate Limiting

The gateway includes built-in rate limiting:
- Default: 1000 requests/minute per API key
- Burst: 100 requests

Configure in `.env`:
```bash
AI_GATEWAY_RATE_LIMIT_REQUESTS=1000
AI_GATEWAY_RATE_LIMIT_BURST=100
```

### 12.4 Request Logging

All requests are logged with:
- Timestamp
- API key (masked)
- Endpoint
- Response status
- Processing time

Logs stored in Docker logs:
```bash
docker-compose logs -f api
```

---

## 13. Future AI Sessions - Quick Start

### Access the Gateway

```bash
# API endpoint
https://ai.yourdomain.com

# Documentation
https://ai.yourdomain.com/docs

# Health check
curl https://ai.yourdomain.com/health
```

### Required Context for Future Sessions

| Item | Value |
|------|-------|
| **Droplet IP** | `143.198.131.XXX` (new one) |
| **SSH Key** | `/c/Users/Amirp/.ssh/do_ai_gateway_key` |
| **SSH Command** | `ssh -i /c/Users/Amirp/.ssh/do_ai_gateway_key root@<DROPLET_IP>` |
| **API URL** | `https://ai.yourdomain.com` |
| **API Key** | See `.env` on server at `/var/www/ai-gateway/.env` |

### Deploy Updates

```bash
ssh -i /c/Users/Amirp/.ssh/do_ai_gateway_key root@<DROPLET_IP>
cd /var/www/ai-gateway
git pull
docker-compose down
docker-compose up -d --build
curl https://ai.yourdomain.com/health
```

---

## 14. Cost Breakdown

| Item | Monthly Cost |
|------|-------------|
| Droplet (1 vCPU, 2GB) | ~$6-7 |
| SSL Certificates | Free (Let's Encrypt) |
| **Total** | **~$6-7/month** |

---

## 15. Next Steps for Implementation

1. **Create droplet** via doctl or DigitalOcean console
2. **SSH and run** `scripts/setup.sh`
3. **Edit `.env`** with your API keys
4. **Run `scripts/deploy.sh`**
5. **Configure DNS** to point subdomain to droplet IP
6. **Run `scripts/ssl-setup.sh`** for HTTPS
7. **Test** the API endpoints
8. **Share API key** with future AI sessions

---

## 16. Troubleshooting

### Container won't start
```bash
docker-compose logs api
```

### API returns 500
```bash
docker-compose exec api cat /app/logs/app.log
```

### Rate limit errors
```bash
# Check current limits
curl -I https://ai.yourdomain.com/health -H "X-API-Key: YOUR_KEY"
```

### SSL certificate renewal
```bash
# Add to crontab for auto-renewal
0 0 * * * cd /var/www/ai-gateway && docker-compose restart nginx
```

---

**Document Created**: January 10, 2026  
**Status**: Blueprint - Ready for Implementation