# Auditoria Técnica e Arquitetural: Local Triage Agent

**Data:** 17 de Dezembro de 2025
**Escopo:** `agents/local_triage/` (Código Atual)
**Objetivo:** Identificar violações de boas práticas modernas (State-Driven, Semantic Validation, etc.) e riscos de estabilidade.

---

## 1. Visão Geral das Violações
A auditoria revelou que, embora o código esteja limpo e modular (LangGraph), a **lógica interna dos nós** ainda opera sob paradigmas legados (*Chat-Driven*), criando os conflitos observados nos testes.

| Categoria | Status Atual | Boas Práticas (Target) | Gravidade |
| :--- | :--- | :--- | :--- |
| **Memória** | Mista (Slice Arbitrário vs Acumulação Infinita) | Context Pinning + State Store | 🔴 Crítica |
| **Fluxo** | Probabilístico (LLM decide "READY") | Determinístico (Regra de Estado) | 🔴 Crítica |
| **Extração** | Implícita (Prompt Chat) | Explícita (LLM-as-Parser/Pydantic) | 🟠 Alta |
| **Validação** | Nula ou Textual ("Não seja perfeccionista") | Semântica (Embeddings/Judge) | 🟠 Alta |

---

## 2. Análise Detalhada por Arquivo

### 2.1 `agents/local_triage/smart_inquiry_node.py`
**Responsabilidade:** Cérebro da conversação, extração de dados e decisão de término.

*   **Violação 1: Amnésia Programada (Anti-Pattern)**
    *   *Código:* `history_text = "\n".join([f"{m.type.upper()}: {m.content}" for m in messages[-10:]])`
    *   *Problema:* Hardcoded slice `[-10:]`. Em conversas longas (loops de validação), a mensagem inicial do usuário (e a intenção original) desaparece do prompt.
    *   *Conflito:* Viola **Context Pinning**. O agente esquece o que está resolvendo.
    *   *Sintoma:* Context Loss ("Efeito Goldfish") observada nos testes.

*   **Violação 2: Flow Logic Probabilística**
    *   *Código:* Prompt instrui: *"Analise. Responda 'READY' (se pronto)..."*
    *   *Problema:* Delega ao LLM a decisão de encerrar o fluxo. Se o modelo "alucinar" uma dúvida, ele nunca emite "READY".
    *   *Conflito:* Viola **Deterministic Closure**. O estado de completude deve ser calculado (`Set(Required) - Set(Collected) == Empty`), não "sentido" pelo LLM.
    *   *Sintoma:* Loops infinitos ("Perfeccionista").

*   **Violação 3: Validação "Patchwork"**
    *   *Código:* `"IMPORTANTE: Se o usuário deu QUALQUER resposta... considere o campo PREECHIDO. Não seja perfeccionista."`
    *   *Problema:* Tentativa de corrigir a rigidez via prompt negativo (instruction tuning fraco). Não há validação real do dado.
    *   *Conflito:* Viola **Semantic Validation**. O sistema aceita lixo ou rejeita dados válidos dependendo da "vontade" do modelo.

### 2.2 `agents/local_triage/state.py`
**Responsabilidade:** Definição da estrutura de dados (Schema).

*   **Violação: State Store Passivo**
    *   *Código:* `messages: Annotated[List[BaseMessage], operator.add]`
    *   *Problema:* A lista de mensagens cresce indefinidamente sem *management*. Enquanto o `smart_inquiry` corta os últimos 10, o estado global acumula tudo.
    *   *Risco:* **Context Overflow** em nós que usem `state['messages']` sem corte (como o `classifier_wrapper_node`).
    *   *Conflito:* Falta de mecanismo de Resumo ou Pinagem no nível do Estado.

### 2.3 `agents/local_triage/graph.py`
**Responsabilidade:** Orquestração do fluxo (Grafo).

*   **Violação: Falsa Segurança no Grafo**
    *   *Código:* `if state.get("ready_to_classify", False): return "classifier"`
    *   *Problema:* A transição é técnica, mas o gatilho (`ready_to_classify`) é setado pelo nó probabilístico (`smart_inquiry`). O grafo é determinístico, mas a *condição de borda* é "vibe-based".
    *   *Conflito:* Arquitetura Híbrida instável. O grafo obedece a um componente não confiável.

### 2.4 `agents/local_triage/classifier_wrapper_node.py`
**Responsabilidade:** Classificação Final e Payload.

*   **Risco: Context Overflow**
    *   *Código:* `messages = state.get("messages", []) ... for m in messages: full_context += ...`
    *   *Problema:* Itera sobre **todas** as mensagens da história para criar o contexto de classificação.
    *   *Risco:* Diferente do `smart_inquiry` (que vê 10), este nó vê *tudo*. Se a conversa for longa (devido a loops), o prompt explodirá o limite de tokens do modelo local ou causará lentidão extrema.
    *   *Inconsistência:* O "Cérebro" (Inquiry) e o "Classificador" (Classifier) enxergam realidades diferentes da mesma conversa.

### 2.5 `agents/local_triage/intents_config.json`
**Responsabilidade:** Definição de Slots e Perguntas.

*   **Obsolescência: Definição Estática**
    *   *Estrutura:* Lista de chaves/perguntas.
    *   *Problema:* Não define **Tipos** (String, Int, Data, Enum). O LLM tenta extrair texto livre.
    *   *Conflito:* Viola **Structured Extraction (Pydantic/Zod)**. Impede validação automática (ex: garantir que `urgency` seja 1-5).

### 2.6 `agents/local_triage/viability_node.py`
**Responsabilidade:** Filtro de Entrada.

*   **Violação: NLU Frágil**
    *   *Código:* Prompt classifica como "YES/NO" baseado em exemplos textuais.
    *   *Problema:* Não usa embeddings ou similaridade. Depende da interpretação do LLM sobre o que é "vague".
    *   *Sintoma:* Falsos negativos (rejeitar tickets válidos escritos de forma simples) ou falsos positivos (aceitar "Oi" como ticket).

---

## 3. Conclusão da Auditoria
O código atual é uma implementação canônica de **"Chat-Driven State Machine"**: tenta simular uma máquina de estados usando apenas prompts de chat.

Essa abordagem foi invalidada pelo estudo arquitetural (Phase 2) por ser inerentemente instável para tarefas de triagem. A refatoração necessária não é apenas "melhorar o prompt", mas **inverter o controle**:

1.  **Do Chat para o Estado:** O Estado deve ditar as perguntas, não o LLM.
2.  **Da String para o Objeto:** A extração deve ser tipada e validada.
3.  **Do Probabilístico para o Determinístico:** O "READY" deve ser uma condição lógica, não uma alucinação textual.

Esta auditoria serve como "Sinal Verde" para a Fase de Refatoração, pois prova que o código atual *não pode* ser consertado apenas com ajustes finos; ele requer migração para os padrões identificados.
