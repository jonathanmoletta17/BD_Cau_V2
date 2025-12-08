# Histórico de Migração - BD_Cau_V2

## Contexto da Migração

**Data**: Dezembro 2025  
**Razão**: Consolidação após múltiplas movimentações de pastas e renomeações

---

## Estado Anterior (Aproximado)

### Projetos Antigos
- **Projeto DOE-RS**: `crawl4ai_workspace` com agentes de scraping do Diário Oficial
- **Projeto RAG Local**: `rag-local` com PostgreSQL + pgvector + Ollama
- **GLPI V2**: `glpi-data-service-v2` (versão anterior do backend)

### Versionamento
- **Status**: Fragmentado entre múltiplos `.git` (histórico perdido)
- **Causa**: Movimentações caóticas de pastas entre diretórios
- **Consequência**: Rastreabilidade completamente quebrada

### Estrutura Desatualizada
```
BD_Cau_V2/ (estrutura OLD - não existe mais)
├── glpi-data-service-v2/      ❌ Substituído por v3
├── rag-local/                  ❌ Projeto removido
└── crawl4ai_workspace/         ❌ Projeto removido
    └── ottomator-agents/
        └── crawl4AI-agent-v2/
```

---

## Estado Atual (Baseline Consolidado)

### Foco
- **Escopo Único**: Ecossistema **GLPI** completo
- **Departamentos**: DTIC e SIS
- **Propósito**: Gestão e análise de tickets GLPI

### Estrutura
```
BD_Cau_V2/ (estrutura ATUAL)
├── glpi-data-service/             ✅ Backend principal (FastAPI + PostgreSQL)
├── glpi-dtic-agent-classificator/ ✅ IA para classificação de tickets
├── glpi-dtic-dashboard/           ✅ Dashboard React DTIC (porta 3005)
├── glpi-dtic-smart-search/        ✅ Busca inteligente DTIC (porta 3002)
├── glpi-sis-dashboard/            ✅ Dashboard React SIS (porta 3001)
├── glpi-sis-smart-search/         ✅ Busca inteligente SIS (porta 3003)
├── glpi-sis-carregadores-dashboard/ ✅ Dashboard carregadores (porta 3004)
└── docs/                          ✅ Documentação técnica
```

**Total**: 7 subprojetos ativos, todos relacionados ao GLPI

### Versionamento
- **Novo Início**: Repositório Git iniciado do zero (Clean Slate)
- **Razão**: Impossibilidade técnica de recuperação de histórico anterior
- **Data**: 2025-12-06

---

## Decisões Arquiteturais Preservadas

### 1. Monorepo
- **Decisão**: Manter todos os componentes GLPI em um único repositório
- **Justificativa**: 
  - Componentes altamente acoplados (compartilham mesmo domínio)
  - Facilita refatorações cross-project
  - Simplifica CI/CD inicial
  - Evita complexidade de coordenação multi-repo

### 2. Separação de Concerns
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL (`glpi-data-service`)
- **Frontend**: React + Vite + TypeScript (dashboards)
- **Agentes**: Python standalone (`agent-classificator`)
- **Busca**: Componentes especializados (smart-search)

### 3. PostgreSQL como Fonte Única de Verdade
- **Schemas**:
  - `glpi`: Dados sincronizados da API GLPI
  - `sis`: Dados específicos do departamento SIS
  - `dtic`: Dados específicos do departamento DTIC
- **Sincronização**: ETL automático do GLPI para banco local

### 4. Integração com GLPI via API
- **Conexão**: REST API do GLPI (versão 10.x)
- **Autenticação**: API Token
- **Uso**: Leitura de tickets, usuários, categorias, grupos

---

## Razões para Reset de Versionamento

### Evidências Técnicas
1. ✅ **Busca Completa Executada**
   - Verificados: `Projetos_Locais`, `Desktop`, `Documents`, `Downloads`, `OneDrive`
   - Resultado: **0 repositórios `.git` encontrados**

2. ✅ **Estrutura Completamente Alterada**
   - Projetos renomeados: `v2` → `v3`
   - Projetos removidos: `rag-local`, `crawl4ai_workspace`
   - Novos projetos: múltiplos dashboards e smart-search

3. ✅ **Documentação Desalinhada**
   - README.md antigo descrevia estrutura inexistente
   - `.gitignore` continha referências a projetos órfãos
   - Contexto de IAs (`.trae`) poluído com projetos antigos

### Decisão
- **Estratégia**: Clean Slate (recomeço limpo)
- **Alternativas Descartadas**: 
  - ❌ Rescue & Rebuild: Inviável (nenhum histórico recuperável)
  - ❌ Cherry-pick seletivo: Inviável (nenhum commit disponível)

