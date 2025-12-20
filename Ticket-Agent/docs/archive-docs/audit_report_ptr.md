# Relatório de Auditoria Reversa - Protótipo Técnico (PTR)

**Referência de Conformidade:** [Documento Mestre de Decisão v2.1](documento_mestre_decisao.md)
**Status do Código:** Protótipo Técnico Não-Produção
**Data:** 18/12/2025

## 1. Resumo Executivo
O código existente (PTR) apresenta **alta aderência (aprox. 95%)** às definições do DMD v2.1. A estrutura macro (Grafo, Nós, Schemas) está correta. Foram identificados desvios pontuais de rigor normativo em `validator.py` (CREATE_USER) e resquícios textuais em `router.py`.

## 2. Auditoria por Arquivo

### 🟦 router.py
| Regra Implementada | Status | Origem DMD | Observação |
| :--- | :--- | :--- | :--- |
| Lista de Intenções (6 + Unknown/Handover) | ✅ Aderente | Seção 2 | Lista exata de 1-6. |
| Remoção de HARDWARE_ISSUE | ⚠️ Parcial | Seção 2 (Warning) | O prompt ainda cita `(NOTE: Old HARDWARE_ISSUE is now...)`. O código não usa a intent, mas o prompt "fala" dela. Deve ser removido. |
| Regra de VPN (Acesso/Justificativa) | ✅ Aderente | Seção 2 / 3.2 | Prompt força roteamento para VPN_ACCESS corretamente. |
| Output JSON Estrito | ✅ Aderente | Seção 4.3 | Implementado via ChatOllama JSON mode. |

### 🟦 extractor.py
| Regra Implementada | Status | Origem DMD | Observação |
| :--- | :--- | :--- | :--- |
| Mapeamento de Schemas | ✅ Aderente | Seção 2 | Todos os schemas mapeados corretamente. |
| Inferência de Request Type (Equipment) | ✅ Aderente | Seção 3.1 | Prompt instrui inferência de Incident vs Requisition. |
| Silence ("Do not converse") | ✅ Aderente | Seção 4.1 | Nó estrito de extração sem geração de texto. |

### 🟦 validator.py
| Regra Implementada | Status | Origem DMD | Observação |
| :--- | :--- | :--- | :--- |
| CREATE_USER: Campos Base | ✅ Aderente | Seção 3.3 | Nome, Setor, Tipo exigidos. |
| CREATE_USER: Identificador Efetivo | ❌ Desvio | Seção 3.3 | Código pede `Matrícula/CPF`. DMD v2.1 exige estritamente **CPF** para Efetivo. |
| CREATE_USER: Identificador Estagiário | ✅ Aderente | Seção 3.3 | Exige **RG**. |
| CREATE_USER: Identificador Terceiro | ⚠️ Implícito | Seção 3.3 | Cai no `else` genérico ("identifier"). Deveria validar explicitamente se é Matrícula ou Empresa. |
| EQUIPMENT: Incident vs Requisition | ✅ Aderente | Seção 3.1 | Valida `issue_description` apenas para incidentes. |
| VPN_ACCESS: Concessão | ✅ Aderente | Seção 3.2 | Exige `request_type` e `justification`. |

### 🟦 inquiry.py
| Regra Implementada | Status | Origem DMD | Observação |
| :--- | :--- | :--- | :--- |
| Anti-Amnésia (Pinned Request) | ✅ Aderente | Seção 4.2 | Usa `pinned_req` no contexto do prompt. |
| Pergunta Contextual (User ID) | ✅ Aderente | Seção 3.3 | Prompt instrui pedir CPF/RG/Matrícula conforme o caso. Alinhado ao DMD. |

### 🟦 schemas.py
| Regra Implementada | Status | Origem DMD | Observação |
| :--- | :--- | :--- | :--- |
| CreateUserSchema | ✅ Aderente | Seção 3.3 | Campos refletem a estrutura (Start Date é aceitável como opcional de identidade). |
| EquipmentRequestSchema | ✅ Aderente | Seção 3.1 | Unificado com Enum `RequestType`. |
| VpnAccessSchema | ✅ Aderente | Seção 3.2 | Enum `ACCESS_GRANT`, `INSTALL`. |
| ResetPasswordSchema | ✅ Aderente | Seção 2 | Default "Rede/Windows". |

### 🟦 graph.py
| Regra Implementada | Status | Origem DMD | Observação |
| :--- | :--- | :--- | :--- |
| Falha Segura (Unknown/Handover) | ✅ Aderente | Seção 4.4 | Roteia intents desconhecidas direto para finalizer. |
| Ciclo de Validação | ✅ Aderente | Seção 4.1 | Loop `Validator -> Inquiry -> Extractor` implícito no fluxo de conversa (via LangGraph state persistence). |

## 3. Ações Corretivas Necessárias (Pré-Implementação)

Antes de considerar o código como "Release Candidate", as seguintes correções devem ser aplicadas:

1.  **Limpeza de Prompt (router.py):** Remover a frase `(NOTE: Old HARDWARE_ISSUE is now EQUIPMENT_REQUEST)` do System Prompt. O modelo deve aprender a nova definição sem referência ao legado.
2.  **Validator Estrito (validator.py):**
    *   Alterar validação de Efetivo para exigir `CPF`.
    *   Criar validação explícita para Terceiro (`Matrícula` ou `Empresa`).
