# Port Cleanup Utility
# Kills processes that are using ports needed by Docker development environment

param([switch]$Force)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Port Conflict Cleanup Utility" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ports = @(3000, 3001, 3003, 3004, 3005, 8000, 5432, 5050)

Write-Host "🔍 Scanning for port conflicts..." -ForegroundColor Cyan
Write-Host ""

$conflicts = @()
foreach ($port in $ports) {
    try {
        $listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        
        foreach ($listener in $listeners) {
            $proc = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
            # Only target non-Docker processes that might conflict
            if ($proc -and ($proc.ProcessName -match "node|wslrelay|python" -or $proc.ProcessName -eq "Code")) {
                $existing = $conflicts | Where-Object { $_.PID -eq $listener.OwningProcess }
                if (-not $existing) {
                    $conflicts += [PSCustomObject]@{
                        Port    = $port
                        PID     = $listener.OwningProcess
                        Process = $proc.ProcessName
                        Path    = $proc.Path
                        Started = $proc.StartTime
                    }
                }
            }
        }
    }
    catch {
        # Ignore errors
    }
}

if ($conflicts.Count -eq 0) {
    Write-Host "✅ No port conflicts found!" -ForegroundColor Green
    Write-Host ""
    Write-Host "All development ports are clear. You can safely run:" -ForegroundColor White
    Write-Host "  .\scripts\dev-up.ps1" -ForegroundColor Cyan
    exit 0
}

Write-Host "⚠️  Found $($conflicts.Count) process(es) using development ports:" -ForegroundColor Yellow
Write-Host ""
$conflicts | Format-Table -Property Port, PID, Process, @{Label = "Started"; Expression = { $_.Started.ToString("dd/MM HH:mm") } } -AutoSize
Write-Host ""

if (-not $Force) {
    Write-Host "These processes will be terminated:" -ForegroundColor Yellow
    Write-Host ""
    $conflicts | ForEach-Object {
        Write-Host "  • PID $($_.PID) - $($_.Process)" -ForegroundColor Gray
    }
    Write-Host ""
    
    $answer = Read-Host "Kill these processes? (y/N)"
    if ($answer -ne "y" -and $answer -ne "Y") {
        Write-Host ""
        Write-Host "Cancelled." -ForegroundColor Gray
        exit 0
    }
}

Write-Host ""
Write-Host "🔨 Terminating conflicting processes..." -ForegroundColor Yellow
Write-Host ""

$killed = 0
$failed = 0

foreach ($conflict in $conflicts) {
    try {
        Stop-Process -Id $conflict.PID -Force -ErrorAction Stop
        Write-Host "✅ Killed $($conflict.Process) (PID $($conflict.PID)) on port $($conflict.Port)" -ForegroundColor Green
        $killed++
    }
    catch {
        Write-Host "❌ Failed to kill PID $($conflict.PID): $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($failed -eq 0) {
    Write-Host " Cleanup Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ Killed $killed process(es)" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run:" -ForegroundColor White
    Write-Host "  .\scripts\dev-up.ps1" -ForegroundColor Cyan
}
else {
    Write-Host " Cleanup Completed with Errors" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ Killed: $killed" -ForegroundColor Green
    Write-Host "❌ Failed: $failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "You may need to manually kill failed processes or restart Docker Desktop." -ForegroundColor Yellow
}
