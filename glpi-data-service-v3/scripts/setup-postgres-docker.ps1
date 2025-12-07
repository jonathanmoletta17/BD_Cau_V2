# Script PowerShell para configurar PostgreSQL para Docker
# EXECUTE COMO ADMINISTRADOR

$PG_VERSION = "15"
$PG_DATA = "C:\Program Files\PostgreSQL\$PG_VERSION\data"
$PG_HBA = "$PG_DATA\pg_hba.conf"
$PG_CONF = "$PG_DATA\postgresql.conf"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Docker Configuration Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se está rodando como Admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ ERRO: Execute este script como Administrador!" -ForegroundColor Red
    Write-Host "   Botão direito no PowerShell -> 'Executar como Administrador'" -ForegroundColor Yellow
    exit 1
}

# 2. Verificar se pg_hba.conf existe
if (-not (Test-Path $PG_HBA)) {
    Write-Host "❌ ERRO: Arquivo não encontrado: $PG_HBA" -ForegroundColor Red
    Write-Host "   Edite a variável `$PG_VERSION no topo do script." -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Arquivo encontrado: $PG_HBA" -ForegroundColor Green

# 3. Fazer backup
$backupFile = "$PG_HBA.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item $PG_HBA $backupFile
Write-Host "✓ Backup criado: $backupFile" -ForegroundColor Green

# 4. Verificar se já está configurado
$content = Get-Content $PG_HBA -Raw
if ($content -match "172\.16\.0\.0/12") {
    Write-Host "⚠️  Configuração Docker já existe no pg_hba.conf" -ForegroundColor Yellow
    Write-Host "   Pulando modificação..." -ForegroundColor Yellow
} else {
    # Adicionar configuração Docker
    $dockerConfig = @"

# Docker network access (added by setup script)
host    all             all             172.16.0.0/12           md5
host    all             all             192.168.0.0/16          md5
"@

    # Inserir antes de "# IPv4 local connections:"
    $newContent = $content -replace "(# IPv4 local connections:)", "$dockerConfig`n`$1"
    
    Set-Content -Path $PG_HBA -Value $newContent -Force
    Write-Host "✓ pg_hba.conf atualizado" -ForegroundColor Green
}

# 5. Verificar postgresql.conf
Write-Host ""
Write-Host "Verificando postgresql.conf..." -ForegroundColor Yellow

$pgConfContent = Get-Content $PG_CONF -Raw
if ($pgConfContent -match "listen_addresses\s*=\s*'\*'") {
    Write-Host "✓ listen_addresses já está configurado para '*'" -ForegroundColor Green
} elseif ($pgConfContent -match "#listen_addresses\s*=\s*'localhost'") {
    # Descomentar e mudar para *
    $newPgConf = $pgConfContent -replace "#listen_addresses\s*=\s*'localhost'", "listen_addresses = '*'"
    Set-Content -Path $PG_CONF -Value $newPgConf -Force
    Write-Host "✓ postgresql.conf atualizado (listen_addresses = '*')" -ForegroundColor Green
} else {
    Write-Host "⚠️  Não foi possível detectar a configuração de listen_addresses" -ForegroundColor Yellow
    Write-Host "   Verifique manualmente: $PG_CONF" -ForegroundColor Yellow
}

# 6. Reiniciar PostgreSQL
Write-Host ""
Write-Host "Reiniciando PostgreSQL..." -ForegroundColor Yellow

$serviceName = "postgresql-x64-$PG_VERSION"
try {
    Restart-Service $serviceName -Force
    Start-Sleep -Seconds 3
    
    $service = Get-Service $serviceName
    if ($service.Status -eq "Running") {
        Write-Host "✓ PostgreSQL reiniciado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "❌ PostgreSQL não está rodando. Status: $($service.Status)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Erro ao reiniciar PostgreSQL: $_" -ForegroundColor Red
    Write-Host "   Reinicie manualmente via services.msc" -ForegroundColor Yellow
}

# 7. Validar
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuração concluída!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:"
Write-Host "1. Teste a conexão Docker:"
Write-Host "   docker-compose up -d"
Write-Host "   docker-compose exec glpi-service python -c 'from src.core import Database; print(Database.get_session(\"dtic\"))'"
Write-Host ""
Write-Host "2. Se houver erro, verifique os logs:"
Write-Host "   docker-compose logs glpi-service"
Write-Host ""
Write-Host "3. Rollback (se necessário):"
Write-Host "   Copy-Item '$backupFile' '$PG_HBA' -Force"
Write-Host "   Restart-Service $serviceName"
Write-Host ""
