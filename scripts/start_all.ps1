Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Starting All GLPI Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/6] Starting GLPI Data Service - PostgreSQL + Backend API..." -ForegroundColor Yellow
Set-Location glpi-data-service
docker-compose up -d --build
Set-Location ..
Write-Host "[OK] GLPI Data Service started" -ForegroundColor Green
Write-Host ""

Write-Host "[2/6] Starting DTIC Dashboard..." -ForegroundColor Yellow
Set-Location 06-dtic-dashboard
docker-compose up -d --build
Set-Location ..
Write-Host "[OK] DTIC Dashboard started" -ForegroundColor Green
Write-Host ""

Write-Host "[3/6] Starting SIS Dashboard..." -ForegroundColor Yellow
Set-Location 06.1-sis-dashboard
docker-compose up -d --build
Set-Location ..
Write-Host "[OK] SIS Dashboard started" -ForegroundColor Green
Write-Host ""

Write-Host "[4/6] Starting SIS Carregadores Dashboard..." -ForegroundColor Yellow
Set-Location 06.1.1-sis-carregadores-dashboard
docker-compose up -d --build
Set-Location ..
Write-Host "[OK] SIS Carregadores Dashboard started" -ForegroundColor Green
Write-Host ""

Write-Host "[5/6] Starting DTIC Smart Search - GLPI..." -ForegroundColor Yellow
Set-Location glpi-smart-search
docker-compose up -d --build
Set-Location ..
Write-Host "[OK] DTIC Smart Search started" -ForegroundColor Green
Write-Host ""

Write-Host "[6/6] Starting SIS Smart Search - Maintenance..." -ForegroundColor Yellow
Set-Location sis-smart-search
docker-compose up -d --build
Set-Location ..
Write-Host "[OK] SIS Smart Search started" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " All Services Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor White
Write-Host "  - GLPI Data Service API:        http://localhost:8000" -ForegroundColor Gray
Write-Host "  - DTIC Dashboard:               http://localhost:3000" -ForegroundColor Gray
Write-Host "  - SIS Dashboard:                http://localhost:3001" -ForegroundColor Gray
Write-Host "  - SIS Carregadores Dashboard:   http://localhost:3005" -ForegroundColor Gray
Write-Host "  - DTIC Smart Search:            http://localhost:3003" -ForegroundColor Gray
Write-Host "  - SIS Smart Search:             http://localhost:3004" -ForegroundColor Gray
Write-Host ""

