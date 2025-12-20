# documentation_standards.md

> **ID:** DOC-STD-001
> **Status:** Approved
> **Responsável:** Governance Team
> **Última Atualização:** 2025-12-19

## 1. Convenções de Nomenclatura
A desorganização anterior ("Consolidado Descritivo de Tudo que.txt") é proibida.
*   **Formato Obrigatório:** `snake_case` (letras minúsculas + sublinhados).
*   **Extensão:** Sempre `.md`.
*   **Estrutura:** `[id]_[tópico_descritivo].md` (quando aplicável).
    *   Exemplo: `01_business_rules.md`, `02_operational_constraints.md`.

## 2. Estrutura Interna (Frontmatter)
Todo documento deve começar com o bloco de metadados:
```markdown
# [Título Principal do Documento]

> **ID:** [Código único, ex: DOC-001]
> **Status:** [Draft | Review | Approved | Deprecated]
> **Responsável:** [Cargo ou Time]
> **Última Atualização:** [YYYY-MM-DD]
```

## 3. Versionamento Semântico
*   **Major (1.0, 2.0):** Mudanças estruturais ou de regras de negócio (requer aprovação formal).
*   **Minor (1.1, 1.2):** Correções, clareza, formatação (aprovação técnica).

## 4. Glossário Obrigatório
Não inventar termos. Consultar `99_glossary.md`.
*   Usar "Incidente" e não "Problema".
*   Usar "Requisição" e não "Pedido".
*   Usar "Handover" e não "Transferência".
