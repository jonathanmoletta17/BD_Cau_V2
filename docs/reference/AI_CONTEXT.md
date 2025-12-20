# Contexto Compartilhado de IA - BD_Cau_V2

**Para**: Antigravity (Gemini), Cursor (Trae), Copilot, e qualquer outra IA  
**Última Atualização**: 2025-12-06

---

## ⚡ Quick Facts

- **Tipo**: Monorepo
- **Foco**: Ecossistema GLPI (8 subprojetos)
- **Backend**: FastAPI + PostgreSQL + CLI Analysis
- **Frontend**: React + Vite + TypeScript
- **IA**: Arquitetura Híbrida (Embeddings + LLM)
- **GPU**: RTX A4000 16GB (disponível)

---

## 🚫 NÃO REFERENCIAR (Projetos Órfãos)

Estes projetos **NÃO EXISTEM MAIS**:
- ❌ `glpi-data-service-v2` (substituído)
- ❌ `rag-local`
- ❌ `crawl4ai_workspace`
- ❌ DOE-RS

**Se eu mencionar estes projetos, estou ERRADO!**

---

## 📋 Documentação Essencial

### Para Entender o Projeto
1. `README.md` - Overview
2. `MIGRATION_HISTORY.md` - Por que não há histórico Git
3. `CONTRIBUTING.md` - Conventional Commits obrigatório

### Para Arquitetura
1. `docs/architecture/00_overview.md` - Diagrama completo
2. `.antigravity/context.md` - Contexto detalhado
3. `.cursorrules` - Regras de código

### Para IA/ML
1. `glpi-dtic-agent-classificator/docs/specs/ADR-001_Rewrite_To_Hybrid_Architecture.md`
2. `local-ai-stack/README.md` - Setup GPU

---

## ⚙️ Workflows Disponíveis

Use `.agent/workflows/` para tarefas automatizadas:
- `deploy-dev.md` - Subir ambiente completo
- `test-all.md` - Rodar todos os testes
- `sync-glpi.md` - Sincronizar GLPI → PostgreSQL
- `run-classifier.md` - Classificar tickets

---

## 💡 Regras Críticas

### Commits
**SEMPRE** usar Conventional Commits:
```
feat(scope): descrição
fix(scope): correção
chore(scope): manutenção
```

### Código
- **Python**: PEP 8, docstrings, type hints
- **TypeScript**: ESLint, tipos explícitos
- **Testes**: pytest (backend), Vitest (frontend)

### Proibições
- ❌ NÃO criar `.git` em subpastas
- ❌ NÃO commitar `.env`, `venv/`, `node_modules/`
- ❌ NÃO assumir que agente é "LLM puro" (é híbrido!)

---

## 🔧 Hardware & AI Architecture

**GPU**: NVIDIA RTX A4000 (16GB VRAM)
**Drivers**: 
- **Estável**: 566.x (REQUIRED para WSL2 vLLM)
- ❌ **Instável**: 591.44 (Quebra JIT/xgrammar)

**Local AI Stack (vLLM)**:
- **Porta**: 9000 (Externa) -> 8000 (Interna)
- **Modelo**: `Qwen/Qwen2.5-Coder-7B-Instruct-AWQ`
- **Configuração**: `config.json` padrão (sem Triton Flags)
- **⚠️ LIMITAÇÃO CRÍTICA**: 
    - **NÃO USAR** `response_format={"type": "json_object"}`. Isso causa crash do servidor (erro de linker xgrammar).
    - **USAR** Prompt Engineering para extrair JSON.

- Embeddings locais: sentence-transformers (GPU)

---

## 🎯 Estrutura

```
BD_Cau_V2/
├── glpi-data-service/                 # Backend (porta 8000)
├── glpi-analysis-cli/                 # Ferramenta CLI de Análise
├── glpi-dtic-agent-classificator/     # Agente IA
├── glpi-dtic-dashboard/               # Dashboard DTIC (porta 3005)
├── glpi-sis-dashboard/                # Dashboard SIS (porta 3001)
├── glpi-dtic-smart-search/            # Busca DTIC (porta 3002)
├── glpi-sis-smart-search/             # Busca SIS (porta 3003)
├── glpi-sis-carregadores-dashboard/   # Carregadores (porta 3004)
├── local-ai-stack/                    # Ollama + Open WebUI
├── docs/architecture/                 # Arquitetura
└── .cursorrules                       # Regras Cursor/Trae
```

---

**Para detalhes completos**, consultar:
- Antigravity: `.antigravity/context.md`
- Cursor/Trae: `.cursorrules`
