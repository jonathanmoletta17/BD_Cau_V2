# 27 — Análise Comparativa: Documentação vs Implementação

**Data:** 19/12/2025
**Escopo:** `agents/Ticket-Agent/archive-docs` (Governança) vs `agents/Ticket-Agent/src` (Código Atual).

---

## 1. Resumo Executivo
A infraestrutura de código (`validator.ts`, `extractor.ts`, `router.ts`) é robusta e **capaz** de suportar as novas decisões de governança, pois implementa lógica de campos condicionais (`conditionalRequired`) e fallback para LLM.

No entanto, a **configuração (JSON)** e a **lógica legada (Hardcoded)** estão desatualizadas em relação aos documentos de governança recém-criados (`17_DETALHAMENTO_CREATE_USER`, `24_INSTRUCAO_ATUALIZACAO_DOCUMENTAL`).

**Status:** ⚠️ **Divergência de Configuração Crítica**

---

## 2. Detalhamento por Intenção

### 2.1. CREATE_USER
| Aspecto | Documentação (DMD v2.1) | Implementação (`src`) | Veredito |
| :--- | :--- | :--- | :--- |
| **Subtipos** | Efetivo, Estagiário. | Apenas Efetivo e Estagiário (implícito regex). | ✅ Alinhado |
| **Identificadores** | Efetivo exige `matricula` + `cpf`. | Schema e Extrator exigem apenas `cpf` para efetivos. | ❌ Divergente |
| **Lógica** | Condicional explícita. | `validator.ts` suporta, mas `schemas.json` não tem a regra. | ⚠️ Configuração |

### 2.2. EQUIPMENT_REQUEST
| Aspecto | Documentação (DMD v2.1) | Implementação (`src`) | Veredito |
| :--- | :--- | :--- | :--- |
| **Distinção** | Incidente vs Requisição (Obrigatória). | `schemas.json` possui a estrutura condicional. | ✅ Alinhado |
| **Inferência** | Keywords definem o tipo (ex: "quebrado" vs "novo"). | `inference_rules.json` possui keywords corretas. | ✅ Alinhado |
| **Zero Tech** | Proibido pedir IP/Serial. | Schema pede `item`, `description`, `reason`. Não pede dados técnicos. | ✅ Alinhado |

### 2.3. RESET_PASSWORD
| Aspecto | Documentação (DMD v2.1) | Implementação (`src`) | Veredito |
| :--- | :--- | :--- | :--- |
| **Padrão** | Assumir `Rede/Windows` se não especificado. | `schemas.json` define `defaults: { "target_system": "Rede/Windows" }`. | ✅ Alinhado |
| **Override** | Keywords (365, SAP) mudam o sistema. | `inference_rules.json` define keywords para override. | ✅ Alinhado |

---

## 3. Análise de Infraestrutura

### 3.1. Extractor (`extractor.ts`)
- **Ponto Forte:** Implementa fallback para LLM quando regras falham.
- **Risco:** Mantém um bloco "Legacy" (linhas 38-131) com Regex *hardcoded*.
    - **Exemplo:** `CREATE_USER` tem regex para CPF/RG no código. Se a regra de governança mudar (ex: aceitar passaporte), o código precisa mudar, ignorando o JSON.
    - **Recomendação:** O bloco Legacy deve ser gradualmente substituído por `inference_rules.json` ou removido em favor do LLM + Validação.

### 3.2. Validator (`validator.ts`)
- **Pontos Fortes:** Implementação perfeita de `conditionalRequired`. É agnóstico às regras, dependendo 100% de `schemas.json`.
- **Alinhamento:** Totalmente compatível com a complexidade de `CREATE_USER` e `EQUIPMENT_REQUEST`.

---

## 4. Análise de Políticas e Arquitetura

### 4.1. Políticas de Erro (`policies.json` vs `07_POLÍTICA...`)
| Aspecto | Documentação | Implementação | Veredito |
| :--- | :--- | :--- | :--- |
| **Max Retries** | 3 tentativas por campo. | `"max_retries_per_field": 3` | ✅ Alinhado |
| **Handover** | Obrigatório após falha. | `"handover_message"` definida. | ✅ Alinhado |

### 4.2. Arquitetura vs Problemas Identificados (Docs 20 e 21)
Os documentos históricos (20, 21) alertam sobre o risco de arquiteturas puramente "Chat-Driven" e recomendam "State-Driven".

- **Estado Atual (`src`):** O código adota um padrão híbrido `ConfigDriven`.
    - `RouterConfigDriven` (Determinístico 1º, LLM 2º).
    - `ExtractorConfigDriven` (Regras 1º, LLM 2º).
    - `ValidatorConfigDriven` (Determinístico puro).
- **Veredito:** O design atual MITIGA os riscos de alucinação e loop apontados nos documentos de pesquisa, pois impõe uma camada rígida de validação e roteamento antes de recorrer ao LLM.

---

## 5. O Que Falta (Gaps)

1.  **Atualizar `schemas.json` (URGENTE):**
    - Adicionar `matricula` em `required` para Efetivo.
    - Sincronizar todos os schemas com o DMD v2.1.

2.  **Atualizar `inference_rules.json`:**
    - Ajustar keywords de subtipo para alimentar o extrator.

3.  **Refatorar `extractor.ts` (Médio Prazo):**
    - O bloco `Legacy` (regex hardcoded) deve ser substituído por lógica que consuma `inference_rules.json` dinamicamente, para evitar que regras de negócio fiquem "escondidas" no código TS.

## 6. Conclusão Final
O agente possui a **capacidade técnica** (esqueleto) para atender à governança, mas está **operando com regras antigas** (cérebro).

**Ação Recomendada:** Sincronizar imediatamente os arquivos JSON de configuração para refletir os documentos de governança (`17_`, `18_`, `24_`). Nenhuma alteração drástica de código `.ts` é necessária no curto prazo.