---

## Garantias de Continuidade

### Código-Fonte
- ✅ **100% Preservado**: Todo código funcional mantido
- ✅ **Funcionalidades Ativas**: Todos os serviços operacionais
- ✅ **Testes**: Suites de testes mantidas (quando existentes)

### Documentação
- ✅ **Documentação Técnica**: Migrada para `docs/`
- ✅ **Comparações de Versões**: `V1_VS_V2_ORGANIZATION.md` preservado
- ✅ **Modelo de Dados**: Documentação de schemas mantida

### Configurações
- ✅ **Ambientes**: `.env.example` em cada subprojeto
- ✅ **Dependências**: `requirements.txt` e `package.json` atualizados
- ✅ **Docker**: Configurações `docker-compose` preservadas

### Conhecimento de Negócio
- ✅ **Lógica de Domínio**: Regras de negócio no código
- ✅ **Integrações**: Conhecimento de endpoints GLPI
- ✅ **Workflows**: Processos documentados

---

## Limpeza Realizada

### Remoção de Poluição de Contexto
**Local**: `.trae/documents` (contexto da IDE Cursor)

**Arquivos Removidos** (8 total):
1. `Diagnóstico e Correções para UI do RAG (DOE-RS).md`
2. `Executar e validar melhorias RAG DOE‑RS.md`
3. `Instalar e Rodar Crawl4AI + Agente RAG (Windows).md`
4. `Integração DOE‑RS ao RAG (MVP).md`
5. `Limpeza e Padronização do Projeto BD_Cau_V2.md` (desatualizado)
6. `Plano Pipeline RAG Local (PostgreSQL + pgvector + Ollama).md`
7. `Precisão da busca em doe_rs_atos...md`
8. `Relatório Técnico_ Arquitetura de Contexto Trae vs. Antigravity.md` (obsoleto)

**Razão**: Evitar alucinações das IAs sobre projetos que não existem mais

### Atualização de Documentação
- **README.md**: Reescrito completamente
  - ❌ Removido: Referências a v2, rag-local, crawl4ai
  - ✅ Adicionado: Estrutura real, 7 subprojetos, governança

- **.gitignore**: Atualizado
  - ❌ Removido: `venv_crawl4ai/`, `crawl4ai_workspace/`, `agents/**/venv*/`
  - ✅ Adicionado: Proteção contextos IA (`.trae/`, `.gemini/`, `.cursor/`)

---

## Governança Futura

### Estrutura de Branches
```
main       → Produção (protegido, requer PR)
  ↓
develop    → Integração (branch padrão para merge)
  ↓
feature/*  → Desenvolvimento
```

### Conventional Commits (Obrigatório)
```
type(scope): message

Types:
- feat:     Nova funcionalidade
- fix:      Correção de bug
- chore:    Manutenção (deps, configs)
- docs:     Documentação
- refactor: Refatoração sem mudança de comportamento
- test:     Testes
- perf:     Performance
- style:    Formatação
```

### Proteção de Contexto
- **Git**: `.trae/`, `.gemini/`, `.cursor/` NUNCA commitados
- **Docs**: Artifacts de IAs migrados para `docs/` quando relevantes
- **Segredos**: `.env` NUNCA commitado (usar `.env.example`)

---

## Cronologia

| Data | Evento |
|------|--------|
| **~2024** | Projetos DOE-RS e RAG em desenvolvimento |
| **2024-2025** | Múltiplas migrações de pastas (histórico perdido) |
| **2025-12** | Evolução para GLPI V3 e expansão de dashboards |
| **2025-12-06** | Consolidação Clean Slate e novo versionamento |

---

## Commit Inicial

**SHA**: [será preenchido após commit]

**Mensagem**:
```
chore: baseline consolidation after migration

- Projeto reestruturado após migração caótica de pastas
- Estrutura atual: 7 subprojetos GLPI
  - glpi-data-service-v3 (backend FastAPI + PostgreSQL)
  - glpi-dtic-agent-classificator (agente de classificação)
  - glpi-dtic-dashboard (dashboard React/Vite)
  - glpi-dtic-smart-search (busca inteligente)
  - glpi-sis-dashboard (dashboard SIS)
  - glpi-sis-smart-search (busca SIS)
  - glpi-sis-carregadores-dashboard
- Histórico anterior não recuperável; novo versionamento iniciado
- Documentação e contexto de negócio preservados

Refs: MIGRATION_HISTORY.md
```

---

**Responsável**: Jonathan Moletta  
**Ferramentas**: Antigravity (Google Gemini) + Trae (Cursor AI)  
**Validação**: Diagnóstico completo executado
