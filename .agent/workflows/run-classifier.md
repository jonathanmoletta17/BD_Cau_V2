---
description: Rodar agente de classificação de tickets
---

# Run GLPI Ticket Classifier

Execute o agente de classificação automática de tickets GLPI.

---

## 1. Verificar Dependências

```bash
cd glpi-dtic-agent-classificator
pip list | grep -E "(torch|transformers|sentence-transformers)"
```

**Esperado**:
- torch >= 2.0.0
- transformers >= 4.30.0
- sentence-transformers >= 2.2.0

---

## 2. Rodar Classificador (Modo Batch)

// turbo
```bash
cd glpi-dtic-agent-classificator
python agent_classificator/main.py batch --limit 100
```

**Parâmetros**:
- `--limit N`: Processar N tickets não classificados
- `--category nome`: Classificar apenas categoria específica
- `--force`: Reclassificar tickets já processados

---

## 3. Rodar Classificador (Modo Interativo)

```bash
python agent_classificator/main.py interactive
```

Teste com texto custom:
```
> Digite descrição do ticket: Meu computador não liga
Categoria predita: Hardware > Desktop
Confiança: 0.92
Método: embeddings
```

---

## 4. Monitorar Performance

```bash
# Ver log de classificações
tail -f logs/classifier.log

# Estatísticas
python agent_classificator/stats.py
```

---

## Configuração GPU (RTX A4000)

**Verificar CUDA**:
```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

**Forçar CPU** (para testes):
```bash
CUDA_VISIBLE_DEVICES="" python agent_classificator/main.py batch
```

---

## Troubleshooting

**Erro: "CUDA out of memory"**
- Reduzir batch_size em `config.yaml`
- Usar modelo menor (e5-base ao invés de e5-large)

**Classificações Ruins**
- Verificar Golden Tickets em `data/golden_tickets/`
- Re-gerar embeddings: `python scripts/regenerate_embeddings.py`

**Muito Lento**
- Verificar se está usando GPU: `nvidia-smi`
- Aumentar batch_size se tiver VRAM disponível
