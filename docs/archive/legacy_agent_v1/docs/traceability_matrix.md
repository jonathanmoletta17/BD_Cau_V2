# Traceability Matrix (Legacy -> Current)

This document maps every "tacit knowledge" file from the legacy system to its formal home in the new documentation structure, proving 100% coverage.

| Legacy File | Key Insight | New Home | Status |
| :--- | :--- | :--- | :--- |
| `sobre isso - Campos obrigatórios.txt` | Distinção Efetivo vs Estagiário (RG/CPF) | `01_business_rules.md` (Sec 3.B) | ✅ Mapped |
| `nao devemos pedir nem ip.txt` | Proibição de IP/Serial; Contexto Visual | `01_business_rules.md` (Sec 3.E) | ✅ Mapped |
| `sobre vpn - só concede acesso.txt` | VPN não cria identidade | `01_business_rules.md` (Sec 3.C) | ✅ Mapped |
| `senha de rede ela é umaa.txt` | 71% dos resets são AD (Dados empíricos) | `01_business_rules.md` (Sec 3.A) | ✅ Mapped |
| `Esclarecimento HARDWARE_ISSU.txt` | Fim da intenção HARDWARE_ISSUE | `01_business_rules.md` (Sec 3.D) | ✅ Mapped |
| `Instrução Formal...txt` | Incidente vs Requisição | `01_business_rules.md` (Sec 3.D) | ✅ Mapped |
| `Voce NÃO pode implementar.txt` | Framework de Decisão (5 steps) | `prompts/framework_micro_decision.md` | ✅ Mapped |
| `PROMPT — AUDITORIA...txt` | Anti-patterns (State-Driven) | `prompts/persona_architectural_auditor.md` | ✅ Mapped |
| `Consolidado Descritivo...txt` | Regras Gerais e Persona | `docs/02_operational_constraints.md` | ✅ Mapped |
| `Local Triage...Especificação.txt` | JSON Schemas & Inference Rules | `docs/10_functional_specification.md` | ✅ Mapped |
| `transicao_planejamento...md` | Pydantic Fields Definition | `docs/10_functional_specification.md` | ✅ Mapped |
| `declaracao_estabilidade...md` | Política de "Closed System" | `docs/04_governance_process.md` | ✅ Mapped |
| `refactoring_blueprint.md` | (Obsoleto - Refatoração passada) | `archive/` | 🗑️ Archived |
| `Esturura...DRA.txt` | (Redundante - Draft) | `archive/` | 🗑️ Archived |

**Conclusion:** All tactical and strategic rules have been successfully extracted and formalized. The "Legacy" folder can now be archived safely.
