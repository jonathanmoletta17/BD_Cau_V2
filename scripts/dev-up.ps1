# Smart Dev Startup Script with Port Conflict Detection
# Usage:
#   .\dev-up.ps1          -> Fast startup, no rebuild (default)
#   .\dev-up.ps1 -Rebuild -> Force rebuild (use when dependencies change)
#   .\dev-up.ps1 -Force   -> Skip port conflict check

param(
    [switch]$Rebuild,
    [switch]$Force
)

# CRITICAL: Check for port conflicts FIRST
function Test-PortConflicts {
    $requiredPorts = @(3000, 3001, 3003, 3004, 3005, 8000, 5432, 5050)
    $conflicts = @()
    
    foreach ($port in $requiredPorts) {
        try {
            $listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
            
            if ($listeners) {
                foreach ($listener in $listeners) {
                    $proc = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
                    # Only flag non-Docker processes as conflicts
                    if ($proc -and $proc.ProcessName -ne "com.docker.backend" -and $proc.ProcessName -ne "Docker Desktop") {
                        $conflicts += [PSCustomObject]@{
                            Port    = $port
                            PID     = $listener.OwningProcess
                            Process = $proc.ProcessName
                            Started = $proc.StartTime
                        }
                    }
                }
            }
        }
        catch {
            # Ignore errors checking ports
        }
    }
    
    return $conflicts
}

$buildFlag = if ($Rebuild) { "--build" } else { "" }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " GLPI Dev Environment - Pre-flight Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check for conflicts unless -Force is used
if (-not $Force) {
    Write-Host "Checking for port conflicts..." -ForegroundColor Cyan
    $conflicts = Test-PortConflicts
    
    if ($conflicts.Count -gt 0) {
        Write-Host ""
        Write-Host "WARNING: Port conflicts detected!" -ForegroundColor Red
        Write-Host ""
        Write-Host "The following processes are using ports needed by Docker:" -ForegroundColor Yellow
        Write-Host ""
        $conflicts | Format-Table -Property Port, PID, Process, @{Label = "Started"; Expression = { $_.Started.ToString("dd/MM HH:mm") } } -AutoSize
        Write-Host ""
        Write-Host "These processes may cause:" -ForegroundColor Yellow
        Write-Host "  - Random behavior (browser accessing wrong version)" -ForegroundColor Gray
        Write-Host "  - Code changes not appearing" -ForegroundColor Gray
        Write-Host "  - Apps showing before containers start" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Recommended actions:" -ForegroundColor White
        Write-Host "  1. Run: .\scripts\cleanup-ports.ps1  (kills conflicting processes)" -ForegroundColor Green
        Write-Host "  2. Restart Docker Desktop  (cleans wslrelay cache)" -ForegroundColor Green
        Write-Host "  3. Use -Force flag to continue anyway  (NOT recommended)" -ForegroundColor Gray
        Write-Host ""
        
        $answer = Read-Host "Continue anyway? (y/N)"
        if ($answer -ne "y" -and $answer -ne "Y") {
            Write-Host ""
            Write-Host "Aborted. Please resolve port conflicts first." -ForegroundColor Red
            Write-Host "   Run: .\scripts\cleanup-ports.ps1" -ForegroundColor Cyan
            exit 1
        }
        Write-Host ""
        Write-Host "Continuing with port conflicts (may cause issues)..." -ForegroundColor Yellow
    }
    else {
        Write-Host "No port conflicts detected" -ForegroundColor Green
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Starting All GLPI Services (DEV MODE)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($Rebuild) {
    Write-Host "REBUILD MODE: Rebuilding all images..." -ForegroundColor Yellow
}
else {
    Write-Host "FAST MODE: Starting without rebuild (hot-reload enabled)" -ForegroundColor Green
}
Write-Host ""

Write-Host "[1/6] Starting GLPI Data Service - PostgreSQL + Backend API (Dev)..." -ForegroundColor Yellow
Set-Location glpi-data-service
if ($buildFlag) {
    docker-compose -f docker-compose.dev.yml up -d --build
}
else {
    docker-compose -f docker-compose.dev.yml up -d
}
Set-Location ..
Write-Host "[OK] GLPI Data Service started" -ForegroundColor Green
Write-Host ""

Write-Host "[2/6] Starting DTIC Dashboard (Dev)..." -ForegroundColor Yellow
Set-Location 06-dtic-dashboard
if ($buildFlag) {
    docker-compose -f docker-compose.dev.yml up -d --build
}
else {
    docker-compose -f docker-compose.dev.yml up -d
}
Set-Location ..
Write-Host "[OK] DTIC Dashboard started" -ForegroundColor Green
Write-Host ""

Write-Host "[3/6] Starting SIS Dashboard (Dev)..." -ForegroundColor Yellow
Set-Location 06.1-sis-dashboard
if ($buildFlag) {
    docker-compose -f docker-compose.dev.yml up -d --build
}
else {
    docker-compose -f docker-compose.dev.yml up -d
}
Set-Location ..
Write-Host "[OK] SIS Dashboard started" -ForegroundColor Green
Write-Host ""

Write-Host "[4/6] Starting SIS Carregadores Dashboard (Dev)..." -ForegroundColor Yellow
Set-Location 06.1.1-sis-carregadores-dashboard
if ($buildFlag) {
    docker-compose -f docker-compose.dev.yml up -d --build
}
else {
    docker-compose -f docker-compose.dev.yml up -d
}
Set-Location ..
Write-Host "[OK] SIS Carregadores Dashboard started" -ForegroundColor Green
Write-Host ""

Write-Host "[5/6] Starting DTIC Smart Search - GLPI (Dev)..." -ForegroundColor Yellow
Set-Location glpi-smart-search
if ($buildFlag) {
    docker-compose -f docker-compose.dev.yml up -d --build
}
else {
    docker-compose -f docker-compose.dev.yml up -d
}
Set-Location ..
Write-Host "[OK] DTIC Smart Search started" -ForegroundColor Green
Write-Host ""

Write-Host "[6/6] Starting SIS Smart Search - Maintenance (Dev)..." -ForegroundColor Yellow
Set-Location sis-smart-search
if ($buildFlag) {
    docker-compose -f docker-compose.dev.yml up -d --build
}
else {
    docker-compose -f docker-compose.dev.yml up -d
}
Set-Location ..
Write-Host "[OK] SIS Smart Search started" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " All Dev Services Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs (Dev):" -ForegroundColor White
Write-Host "  - GLPI Data Service API:        http://localhost:8000" -ForegroundColor Gray
Write-Host "  - DTIC Dashboard:               http://localhost:3000" -ForegroundColor Gray
Write-Host "  - SIS Dashboard:                http://localhost:3001" -ForegroundColor Gray
Write-Host "  - SIS Carregadores Dashboard:   http://localhost:3005" -ForegroundColor Gray
Write-Host "  - DTIC Smart Search:            http://localhost:3003" -ForegroundColor Gray
Write-Host "  - SIS Smart Search:             http://localhost:3004" -ForegroundColor Gray
Write-Host ""
if (-not $Rebuild) {
    Write-Host "Tip: Use '.\dev-up.ps1 -Rebuild' to force rebuild when dependencies change" -ForegroundColor Cyan
}
