#!/bin/bash

echo "🔍 Checking TherapyBot Deployment Status..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run 'make setup' first."
    exit 1
fi

# Check if GCP credentials exist
if [ ! -f secrets/gcp-credentials.json ]; then
    echo "⚠️  GCP credentials not found at secrets/gcp-credentials.json"
    echo "   Follow instructions in secrets/README.md to set up Vertex AI"
fi

# Check Docker services
echo "📦 Checking Docker services..."
docker compose ps

echo ""
echo "🏥 Health Checks:"

# Backend health
echo -n "Backend: "
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Frontend health
echo -n "Frontend: "
if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Database health
echo -n "Database: "
if docker compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Redis health
echo -n "Redis: "
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

echo ""
echo "🌐 Access URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Health Check: http://localhost:8000/health"

echo ""
echo "📊 Service Logs (last 10 lines):"
echo "Backend:"
docker compose logs --tail=10 backend
echo ""
echo "Frontend:"
docker compose logs --tail=10 frontend