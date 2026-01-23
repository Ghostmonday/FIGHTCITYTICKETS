#!/bin/bash
# Quick restart script for FightSFTickets

set -e

echo "🛑 Stopping containers..."
docker-compose down

echo "🔨 Rebuilding containers..."
docker-compose build --no-cache

echo "🚀 Starting containers..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "📊 Container status:"
docker-compose ps

echo ""
echo "🔍 Testing endpoints..."
echo "Health check:"
curl -s http://localhost/health || echo "❌ Health check failed"

echo ""
echo "Frontend:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost/ || echo "❌ Frontend failed"

echo ""
echo "✅ Done! Site should be available at:"
echo "   - http://localhost (via nginx)"
echo "   - http://localhost:3000 (direct Next.js)"
echo ""
echo "📋 View logs with: docker-compose logs -f"
