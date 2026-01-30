# Contexto do Projeto BD_Cau_V2 - Para Antigravity

**Última Atualização**: 2025-12-06  
**Versão**: 1.0 (Baseline)

---

## 🎯 Sobre Este Projeto

**Nome**: BD_Cau_V2  
**Tipo**: Monorepo  
**Foco**: Ecossistema GLPI completo (análise, classificação e visualização de tickets)  
**Departamentos**: DTIC e SIS

### Propósito
Sistema integrado para gestão e análise de tickets GLPI, incluindo:
- Sincronização de dados GLPI → PostgreSQL local
- Classificação automática de tickets usando IA
- Dashboards interativos para análise
- Busca inteligente em tickets

---

## 📂 Estrutura (7 Subprojetos)

```
BD_Cau_V2/
├── glpi-data-service-v3/          # Backend principal
│   ├── Stack: FastAPI + SQLAlchemy + PostgreSQL
│   ├── Schemas: glpi, sis, dtic
│   └── Porta: 8000
├── glpi-dtic-agent-classificator/ # Agente de classificação IA
│   ├── Arquitetura: Híbrida (Embeddings + LLM)
│   ├── Modelo Embeddings: multilingual-e5-large
│   ├── LLM: Llama 3 / NVIDIA NIM / Gemini
│   └── Ver: docs/specs/ADR-001_Rewrite_To_Hybrid_Architecture.md
├── glpi-dtic-dashboard/           # Dashboard DTIC
│   └── Stack: React + Vite + TypeScript + Recharts
├── glpi-dtic-smart-search/        # Busca inteligente DTIC
├── glpi-sis-dashboard/            # Dashboard SIS
├── glpi-sis-smart-search/         # Busca inteligente SIS
└── glpi-sis-carregadores-dashboard/ # Dashboard carregadores
```

---

## 🧠 Decisões Arquiteturais Críticas

### 1. Clean Slate (2025-12-06)
- **Contexto**: Histórico Git completamente quebrado (migração caótica)
- **Decisão**: Recomeçar versionamento do zero
- **Baseline Commit**: `7d9773a`
- **Documento**: `MIGRATION_HISTORY.md`

### 2. Arquitetura Híbrida do Agente
- **Context**: IA generativa pura causava alucinações
- **Decisão**: Sistema híbrido determinístico
  - **Motor Primário**: Embeddings (rápido, 80-90% dos casos)
  - **Motor Secundário**: LLM (casos de baixa confiança)
- **Documento**: `glpi-dtic-agent-classificator/docs/specs/ADR-001_Rewrite_To_Hybrid_Architecture.md`

### 3. Monorepo
- **Decisão**: Manter tudo em um repositório único
- **Razão**: 7 serviços altamente acoplados, CI/CD simplificado
- **Trade-off**: Builds mais lentos vs coordenação mais fácil

---

## 🚫 Projetos Órfãos (NÃO EXISTEM MAIS - NÃO REFERENCIAR!)

Estes projetos foram **removidos** durante migração caótica:
- ❌ `glpi-data-service-v2` (substituído por v3)
- ❌ `rag-local` (projeto RAG descartado)
- ❌ `crawl4ai_workspace` (projeto DOE-RS descartado)

**Se eu mencionar estes projetos, estou ERRADO. Corrija-me referenciando este documento.**

---

## 🔧 Stack Tecnológico

### Backend
- **Python**: 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **DB**: PostgreSQL (local + schemas específicos)
- **API Externa**: GLPI REST API v10.x

### Frontend
- **Framework**: React 18
- **Build**: Vite
- **Linguagem**: TypeScript
- **Charts**: Recharts
- **Estado**: Hooks (useState, useEffect)

### IA/ML
- **Embeddings**: intfloat/multilingual-e5-large
- **LLM**: Gemini API (Google) / Llama 3 (local via Ollama)
- **GPU**: RTX A4000 16GB (disponível para processamento local)
- **Vector Store**: Simples (dict Python ou FAISS)

---

## 📋 Regras de Trabalho (CRÍTICO)

### Commits
- **OBRIGATÓRIO**: Conventional Commits (`type(scope): message`)
- **Tipos**: feat, fix, chore, docs, refactor, test, perf, style, ci
- **Ver**: `CONTRIBUTING.md`

### Código
- **Python**: PEP 8, docstrings obrigatórias, type hints recomendados
- **TypeScript**: ESLint + Prettier
- **Testes**: pytest (backend), Vitest (frontend)

