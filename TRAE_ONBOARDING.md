# 🤖 Onboarding: Trae (Cursor AI)

**Para**: Trae (Cursor AI / @cursor)  
**De**: Antigravity (Google Gemini)  
**Data**: 2025-12-06  
**Assunto**: Nova Infraestrutura de IA - Como Proceder

---

## 📋 Resumo Executivo

Durante a sessão de hoje com Antigravity, criamos uma **infraestrutura completa de IA** para o projeto BD_Cau_V2. Este documento contextualiza você (Trae) sobre as mudanças e como proceder daqui pra frente.

---

## 🎯 O Que Mudou

### Antes (Até 2025-12-06 22:00)
- ❌ Sem configurações específicas para IAs
- ❌ Workflows manuais
- ❌ GPU RTX A4000 subutilizada
- ❌ Sem contexto persistente

### Depois (2025-12-06 23:10)
- ✅ Estrutura completa de configs `.antigravity/`, `.cursorrules`, `AI_CONTEXT.md`
- ✅ 4 workflows automatizados em `.agent/workflows/`
- ✅ Stack de IA local (Ollama + Open WebUI + GPU)
- ✅ Documentação arquitetural completa

---

## 📁 Arquivos Críticos para Você (Trae)

### 1. `.cursorrules` (SEU MANUAL)

**Localização**: Raiz do projeto  
**O que é**: Suas regras de trabalho neste projeto

**Principais Regras**:
- ✅ **Conventional Commits** obrigatório (`feat(scope): message`)
- ✅ **Filosofia "Less is More"** (simplicidade sobre complexidade)
- ✅ **Monorepo** (7 subprojetos GLPI)
- ❌ **NÃO referenciar** projetos órfãos (rag-local, DOE-RS, crawl4ai)
- ❌ **NÃO criar** novos `.git` em subpastas

**Leia SEMPRE** este arquivo antes de sugerir mudanças arquiteturais!

### 2. `.agent/workflows/` (SEUS COMANDOS RÁPIDOS)

**Localização**: `.agent/workflows/`

**Workflows Disponíveis**:

#### `/deploy-dev`
Sobe todo o ambiente de desenvolvimento:
- Backend (glpi-data-service-v3)
- Dashboard DTIC
- Dashboard SIS (opcional)

#### `/test-all`
Roda suite completa de testes:
- Backend (pytest)
- Agente (pytest)
- Linting (black, flake8)

#### `/sync-glpi`
Sincroniza dados GLPI → PostgreSQL

#### `/run-classifier`
Executa agente de classificação de tickets (com GPU)

**Como Usar**:
Quando o usuário pedir "suba o ambiente", você pode referenciar ou executar automaticamente o workflow adequado.

### 3. `AI_CONTEXT.md` (REFERÊNCIA RÁPIDA)

**Localização**: Raiz do projeto

**O que tem**:
- Quick facts do projeto
- Documentação essencial
- Projetos órfãos (NÃO USAR!)
- Regras críticas

**Quando Consultar**: Se tiver dúvida sobre a estrutura do projeto.

---

## 🚀 Como Proceder Daqui Pra Frente

### Quando o Usuário Pedir "Suba o Dashboard DTIC"

**ANTES** (você faria):
```bash
cd glpi-dtic-dashboard/frontend
npm install
npm run dev
```

**AGORA** (recomendado):
1. Referenciar workflow: "Vou usar o workflow `/deploy-dev`"
2. Executar automaticamente os comandos do workflow
3. Verificar que subiu na porta 3000

### Quando o Usuário Pedir "Rode os Testes"

**ANTES**: Comandos manuais

**AGORA**:
1. Usar workflow `/test-all`
2. Reportar cobertura de testes

### Quando o Usuário Mencionar "v2" ou "RAG"

**ATENÇÃO** 🚨:
- `glpi-data-service-v2` NÃO existe mais (substituído por v3)
- `rag-local` NÃO existe mais (projeto órfão)
- `crawl4ai_workspace` NÃO existe mais (projeto órfão)

**Ação**: Confirmar com usuário se está falando sobre projeto diferente!

### Quando Criar Commits

**SEMPRE** usar Conventional Commits:
```
feat(scope): descrição
fix(scope): correção  
chore(scope): manutenção
docs(scope): documentação
```

**Validação**: Veja `.cursorrules` seção "Conventional Commits Obrigatório"

---

## 🧠 Diferenças: Você (Trae) vs Antigravity

### Antigravity (Gemini)
- Tem `.antigravity/context.md` (contexto detalhado)
- Foco em planejamento, arquitetura, documentação
- Trabalha em sessões longas

### Você (Trae)
- Tem `.cursorrules` (regras de código)
- Foco em edição de código, refatoração, testes
- Trabalha inline com o usuário

### Contexto Compartilhado
Ambos têm acesso a `AI_CONTEXT.md` (visão geral do projeto)

---

## 🎯 Agente de Classificação (IMPORTANTE!)

### Arquitetura Híbrida

**NÃO** é um chatbot simples!

**Pipeline**:
1. **Embeddings** (primário): multilingual-e5-large → Similaridade com Golden Tickets
2. **LLM** (fallback): Llama 3 / Gemini → Apenas se confiança < 0.75

**Documentação**: 
`glpi-dtic-agent-classificator/docs/specs/ADR-001_Rewrite_To_Hybrid_Architecture.md`

**Leia SEMPRE** este ADR antes de sugerir mudanças no agente!

---

## 🖥️ Stack de IA Local (Ollama)

### O Que É?

Um stack completo de LLMs rodando **localmente** na GPU RTX A4000:
- **Ollama**: Runtime para Llama 3, Mistral, etc.
- **Open WebUI**: Interface tipo ChatGPT
- **GPU Acelerado**: CUDA

### Como Iniciar

```bash
cd local-ai-stack
docker-compose up -d

# Baixar modelo
docker exec ollama ollama pull llama3:13b
```

### Como Usar no Agente

Editar `glpi-dtic-agent-classificator/config.yaml`:
```yaml
llm:
  provider: "ollama"
  model: "llama3:13b"
  base_url: "http://localhost:11434"
```

### Performance Esperada

- **Llama 3 13B**: ~30-40 tokens/s
- **Latência**: 3-5s por resposta (100 tokens)
- **VRAM**: ~13GB

---

## 📊 Validação Realizada

### Dashboard DTIC

**Status**: ✅ **Validado e funcionando**

**Evidência**:

![Dashboard DTIC Carregado](file:///C:/Users/jonathan-moletta/.gemini/antigravity/brain/6cff7bb8-80ec-4d84-9d4d-d2fcec29570f/dashboard_dtic_carregado_1765073242618.png)

**Funcionalidades Confirmadas**:
- ✅ Métricas gerais
- ✅ Gráficos de distribuição
- ✅ Ranking de técnicos
- ✅ Atividades recentes

### Stack de IA Local

**Status**: 🔄 **Docker baixando imagens** (em andamento)

**Próximo Passo**: Validar acesso ao Open WebUI (http://localhost:3000)

---

## 🎓 Exemplos de Interação

### Exemplo 1: Usuário Pede "Suba o Projeto"

**Você (Trae)**:
```
Vou usar o workflow de deploy-dev para subir todos os serviços:

1. Backend (porta 8000)
2. Dashboard DTIC (porta 3000)
3. Dashboard SIS (porta 5174)

Executando...
```

**Comandos**:
```bash
cd glpi-data-service-v3
uvicorn src.main:app --reload --port 8000

cd glpi-dtic-dashboard/frontend
npm run dev
```

### Exemplo 2: Usuário Menciona "rag-local"

**Você (Trae)**:
```
⚠️ ATENÇÃO: `rag-local` não existe mais neste projeto (foi removido durante a migração).

Você está falando sobre:
1. Este projeto (BD_Cau_V2 - GLPI)?
2. Outro projeto diferente?

Veja `MIGRATION_HISTORY.md` para detalhes.
```

### Exemplo 3: Usuário Pede "Classifique Tickets"

**Você (Trae)**:
```
Vou usar o workflow de classificação:

Executando:
cd glpi-dtic-agent-classificator
python agent_classificator/main.py batch --limit 100

Nota: O agente usa arquitetura híbrida (Embeddings + LLM).
Ver: docs/specs/ADR-001_Rewrite_To_Hybrid_Architecture.md
```

---

## 💡 Dicas para Você (Trae)

### Quando Sugerir Mudanças Arquiteturais

1. **Verificar** se existe ADR relevante em `docs/architecture/decisions/`
2. **Consultar** `.cursorrules` seção "Quando Criar ADR"
3. **Propor** criar novo ADR se mudança for significativa

### Quando o Usuário Pede "Refatore o Agente"

1. **Ler PRIMEIRO**: `ADR-001_Rewrite_To_Hybrid_Architecture.md`
2. **Entender**: Arquitetura híbrida (não é LLM puro!)
3. **Sugerir**: Mudanças alinhadas com a decisão arquitetural

### Quando Commitar

**SEMPRE** validar:
- ✅ Conventional Commits (`feat`, `fix`, `chore`)
- ✅ Scope apropriado (`agent`, `dashboard`, `api`)
- ✅ Sem `.env`, `venv/`, `node_modules/`

---

## 🔗 Documentação Essencial

### Para Você Ler Agora
1. `.cursorrules` - Suas regras de trabalho
2. `AI_CONTEXT.md` - Visão geral do projeto
3. `README.md` - Setup e estrutura

### Para Consultar Quando Necessário
1. `.agent/workflows/` - Workflows automatizados
2. `MIGRATION_HISTORY.md` - Por que não há histórico Git
3. `CONTRIBUTING.md` - Conventional Commits detalhado
4. `docs/architecture/00_overview.md` - Diagrama arquitetural

---

## 🎯 Checklist de Onboarding

- [ ] Ler `.cursorrules` completamente
- [ ] Entender workflows em `.agent/workflows/`
- [ ] Memorizar projetos órfãos (NÃO usar!)
- [ ] Consultar `AI_CONTEXT.md` quando em dúvida
- [ ] Testar workflows `/deploy-dev` e `/test-all`
- [ ] Ler ADR-001 do agente de classificação

---

## ✨ Conclusão

Bem-vindo à nova infraestrutura! 🚀

Você agora tem:
- ✅ Regras claras (`.cursorrules`)
- ✅ Workflows automatizados (`.agent/workflows/`)
- ✅ Contexto compartilhado (`AI_CONTEXT.md`)
- ✅ Stack de IA local (Ollama + GPU)

**Como Proceder**:
1. Ler `.cursorrules` (seu manual)
2. Usar workflows quando aplicável
3. Referenciar `AI_CONTEXT.md` para dúvidas rápidas
4. Consultar Antigravity (`.antigravity/context.md`) para decisões históricas

Vamos trabalhar juntos de forma mais eficiente! 💪

---

**Criado por**: Antigravity (Google Gemini)  
**Data**: 2025-12-06 23:10  
**Versão**: 1.0
