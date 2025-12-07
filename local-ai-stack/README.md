# Local AI Stack - Ollama + RTX A4000

Stack completo de IA local aproveitando GPU NVIDIA RTX A4000 (16GB VRAM).

---

## Serviços Incluídos

1. **Ollama**: LLM runtime (Llama 3, Mistral, etc.)
2. **Open WebUI**: Interface web para Ollama
3. **PostgreSQL**: (Opcional) pgvector para embeddings

---

## Docker Compose

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - OLLAMA_KEEP_ALIVE=24h
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    volumes:
      - open_webui_data:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
    restart: unless-stopped

volumes:
  ollama_data:
  open_webui_data:
```

---

## Setup

### 1. Instalar NVIDIA Container Toolkit (Windows WSL2)

```bash
# No WSL2
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### 2. Subir Stack

```bash
cd local-ai-stack
docker-compose up -d
```

### 3. Verificar

```bash
# Ollama rodando
curl http://localhost:11434/api/version

# Open WebUI
# Abrir: http://localhost:3000
```

---

## Modelos Recomendados (RTX A4000 - 16GB)

### LLMs

| Modelo | VRAM | Qualidade | Velocidade | Uso |
|--------|------|-----------|------------|-----|
| `llama3:13b` | ~13GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Classificação complexa |
| `llama3:8b` | ~8GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Uso geral |
| `mistral:7b` | ~7GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Classificação simples |
| `gemma:7b` | ~7GB | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Testes rápidos |

### Embeddings

| Modelo | VRAM | Dimensões | Uso |
|--------|------|-----------|-----|
| `nomic-embed-text` | ~400MB | 768 | Embeddings gerais |
| `all-minilm` | ~120MB | 384 | Embeddings leves |

---

## Baixar Modelos

```bash
# LLM principal (recomendado)
docker exec ollama ollama pull llama3:13b

# LLM alternativo (mais rápido)
docker exec ollama ollama pull mistral:7b

# Embeddings
docker exec ollama ollama pull nomic-embed-text
```

---

## Uso no Agente Classificador

### Configuração (`agent_classificator/config.yaml`)

```yaml
llm:
  provider: "ollama"  # ou "gemini" para cloud
  model: "llama3:13b"
  base_url: "http://localhost:11434"
  temperature: 0.1
  max_tokens: 512
  
embeddings:
  provider: "local"  # sentence-transformers (GPU)
  model: "intfloat/multilingual-e5-large"
  device: "cuda"  # Usar RTX A4000
  batch_size: 32  # Ajustar conforme VRAM
```

### Código Python

```python
# agent_classificator/llm_client.py
from ollama import Client

client = Client(host='http://localhost:11434')

def classify_with_llm(text: str) -> dict:
    response = client.chat(
        model='llama3:13b',
        messages=[{
            'role': 'system',
            'content': 'Você é um classificador de tickets GLPI...'
        }, {
            'role': 'user',
            'content': f'Classifique: {text}'
        }]
    )
    return response['message']['content']
```

---

## Monitoramento GPU

```bash
# Terminal 1: Monitorar GPU
watch -n 1 nvidia-smi

# Terminal 2: Rodar classificador
python agent_classificator/main.py batch --limit 100
```

**Output esperado** (nvidia-smi):
```
| NVIDIA-SMI 535.xxx       Driver Version: 535.xxx      CUDA Version: 12.2     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
|   0  NVIDIA RTX A4000    On   | 00000000:01:00.0 Off |                  Off |
| 30%   45C    P2    80W / 140W |  12345MiB / 16376MiB |     95%      Default |
```

---

## Performance Tips

### 1. Batch Processing
```python
# RUIM: Processar um por um
for ticket in tickets:
    embedding = model.encode(ticket.text)  # GPU ociosa entre calls

# BOM: Processar em batch
texts = [t.text for t in tickets]
embeddings = model.encode(texts, batch_size=32)  # GPU saturada
```

### 2. Quantização (Reduzir VRAM)

```bash
# Modelo quantizado (menor qualidade, menos VRAM)
docker exec ollama ollama pull llama3:13b-q4_K_M  # ~7GB ao invés de 13GB
```

### 3. Context Window

```yaml
# Limitar tokens para economizar VRAM
llm:
  max_tokens: 256  # Ao invés de 2048
```

---

## Troubleshooting

**Erro: "CUDA out of memory"**
```bash
# 1. Verificar VRAM disponível
nvidia-smi

# 2. Usar modelo menor
docker exec ollama ollama pull llama3:8b

# 3. Reduzir batch_size
# Em config.yaml: batch_size: 16
```

**Ollama não inicia**
```bash
# Verificar logs
docker logs ollama

# Verificar GPU disponível para Docker
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**Muito Lento**
```bash
# Verificar se está usando GPU
docker exec ollama ollama ps

# Ver qual modelo está carregado
# Se estiver vazio, modelo não foi carregado (problema)
```

---

## Próximos Passos

1. Experimentar com `llama3:13b` vs `mistral:7b`
2. Medir latência vs qualidade
3. Implementar cache de embeddings
4. Considerar fine-tuning do modelo de embeddings

---

**Referências**:
- Ollama: https://ollama.ai
- Open WebUI: https://github.com/open-webui/open-webui
- NVIDIA Container Toolkit: https://github.com/NVIDIA/nvidia-docker