### Proibições
- ❌ **NÃO** criar novos repositórios `.git` em subpastas
- ❌ **NÃO** commitar arquivos `.env`
- ❌ **NÃO** commitar `node_modules/`, `venv/`, `__pycache__/`
- ❌ **NÃO** adicionar dependências sem atualizar `requirements.txt` ou `package.json`

---

## 🎓 Conhecimento Acumulado

### Problema 1: "Working tree não está limpo"
**Causa**: Arquivos `.git` embedded em subpastas  
**Solução**: Remover com `Remove-Item -Recurse -Force <path>/.git`  
**Referência**: Commit `7d9773a` (baseline consolidation)

### Problema 2: "Contexto poluído de IAs"
**Causa**: Arquivos `.trae/` ou `.gemini/` com referências a projetos órfãos  
**Solução**: Remover arquivos órfãos, manter apenas contexto GLPI  
**Documentado em**: `final_consistency_report.md`

### Problema 3: "Classificação de tickets imprecisa"
**Causa**: Uso de LLM puro + dados sujos (histórico GLPI)  
**Solução**: Arquitetura híbrida + Golden Tickets (exemplos curados)  
**Documentado em**: `ADR-001_Rewrite_To_Hybrid_Architecture.md`

---

## 📁 Documentação Essencial

### Para Entender o Projeto
1. `README.md` - Overview e quick start
2. `MIGRATION_HISTORY.md` - Por que não há histórico Git
3. `CONTRIBUTING.md` - Como contribuir

### Para Entender o Agente
1. `glpi-dtic-agent-classificator/docs/specs/ADR-001_Rewrite_To_Hybrid_Architecture.md`
2. `glpi-dtic-agent-classificator/docs/specs/Architecture_Specs.md`

### Para Arquitetura
1. `docs/architecture/00_overview.md` (a ser criado)
2. `docs/architecture/02_agent_pipeline.md` (a ser criado)

---

## 🚀 Como Rodar (Quick Reference)

### Backend
```bash
cd glpi-data-service-v3
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### Dashboard
```bash
cd glpi-dtic-dashboard/frontend
npm install
npm run dev
```

### Agente (Classificador)
```bash
cd glpi-dtic-agent-classificator
pip install -r requirements.txt
python agent_classificator/main.py
```

---

## 🔮 Hardware Disponível

### GPU
- **Modelo**: NVIDIA RTX A4000
- **VRAM**: 16GB
- **Compute Capability**: 8.6 (Ampere)
- **Uso Ideal**: 
  - Embeddings locais (multilingual-e5-large cabe confortavelmente)
  - LLM até 13B parâmetros (Llama 3 13B quantizado)
  - Batch processing de tickets

### Setup Local de IA
- **Docker**: Ollama + Open WebUI
- **Modelos Recomendados**:
  - `llama3:13b` (13GB VRAM, excelente qualidade)
  - `mistral:7b` (7GB VRAM, mais rápido)
  - `nomic-embed-text` (embeddings, 400MB)

---

## 💡 Dicas para Antigravity (Eu!)

### Quando o Usuário Pedir para "Analisar o Agente"
1. Ir direto para `glpi-dtic-agent-classificator/docs/specs/`
2. Ler ADR-001 primeiro (decisões arquiteturais)
3. **NÃO** assumir que é LLM puro (é híbrido!)

### Quando o Usuário Mencionar "v2"
**CUIDADO**: Pode ser:
- `glpi-data-service-v2` (projeto ANTIGO, não existe mais)
- `glpi-data-service-v3` (projeto ATUAL, usar este)

### Quando o Usuário Pedir para "Criar Commit"
1. **SEMPRE** usar Conventional Commits
2. Verificar `CONTRIBUTING.md` se inseguro
3. Incluir referências (`Refs: MIGRATION_HISTORY.md`) quando relevante

### Quando o Usuário Mencionar "RAG" ou "DOE-RS"
**ATENÇÃO**: Projetos órfãos! **NÃO EXISTEM MAIS** neste repositório.  
Se o usuário insistir, perguntar se está trabalhando em projeto diferente.

---

## 📊 Métricas de Qualidade

- **Test Coverage**: (a definir)
- **Code Quality**: Black + Flake8 (Python), ESLint (TypeScript)
- **Documentation**: Inline docstrings + ADRs
- **Git Hygiene**: Conventional Commits obrigatório

---

**Este é meu cartão de memória do projeto. Consultar SEMPRE antes de iniciar trabalho.**
