# Quick deploy script for Windows
# PowerShell version

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "GLPI Data Service V3 - Deploy" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "❌ Arquivo .env não encontrado!" -ForegroundColor Red
    Write-Host "   Copie .env.example para .env e configure."
    exit 1
}

# Build image
Write-Host ""
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker-compose build

# Start services
Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for health check
Write-Host ""
Write-Host "⏳ Waiting for service to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check status
Write-Host ""
docker-compose ps

# Show logs
Write-Host ""
Write-Host "📋 Recent logs:" -ForegroundColor Yellow
docker-compose logs --tail=20

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ Deploy completed!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Comandos úteis:"
Write-Host "  docker-compose logs -f      # Ver logs"
Write-Host "  docker-compose ps           # Status"
Write-Host "  docker-compose down         # Parar"
Write-Host ""
