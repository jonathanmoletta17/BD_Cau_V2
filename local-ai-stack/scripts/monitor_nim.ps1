param(
  [int]$IntervalSeconds = 30,
  [int]$MaxMinutes = 30,
  [string]$ContainerName = "glpi-nim-llm"
)

$ErrorActionPreference = "Stop"

$scriptRoot = $PSScriptRoot
$projectRoot = Resolve-Path (Join-Path $scriptRoot "..\")
$logDir = Join-Path $scriptRoot "..\monitor_logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
$logDir = Resolve-Path $logDir

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$monitorLog = Join-Path $logDir ("monitor_" + $ts + ".log")

function Log($msg) {
  $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
  $line | Tee-Object -FilePath $monitorLog -Append
}

Log "Monitor iniciado. Intervalo=${IntervalSeconds}s, Timeout=${MaxMinutes}min, Container=${ContainerName}"

# Carrega NGC_API_KEY do .env (preferir local-ai-stack/.env, depois raiz)
$envLocal = Resolve-Path (Join-Path $scriptRoot "..\.env")
$envRoot  = Resolve-Path (Join-Path $projectRoot ".env")
$ngcKey = ""
if (Test-Path $envLocal) {
  $ngcKey = (Get-Content $envLocal | Select-String -Pattern '^NGC_API_KEY=' | ForEach-Object { $_.ToString().Split('=')[1] }).Trim()
  Log "NGC_API_KEY carregada de local-ai-stack/.env (len=$($ngcKey.Length))"
} elseif (Test-Path $envRoot) {
  $ngcKey = (Get-Content $envRoot  | Select-String -Pattern '^NGC_API_KEY=' | ForEach-Object { $_.ToString().Split('=')[1] }).Trim()
  Log "NGC_API_KEY carregada de raiz .env (len=$($ngcKey.Length))"
} else {
  Log "Arquivo .env não encontrado; OPENAI_API_KEY será omitido"
}

$deadline = (Get-Date).AddMinutes($MaxMinutes)
$lastStatus = ""

while ($true) {
  try {
    $status = docker inspect -f "{{.State.Health.Status}}" $ContainerName 2>$null
    if (-not $status) { $status = "unknown" }
  } catch {
    $status = "unknown"
  }

  if ($status -ne $lastStatus) {
    Log "Status alterado: '$lastStatus' -> '$status'"
    $lastStatus = $status
  } else {
    Log "Status atual: '$status'"
  }

  if ($status -eq "healthy") {
    Log "Container saudável. Disparando análise completa..."

    $analysisOutDir = Resolve-Path (Join-Path $projectRoot "glpi-analysis-cli\output")
    if (-not (Test-Path $analysisOutDir)) { New-Item -ItemType Directory -Force -Path $analysisOutDir | Out-Null }
    $analysisLog = Join-Path $analysisOutDir ("analysis_run_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")

    $modelName = "meta-llama/llama-3.1-8b-instruct"
    $baseUrl   = "http://host.docker.internal:9000/v1"
    $query     = "Relatorio completo: categorias com maior volume, desempenho por tecnico, tendencias mensais 2023-2025 e tempo medio de resolucao; gerar graficos."

    $openAiArg = @()
    if ($ngcKey -and $ngcKey.Length -gt 0) { $openAiArg = @('-e', "OPENAI_API_KEY=$ngcKey") }

    $cmd = @(
      'docker','run','--network','bd_cau_v2_app_network',
      '-e', "OPENAI_API_BASE=$baseUrl"
    ) + $openAiArg + @(
      '-e', "LLM_MODEL_NAME=$modelName",
      '-v', (Join-Path $projectRoot "glpi-analysis-cli:/app"),
      'glpi-analyst', $query
    )

    Log "Executando: $($cmd -join ' ')"
    try {
      & $cmd 2>&1 | Tee-Object -FilePath $analysisLog -Append
      Log "Análise concluída. Log salvo em: $analysisLog"
    } catch {
      Log "Falha ao executar análise: $($_.Exception.Message)"
    }

    break
  }

  if ((Get-Date) -gt $deadline) {
    Log "Timeout atingido sem 'healthy'. Encerrando monitor."
    exit 1
  }

  Start-Sleep -Seconds $IntervalSeconds
}

Log "Monitor finalizado."
