# 23 — Modo de Operação: Refatoração Incremental

## Objetivo
Refatoração Incremental Controlada.

## Restrições
A partir deste ponto, você **NÃO** deve:
- Refatorar o sistema completo.
- Antecipar correções futuras.
- Alterar múltiplos invariantes ao mesmo tempo.

## Metodologia
Trabalhar por **micro-fases**, cada uma focada em **UM única problema arquitetural**.

### Fase Atual (Exemplo)
**Objetivo Único:** [ex: Eliminar Context Loss]

**Escopo Permitido:** Apenas arquivos/componentes relevantes para este problema.

**Tarefas Obrigatórias:**
1. Reanalisar apenas o código do escopo.
2. Explicar onde a regra é violada e por quê.
3. Propor a **menor correção possível**.
4. Mostrar impacto e critérios de validação.

**Regra de Ouro:**
> **Não implemente ainda.** Aguarde aprovação explícita.
