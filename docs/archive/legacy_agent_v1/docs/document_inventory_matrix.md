# document_inventory_matrix.md

> **ID:** DOC-INV-001
> **Status:** Living Document
> **Responsável:** Researcher
> **Última Atualização:** 2025-12-19

## Inventário e Análise Forense
Este documento mapeia os artefatos legados encontrados na raiz do projeto e define seu destino na nova estrutura.

| Arquivo Original | Categoria | Valor | Risco | Ação Recomendada | Destino |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Consolidado Descritivo de Tudo que.txt` | Regra de Negócio | Alto | Baixo | **MIGRATE** | `01_business_rules.md` |
| `Local Triage Agent — Documento Narr.txt` | Contexto | Alto | Médio | **MIGRATE** | `10_functional_specification.md` |
| `PROMPT — AUDITORIA ARQUITETURAL PRO.txt` | Arquitetura | Alto | Alto | **MIGRATE** | `03_technical_architecture.md` |
| `senha de rede ela é umaa das princi.txt` | Regra Específica | Médio | Baixo | **FUNDIR** | `01_business_rules.md` (RESET_PASSWORD) |
| `sobre vpn - só concede acesso a uma.txt` | Regra Específica | Médio | Baixo | **FUNDIR** | `01_business_rules.md` (VPN_ACCESS) |
| `Esclarecimento direto HARDWARE_ISSU.txt` | Decisão | Médio | Baixo | **FUNDIR** | `01_business_rules.md` (EQUIPMENT_REQUEST) |
| `nao devemos pedir nem ip e nem patr.txt` | Constraint | Alto | Médio | **MIGRATE** | `02_operational_constraints.md` |
| `Atue exclusivamente como Analista d.txt` | Persona | Baixo | Baixo | **ARQUIVAR** | `archive/legacy_personas/` |
| `Atue exclusivamente como Documentad.txt` | Persona | Baixo | Baixo | **ARQUIVAR** | `archive/legacy_personas/` |
| `Papel.txt` | Rascunho | Baixo | Baixo | **ARQUIVAR** | `archive/trash/` |

## Legenda de Ações
*   **MIGRATE:** Conteúdo vital. Rescrever formatado no novo padrão.
*   **FUNDIR:** Pequeno fragmento de verdade. Incorporar em documento maior.
*   **ARQUIVAR:** Obsoleto ou redundante. Mover para pasta de legado.
*   **CONSULTAR:** Manter como referência histórica, mas não oficial.
