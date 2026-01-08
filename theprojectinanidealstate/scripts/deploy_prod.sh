#!/bin/bash
set -e

# FightSFTickets Production Deployment Script

echo "🚀 Starting deployment process..."

# 1. Pull latest changes
echo "📥 Pulling latest changes from git..."
git pull origin main

# 2. Build Frontend
echo "🏗️  Building Next.js frontend..."
cd frontend
npm ci --legacy-peer-deps
npm run build
cd ..

# 3. Database Migrations
echo "🗄️  Applying database migrations..."
# Assuming we can run alembic via docker or locally if installed
# If running via docker:
docker-compose run --rm backend alembic upgrade head
# Or if local:
# cd backend && alembic upgrade head && cd ..

# 4. Restart Containers
echo "🔄 Restarting Docker containers..."
docker-compose down
docker-compose up -d --build --force-recreate

echo "✅ Deployment complete!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
