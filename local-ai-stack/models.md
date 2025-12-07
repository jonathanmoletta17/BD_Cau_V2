# Modelos Recomendados para RTX A4000 (16GB VRAM)

Este documento lista os modelos de IA recomendados para uso com a GPU RTX A4000.

---

## LLMs (Large Language Models)

### Tier 1: Alta Qualidade (13GB)
```bash
ollama pull llama3:13b
```
- **VRAM**: ~13GB
- **Parâmetros**: 13 bilhões
- **Qualidade**: ⭐⭐⭐⭐⭐ Excelente
- **Velocidade**: ⭐⭐⭐ Boa
- **Uso**: Classificação complexa, reasoning sofisticado

### Tier 2: Balanceado (8GB)
```bash
ollama pull llama3:8b
ollama pull mistral:7b
```
- **VRAM**: ~7-8GB
- **Qualidade**: ⭐⭐⭐⭐ Muito boa
- **Velocidade**: ⭐⭐⭐⭐ Muito boa
- **Uso**: Classificação geral, casos de uso diário

### Tier 3: Rápido (4-7GB)
```bash
ollama pull gemma:7b
ollama pull phi:3
```
- **VRAM**: ~4-7GB
- **Qualidade**: ⭐⭐⭐ Boa
- **Velocidade**: ⭐⭐⭐⭐⭐ Excelente
- **Uso**: Testes rápidos, prototipação

---

## Embeddings Models

### Recomendado: Nomic Embed
```bash
ollama pull nomic-embed-text
```
- **VRAM**: ~400MB
- **Dimensões**: 768
- **Contexto**: 8192 tokens
- **Uso**: Embeddings gerais, classificação

### Alternativo: All-MiniLM
```bash
ollama pull all-minilm
```
- **VRAM**: ~120MB
- **Dimensões**: 384
- **Contexto**: 512 tokens
- **Uso**: Embeddings leves, quando velocidade é crítica

---

## Modelos Especializados

### Code Generation
```bash
ollama pull codellama:13b
```
- **VRAM**: ~13GB
- **Uso**: Geração de código, análise de scripts

### Portuguese-Focused
```bash
ollama pull sabia-2:7b  # Modelo treinado em PT-BR
```
- **VRAM**: ~7GB
- **Uso**: Se precisar de melhor compreensão de português

---

## Quantização (Menor VRAM)

Para economizar VRAM, use versões quantizadas:

```bash
# Original: 13GB
ollama pull llama3:13b

# Quantizado Q4: ~7GB (perda mínima de qualidade)
ollama pull llama3:13b-q4_K_M

# Quantizado Q5: ~9GB (qualidade quase original)
ollama pull llama3:13b-q5_K_M
```

**Trade-off**:
- **Q4**: 50% menos VRAM, 5-10% perda de qualidade
- **Q5**: 30% menos VRAM, 2-5% perda de qualidade

---

## Recomendação para Projeto GLPI

### Setup Inicial
```bash
# 1. LLM principal (classificação complexa)
ollama pull llama3:13b

# 2. LLM rápido (fallback)
ollama pull mistral:7b

# 3. Embeddings
ollama pull nomic-embed-text
```

**VRAM Total**: ~13GB + 7GB + 0.4GB = ~20GB

⚠️ **Atenção**: Somente 1 modelo LLM pode estar ativo por vez! RTX A4000 tem 16GB.

### Uso no Agente
- **Embeddings primary**: Usar sentence-transformers (local, GPU)
- **LLM fallback**: Ollama com `llama3:13b` (para baixa confiança)
- **Alternativo**: Gemini API (cloud, quando Ollama indisponível)

---

## Verificar Modelos Instalados

```bash
# Listar modelos
ollama list

# Informações detalhadas
ollama show llama3:13b

# Remover modelo
ollama rm gemma:7b
```

---

## Performance Esperada (RTX A4000)

| Modelo | Tokens/segundo | Latência (p/ resposta) |
|--------|----------------|------------------------|
| llama3:13b | ~30-40 t/s | ~3-5s |
| mistral:7b | ~50-70 t/s | ~2-3s |
| gemma:7b | ~60-80 t/s | ~1-2s |

*Latência para resposta de 100 tokens*

---

## Próximos Passos

1. Experimentar com diferentes modelos
2. Medir accuracy vs speed
3. Considerar fine-tuning para categorias GLPI específicas
4. Implementar cache de respostas frequentes

---

**Referências**:
- Ollama Models: https://ollama.ai/library
- Model Benchmarks: https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard
