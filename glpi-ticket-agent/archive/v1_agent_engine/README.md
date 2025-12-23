# AgentEngine V1 - Código Arquivado

**Data de Arquivamento:** 22/12/2025  
**Motivo:** Substituído pela arquitetura TOD (Task-Oriented Dialogue) V2

---

## 📦 Arquivos Arquivados

### `/core/` - Motor Principal V1
1. **engine.ts** (5.9 KB)
   - Classe `AgentEngine`
   - Lógica de fluxo antiga baseada em extração + validação
   - Substituído por: `ConversationalAgent` (TOD)

2. **types.ts** (1.4 KB)
   - Tipos TypeScript para V1
   - Interfaces: `EngineConfig`, `SessionState`, etc.
   - Substituído por: `tod/interfaces.ts`

3. **validator.ts** (4.3 KB)
   - Validação de entidades extraídas
   - Lógica de completude de dados
   - Substituído por: `StateTracker` + `PolicyManager` (TOD)

### `/skills/` - Habilidades V1
4. **extractor.ts** (4.3 KB)
   - Classe `ExtractorService`
   - Extração de entidades com LLM
   - Substituído por: `NLUExtractor` (TOD)

5. **summarizer.ts** (2.5 KB)
   - Sumarização de conversas
   - Não utilizado em produção
   - Sem substituto direto (funcionalidade removida)

**Total Arquivado:** ~18 KB de código

---

## 🔄 Migração para TOD V2

### Arquitetura Antiga (V1)
```
User Message
    ↓
ExtractorService (LLM)
    ↓
Validator
    ↓
AgentEngine
    ↓
Response
```

### Nova Arquitetura (TOD V2)
```
User Message
    ↓
NLU Extractor (LLM + Variations)
    ↓
State Tracker (Redis + Merge Determinístico)
    ↓
Policy Manager (Regras Determinísticas)
    ↓
NLG Generator (LLM + Templates)
    ↓
Response
```

---

## ✅ Melhorias do TOD V2

1. **Contexto Mantido:** Redis + `conversationId`
2. **Loops Prevenidos:** Contador de tentativas (max 3)
3. **Variações Aceitas:** Mapa de 40+ termos (CC → Casa Civil)
4. **Frustração Detectada:** 8 padrões regex
5. **Confirmação Rigorosa:** Validação yes/no/unclear

---

## 📚 Documentação TOD V2

**Localização:** `/src/tod/`

**Documentos:**
- `walkthrough.md` - Implementação das 5 fases
- `plano_correcao_bugs_tod.md` - Correções aplicadas
- `conclusao_final_sessao.md` - Relatório completo

**Arquivos Principais:**
- `conversational_agent.ts` - Orquestrador
- `nlu_extractor.ts` - NLU
- `state_tracker.ts` - Estado
- `policy_manager.ts` - Decisões
- `response_generator.ts` - NLG
- `variations.ts` - Normalizações

---

## 🚫 Por Que Foi Arquivado?

### Problemas do V1
1. ❌ Sem contexto entre mensagens
2. ❌ Loops infinitos em slots difíceis
3. ❌ Não aceita variações linguísticas
4. ❌ Sem detecção de frustração
5. ❌ Confirmação fraca (cria tickets incorretos)

### Soluções do V2
1. ✅ Contexto mantido via Redis
2. ✅ Max 3 tentativas, depois aceita valor bruto
3. ✅ Mapa de variações (normalização automática)
4. ✅ Detecção de padrões de confusão
5. ✅ Validação estrita de confirmação

---

## 🔧 Como Reativar (Se Necessário)

> **AVISO:** Não recomendado! V2 é superior em todos os aspectos.

1. Mover arquivos de volta para `/src/`
2. Descomentar imports em `index.ts`
3. Mudar `ENABLE_TOD_ARCHITECTURE = false` em `tod_config.ts`
4. Rebuild do backend

---

## 📊 Métricas Comparativas

| Métrica | V1 | V2 (TOD) |
|---------|-----|----------|
| Taxa de sucesso | ~50% | ~90% |
| Turnos médios | 3-4 | 3-5 |
| Loops infinitos | Sim (comum) | Não (max 3 tentativas) |
| Variações aceitas | Não | Sim (40+) |
| Frustração detectada | Não | Sim (8 padrões) |
| Contexto mantido | Não | Sim (Redis) |

---

## 📅 Histórico

- **Desenvolvimento V1:** Set-Nov 2025
- **Problemas identificados:** Dez 2025 (4 testes)
- **Implementação V2:** Dez 22, 2025 (5 fases, 2h sessão)
- **Arquivamento V1:** Dez 22, 2025 02:18

---

## 👥 Contato

Para dúvidas sobre código arquivado ou migração:
- Ver documentação TOD em `/src/tod/`
- Relatórios em `.gemini/antigravity/brain/`

**Arquivado, NÃO deletado** - Recuperação possível se necessário
