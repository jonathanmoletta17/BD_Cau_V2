---
description: Iniciar stack de IA local (Ollama + Open WebUI) para chat e experimentação com LLMs
---

# Workflow: LLM Local Stack

Este workflow inicia o stack de IA local usando GPU (RTX A4000).

## Pré-requisitos

- Docker Desktop rodando
- NVIDIA Container Toolkit instalado
- Modelo GPT-OSS 20B disponível em `~/.lmstudio/models/` (ou importado no Ollama)

## Passos

### 1. Verificar GPU disponível
```bash
nvidia-smi
```

### 2. Iniciar stack (Ollama + Open WebUI)
```bash
cd local-ai-stack
docker compose --env-file ../.env up -d
```

### 3. Verificar containers
```bash
docker ps --filter "name=ollama" --filter "name=open-webui"
```

### 4. Acessar Open WebUI
Abrir no navegador: http://localhost:3000

### 5. (Opcional) Importar modelo do LM Studio para Ollama
```bash
# Criar Modelfile
echo 'FROM C:\Users\jonathan-moletta\.lmstudio\models\gpt-oss-20b-MXFP4.gguf' > Modelfile

# Importar no Ollama
ollama create gpt-oss-20b -f Modelfile
```

### 6. Listar modelos disponíveis
```bash
ollama list
```

### 7. Testar modelo
```bash
ollama run gpt-oss-20b "Olá, como você está?"
```

## Parar Stack

```bash
cd local-ai-stack
docker compose --env-file ../.env down
```

## Portas Utilizadas

| Serviço | Porta |
|---------|-------|
| Ollama API | 11434 |
| Open WebUI | 3000 |

## Notas

- **VRAM:** O modelo GPT-OSS 20B ocupa ~12-13 GB. Não execute simultaneamente com o classificador em carga pesada.
- **LM Studio:** Se preferir usar LM Studio, ele roda na porta 1234 por padrão.
