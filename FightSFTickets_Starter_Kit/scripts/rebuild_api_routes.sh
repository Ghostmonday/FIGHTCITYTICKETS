#!/bin/bash
# Rebuild API container with fixed routes
# Run on server: bash scripts/rebuild_api_routes.sh

set -e

echo "🔧 Rebuilding API container with fixed routes..."
cd /var/www/fightsftickets

echo "Stopping API container..."
docker-compose stop api

echo "Building API container..."
docker-compose build --no-cache api

echo "Starting API container..."
docker-compose up -d api

echo "Waiting for API to start..."
sleep 15

echo "Testing endpoints..."
echo ""
echo "Testing /api/statement/refine:"
curl -s http://localhost:8000/statement/refine -X POST \
  -H "Content-Type: application/json" \
  -d '{"original_statement":"test","citation_type":"parking","desired_tone":"professional","max_length":500}' \
  | head -5 || echo "Endpoint test failed"

echo ""
echo "Testing /api/webhook/health:"
curl -s http://localhost:8000/webhook/health | head -5 || echo "Endpoint test failed"

echo ""
echo "✅ API container rebuilt and restarted"
echo "Check logs: docker-compose logs api --tail=50"

