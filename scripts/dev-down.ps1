Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Stopping All GLPI Services (DEV MODE)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/6] Stopping SIS Smart Search..." -ForegroundColor Yellow
Set-Location sis-smart-search
docker-compose -f docker-compose.dev.yml down
Set-Location ..
Write-Host "[OK] SIS Smart Search stopped" -ForegroundColor Green
Write-Host ""

Write-Host "[2/6] Stopping DTIC Smart Search - GLPI..." -ForegroundColor Yellow
Set-Location glpi-smart-search
docker-compose -f docker-compose.dev.yml down
Set-Location ..
Write-Host "[OK] DTIC Smart Search stopped" -ForegroundColor Green
Write-Host ""

Write-Host "[3/6] Stopping SIS Carregadores Dashboard..." -ForegroundColor Yellow
Set-Location 06.1.1-sis-carregadores-dashboard
docker-compose -f docker-compose.dev.yml down
Set-Location ..
Write-Host "[OK] SIS Carregadores Dashboard stopped" -ForegroundColor Green
Write-Host ""

Write-Host "[4/6] Stopping SIS Dashboard..." -ForegroundColor Yellow
Set-Location 06.1-sis-dashboard
docker-compose -f docker-compose.dev.yml down
Set-Location ..
Write-Host "[OK] SIS Dashboard stopped" -ForegroundColor Green
Write-Host ""

Write-Host "[5/6] Stopping DTIC Dashboard..." -ForegroundColor Yellow
Set-Location 06-dtic-dashboard
docker-compose -f docker-compose.dev.yml down
Set-Location ..
Write-Host "[OK] DTIC Dashboard stopped" -ForegroundColor Green
Write-Host ""

Write-Host "[6/6] Stopping GLPI Data Service - PostgreSQL + Backend API..." -ForegroundColor Yellow
Set-Location glpi-data-service
docker-compose -f docker-compose.dev.yml down
Set-Location ..
Write-Host "[OK] GLPI Data Service stopped" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " All Dev Services Stopped Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
