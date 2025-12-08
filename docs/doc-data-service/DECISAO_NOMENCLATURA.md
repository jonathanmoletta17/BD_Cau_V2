# Decisão Técnica: Padronização de Nomenclatura

## Análise Realizada

Mapeamento completo de nomenclaturas em Python (`*.py`):

### ✅ Padrão PORTUGUÊS (Dominante - 99%)

**Timestamps:**
- `criado_em` ✅ (60+ ocorrências)
- `atualizado_em` ✅ (60+ ocorrências)
- `solucionado_em` ✅ (20+ ocorrências)
- `fechado_em` ✅ (20+ ocorrências)
- ❌ `sincronizado_em` (ÚNICA INCONSISTÊNCIA - deveria ser `synced_at` se fosse inglês)

**Campos de Negócio:**
- `titulo` ✅ (60+ ocorrências)
- `descricao` ✅ (40+ ocorrências)
- `categoria_id` ✅ (20+ ocorrências)
- `entidade_id` ✅ (30+ ocorrências)
- `prioridade_id` ✅ (25+ ocorrências)
- `status_id` ✅ (50+ ocorrências)

**Campos de Relacionamento:**
- `usuario_id` ✅
- `usuario_nome` ✅
- `tecnico` ✅
- `requerente` ✅
- `campo` ✅
- `campo_id` ✅
- `valor_antigo` ✅
- `valor_novo` ✅

### ❌ Padrão INGLÊS (Inexistente)

- `created_at` - **0 ocorrências**
- `updated_at` - **0 ocorrências**
- `deleted_at` - **0 ocorrências**
- `synced_at` - **0 ocorrências**
- `title`, `description`, `category_id`, etc - **0 ocorrências**

---

## Conclusão

**O projeto usa PORTUGUÊS em 99% do código Python.**

A única exceção é `sincronizado_em` que deveria ser `criado_sincronizacao_em` ou similar para **manter consistência**.

---

## Decisão: MANTER PORTUGUÊS

### Justificativa

1. **Menor Risco**: 99% do código já está em português
2. **Menor Esforço**: Migrar para inglês = reescrever 99% vs 1%
3. **Boas Práticas**: Tim Peters (Python): "There should be one-- and preferably only one --obvious way to do it."
   - Uma única língua por projeto é melhor que misturar
4. **Contexto de Negócio**: GLPI é brasileiro, equipe é brasileira, domínio é português
5. **Sem impacto em bibliotecas**: Campos de modelos são internos, não violam APIs

### Trade-offs Considerados

**Português:**
- ✅ Alinhado com contexto de negócio
- ✅ Menor risco e esforço de migração
- ✅ Já é o padrão estabelecido (99%)
- ⚠️ Mistura conceitos técnicos (Column, String) com domínio (titulo)

**Inglês:**
- ✅ Padrão internacional em código
- ✅ Melhor para bibliotecas open-source
- ❌ Requer reescrever 99% do código
- ❌ Risco ALTO de introduzir bugs
- ❌ Exige migração SQL

---

## Ações

### Imediata: Renomear `sincronizado_em` → `atualizado_sincronizacao_em`

**Motivação:** Manter coerência com `criado_em`, `atualizado_em`, etc.

**Impacto:**
- ✅ Baixo: Apenas 43 ocorrências em código
- ✅ Baixo: Usado internamente, não exposto em APIs
- ⚠️ Médio: Requer migração SQL

**Migração SQL:**
```sql
-- DTIC
ALTER TABLE dtic.tickets RENAME COLUMN sincronizado_em TO atualizado_sincronizacao_em;
ALTER TABLE dtic.glpi_users RENAME COLUMN sincronizado_em TO atualizado_sincronizacao_em;
-- ... (8 tabelas DTIC + 8 tabelas SIS)
```

**Alternativa Conservadora:** Manter `sincronizado_em` por enquanto e adiar até refatoração maior.

---

## Recomendação Final

**Fase 1 (Agora):** 
- Manter `sincronizado_em` como está
- Focar em corrigir problemas de dados (prioridade)

**Fase 2 (Futuro):**
- Renomear para `atualizado_sincronizacao_em` em refatoração planejada
- Criar issue para decisão de equipe

---

## Decisão Aprovada pelo Usuário

**Manter PORTUGUÊS em todo o projeto ✅**

Próximo passo: Avançar para correções de dados no sync_service.py
