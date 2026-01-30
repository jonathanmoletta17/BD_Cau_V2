#!/bin/bash
# Quick deploy script for GLPI Data Service V3

set -e

echo "=========================================="
echo "GLPI Data Service V3 - Deploy"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "   Copie .env.example para .env e configure."
    exit 1
fi

# Build image
echo ""
echo "🔨 Building Docker image..."
docker-compose build

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Wait for health check
echo ""
echo "⏳ Waiting for service to be healthy..."
sleep 5

# Check status
echo ""
docker-compose ps

# Show logs
echo ""
echo "📋 Recent logs:"
docker-compose logs --tail=20

echo ""
echo "=========================================="
echo "✅ Deploy completed!"
echo "=========================================="
echo ""
echo "API: http://localhost:8000/docs"
echo ""
echo "Comandos úteis:"
echo "  docker-compose logs -f      # Ver logs"
echo "  docker-compose ps           # Status"
echo "  docker-compose down         # Parar"
echo ""
