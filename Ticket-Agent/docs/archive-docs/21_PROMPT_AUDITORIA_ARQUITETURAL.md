# 21 — Prompt: Auditoria Arquitetural Profunda

*Este é um artefato histórico usado para orientar a fase de auditoria de código.*

---

## Papel
Atuar exclusivamente como **auditor técnico e pesquisador arquitetural**.
Foco em conformidade com boas práticas de agentes conversacionais modernos.

**NÃO Autorizado:** Implementação, refatoração, correção.

## Contexto
O diagnóstico inicial apontou falhas estruturais:
- Sliding Window ingênua.
- Arquitetura Chat-Driven inadequada.
- Ausência de State Store persistente.
- Validação rígida baseada em string.

## Escopo da Auditoria (Phase 3)
Analisar script por script (`agents/`, `graph/`, `nodes/`, `state/`) para identificar:
1. Violações de State-Driven Architecture.
2. Dependência excessiva de histórico textual.
3. Lógica probabilística onde deveria ser determinística (Flow Logic).
4. Riscos de Loop e Amnésia.

## Método
Para cada arquivo:
1. **Identificação:** Responsabilidade do arquivo.
2. **Avaliação:** Depende de texto? Mistura NLU/Flow?
3. **Confronto:** Viola padrões validados?
4. **Classificação:** Anti-pattern, Risco, Obsoleto.

## Entregável
Radiografia arquitetural completa ("O que está errado e por quê"), sem propor código de correção.
