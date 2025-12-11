# Local AI Stack

Infraestrutura local de LLM usando vLLM com quantização AWQ-INT4.

## 🎯 Objetivo

Fornecer um servidor LLM local compatível com API OpenAI para os projetos:
- `glpi-dtic-agent-classificator` - Classificação de tickets
- `glpi-analysis-cli` - Análise de dados GLPI

## 🚀 Quick Start

### Iniciar

```bash
docker-compose up -d
```

### Verificar Status

```bash
docker logs glpi-vllm-awq --follow
```

Aguarde "Application startup complete" (~5 minutos na primeira execução).

### Parar

```bash
docker-compose down
```

## ⚙️ Configuração

### Modelo

**Nome**: `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4`  
**Quantização**: AWQ-INT4  
**Tamanho**: ~4.5 GB  
**VRAM**: ~6 GB  

### Recursos

- **GPU**: 1x (NVIDIA RTX A4000 ou similar)
- **GPU Memory Utilization**: 90%
- **Max Model Length**: 4096 tokens
- **Shared Memory**: 16 GB

### Portas

| Porta Externa | Porta Interna | Serviço |
|---------------|---------------|---------|
| **9000** | 8000 | vLLM API Server |

**API Endpoint**: `http://localhost:9000/v1`

## 🔍 Health Check

### Automático (Docker)

O container possui healthcheck configurado:

```yaml
test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
start_period: 300s
interval: 30s
timeout: 10s
retries: 60
```

### Manual

```bash
# Health
curl http://localhost:9000/health

# Listar modelos
curl http://localhost:9000/v1/models

# Test completion
curl http://localhost:9000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4",
    "prompt": "Hello, ",
    "max_tokens": 10
  }'
```

## 📂 Volumes

```yaml
C:\NIM\cache\huggingface:/root/.cache/huggingface
```

Cache de modelos persistido localmente em `C:\NIM\cache\huggingface`.

## 🛠️ Configuração Avançada

### docker-compose.yml

```yaml
services:
  vllm-llm-awq:
    image: vllm/vllm-openai:latest
    container_name: glpi-vllm-awq
    runtime: nvidia
    ports:
      - "9000:8000"
    command: >
      --model hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4
      --quantization awq_marlin
      --gpu-memory-utilization 0.90
      --max-model-len 4096
      --dtype auto
      --trust-remote-code
      --enforce-eager
      --disable-log-stats
```

### Variáveis de Ambiente (.env)

```env
HF_TOKEN=seu_token_opcional  # Apenas se modelo privado
NGC_API_KEY=seu_api_key      # NVIDIA (se necessário)
```

## 🔧 Troubleshooting

### Container não inicia

1. Verificar se GPU está disponível:
   ```bash
   nvidia-smi
   ```

2. Verificar runtime nvidia:
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
   ```

### Modelo demora para carregar

É normal! Processo de inicialização:
1. Download do modelo (~4.5 GB) **[1-3 min]**
2. Carregamento na GPU **[2-3 min]**
3. Warmup **[30s]**

**Total**: ~5-7 minutos na primeira execução.

### Out of Memory

Reduzir `--gpu-memory-utilization`:

```yaml
command: >
  --model hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4
  --quantization awq_marlin
  --gpu-memory-utilization 0.80  # Reduzido de 0.90
  --max-model-len 4096
```

### Porta 9000 já em uso

Alterar mapeamento em `docker-compose.yml`:

```yaml
ports:
  - "9001:8000"  # Usar porta 9001
```

Atualizar `.env` dos projetos consumidores:
```env
LLM_BASE_URL=http://host.docker.internal:9001/v1
```

## 📊 Monitoramento

### Script de Monitoramento

```bash
./scripts/monitor_nim.ps1
```

Monitora uso de GPU, memória e status do modelo.

## 🔗 Integração

### Projetos que Usam Este Stack

1. **glpi-dtic-agent-classificator**
   ```env
   LLM_BASE_URL=http://host.docker.internal:9000/v1
   LLM_MODEL_NAME=hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4
   ```

2. **glpi-analysis-cli**
   ```env
   OPENAI_API_BASE=http://host.docker.internal:9000/v1
   LLM_MODEL_NAME=hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4
   ```

### Compatibilidade API

✅ OpenAI API v1 compatible:
- `/v1/completions`
- `/v1/chat/completions`
- `/v1/models`
- `/health`

## 📝 Logs

### Ver logs em tempo real

```bash
docker logs glpi-vllm-awq --follow
```

### Últimas 50 linhas

```bash
docker logs glpi-vllm-awq --tail 50
```

## 🎓 Recursos

- [vLLM Documentation](https://docs.vllm.ai/)
- [AWQ Quantization](https://github.com/mit-han-lab/llm-awq)
- [Model Card](https://huggingface.co/hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4)

## 📄 Licença

MIT
