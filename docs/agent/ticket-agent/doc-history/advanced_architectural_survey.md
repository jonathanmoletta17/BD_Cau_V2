# Levantamento Arquitetural Avançado: Diagnóstico e Validação de Agentes Conversacionais

**Data:** 17 de Dezembro de 2025
**Objetivo:** Fundamentar tecnicamente as falhas do *Local Triage Agent* e mapear soluções baseadas no estado da arte.
**Ciclo:** Deep Research - Phase 2 (Validation)

---

## 1. Sistemas de Memória em Agentes Conversacionais Modernos

**Diagnóstico Atual:** O agente sofre de "Amnésia" (Context Loss) devido ao uso ingênuo de uma Janela Deslizante (`messages[-10:]`), onde a mensagem inicial do usuário é descartada, removendo o contexto vital da intenção original.

### 1.1 Mapeamento de Tipos de Memória
A indústria classifica a memória de agentes em níveis distintos, superando a simples "história do chat":

| Tipo | Função | Implementação Comum | Status no Agente |
| :--- | :--- | :--- | :--- |
| **Context Window (Working Memory)** | Memória de curto prazo imediata (atenção ativa). Limitada por tokens. | Prompt direto ao LLM. | **Única implementada (e falha)**. |
| **Short-Term Memory (Session)** | Mantém o contexto da sessão atual (fio da meada), resolvendo pronomes ("ele", "isso"). | `ConversationSummaryBufferMemory` (LangChain), Checkpointers (LangGraph). | Implícita e volátil. |
| **Long-Term Memory (Episodic/Semantic)** | Retém fatos, preferências e aprendizados entre sessões. | Vector Stores (RAG), Bancos de Dados Relacionais, Knowledge Graphs. | Inexistente. |

### 1.2 Estratégias de Preservação de Contexto (Anti-Amnésia)
Pesquisas em frameworks como **LangChain** e **Rasa** revelam padrões para evitar a perda da "Mensagem Semente":

*   **Context Pinning (Pinagem):** Em vez de deslizar *todas* as mensagens, o sistema "pina" (fixa) mensagens críticas no início do prompt.
    *   *Padrão:* `[System Prompt] + [Pinned: User Original Request] + [Summarized History] + [Last N Messages]`
    *   *Por que funciona:* Garante que a intenção original (`User Request`) nunca saia da janela de atenção, mesmo após 50 turnos de validação.
*   **Recursive Summarization:** Conforme o histórico cresce, o sistema gera resumos progressivos das mensagens intermediárias, mantendo os fatos mas descartando o texto "verborrágico".
*   **Entity-Aware Memory:** O sistema extrai entidades (`nome`, `problema`, `patrimônio`) e as armazena em um objeto de estado separado (`State Store`). O prompt recebe esse objeto a cada turno, não dependendo de "lembrar" onde a informação foi citada no texto.

**Conclusão 1:** A dependência exclusiva de `messages[-10:]` é um anti-pattern conhecido para fluxos transacionais. A solução validada é migrar para **State-Store + Context Pinning**.

---

## 2. Arquiteturas State-Driven vs Chat-Driven

**Diagnóstico Atual:** O agente opera em modo *Chat-Driven*, onde o fluxo é determinado probabilisticamente pelo LLM a cada turno. Isso causa "Looping" e "Hesitação", pois o modelo não tem um sinal determinístico de "Fim de Tarefa".

### 2.1 Comparativo Arquitetural

| Característica | Chat-Driven (Atual) | State-Driven (Recomendado - LangGraph/Rasa) |
| :--- | :--- | :--- |
| **Controle de Fluxo** | Probabilístico (LLM decide o próximo passo). | Determinístico (Máquina de Estados/Grafo). |
| **Transição** | Implícita ("Acho que acabei"). | Explícita (`if completeness_check() == True then transition`). |
| **Resiliência** | Baixa (suscetível a prompts do usuário e loops). | Alta (segue regras rígidas de negócio). |
| **Caso de Uso Ideal** | Chatbot de bate-papo, FAQ aberto. | Triagem técnica, Coleta de dados, Processos de suporte. |

### 2.2 Padrões de Mercado
*   **Rasa Forms:** Utiliza "Slots" e "Forms" explícitos. O agente entra em um *loop de formulário* onde a única prioridade é preencher slots faltantes. O LLM não "decide" se deve perguntar; o framework obriga a pergunta até que o slot seja preenchido.
*   **LangGraph:** Permite definir fluxos como grafos direcionados. Um nó `CollectInfo` pode ciclar sobre si mesmo até que o estado satisfaça uma condição de borda (`conditional_edge`), momento em que a transição para `CreateTicket` é forçada, independente da "vontade" do LLM de continuar conversando.

**Conclusão 2:** Para processos de triagem (onde o objetivo é preencher um ticket), a arquitetura *State-Driven* é superior. O LLM deve ser usado apenas para NLU (entender o texto) e NLG (gerar a resposta), mas nunca para Flow Logic (decidir o próximo passo).

---

## 3. Extração Estruturada e Persistência (Slot Filling)

**Diagnóstico Atual:** O agente mistura "conversar" com "extrair". Ele tenta pescar informações no meio de um texto livre, muitas vezes alucinando que precisa de mais detalhes.

### 3.1 Padrões de Extração (Structured Output)
A evolução do NER (Named Entity Recognition) clássico para LLMs trouxe o padrão de **LLM-as-Parser**:

*   **Silent Extraction Pattern:**
    *   O usuário envia: "Meu PC quebrou".
    *   O sistema roda um LLM "silencioso" (sem gerar chat) com um schema Pydantic/JSON estrito: `extract_entities(text) -> {equipment: "PC", problem: "quebrou"}`.
    *   O sistema atualiza o Estado Persistente com esses dados.
    *   *Só depois* o nó de conversação é ativado para verificar o que falta.

*   **Ferramentas:**
    *   **Pydantic / Zod:** Indispensáveis para garantir que o output do LLM respeite tipos (ex: `priority` deve ser `int`, não `string "alta"`).
    *   **LangChain `with_structured_output`:** Força o modelo a responder APENAS o JSON, eliminando "preâmbulos" ou tentativas de conversa.

**Conclusão 3:** Separar a *Cognição de Extração* da *Cognição de Conversação* elimina o "Looping". O agente para de perguntar o nome porque o campo `name` no estado já está preenchido e validado.

---

## 4. Validação Semântica (Fuzzy & Judge)

**Diagnóstico Atual:** Rigidez. O usuário diz "tá pifado", o sistema rejeita porque espera "Defeito de Hardware". Isso gera frustração e loops de correção.

### 4.1 Abordagens de Validação Flexível
*   **Embeddings (Proximidade Vetorial):** Transformar input do usuário e categorias válidas em vetores. Se `CosineSimilarity("pifado", "Defeito Hardware") > 0.8`, aceitar automaticamente.
*   **LLM-as-a-Judge:** Utilizar um prompt leve para julgar a equivalência.
    *   *Prompt:* "Neste contexto de TI, a frase '{user_input}' pode ser mapeada para a categoria '{target_category}'? Responda Sim/Não."
*   **Fuzzy Matching (Nível Básico):** Algoritmos como Levenshtein para tolerar typos (ex: "Noteebok" -> "Notebook").

**Conclusão 4:** A validação deve ser semântica (baseada em significado), não sintática (baseada em texto exato). Isso humaniza a interface e reduz a fricção.

---

## 5. Design Pattern Antilooping: Closure Determinístico

**Diagnóstico Atual:** O agente sofre de "Perfeccionismo". Ele tem todos os dados, mas pergunta "Tem certeza?", "Mais algum detalhe?", entrando em loop.

### 5.1 O Padrão "Closure by State"
Agentes não devem "sentir" que acabaram; eles devem "calcular" que acabaram.

*   **Checklist de Completude:**
    *   Definir explicitamente: `Required_Slots = [Name, Problem, Location]`.
    *   A cada turno, calcular: `Missing = Required - Current_State`.
    *   Se `Missing` vazio -> Disparar Evento `READY`.
*   **Anti-Pattern:** Perguntar "Posso prosseguir?". Isso abre espaço para o usuário (ou o próprio agente) introduzir dúvidas.
*   **Pattern "Assumed Closure":** "Entendi. Tenho tudo que preciso (Nome: X, Problema: Y). Criando ticket..." -> Ação direta, informando o usuário, sem pedir permissão redundante.

---

## Resumo Final e Próximos Passos

Este levantamento valida que as falhas do *Local Triage Agent* são **estruturais e esperadas** dado o design atual (*Chat-Driven*, *Sliding Window*, *String Validation*).

A solução não reside em "ajustar o prompt", mas em uma evolução arquitetural para:
1.  **State-Driven (Graph):** Controle de fluxo determinístico.
2.  **State-Store Memory:** Persistência de dados estruturada, independente do chat.
3.  **Silent Extraction:** Pipelines dedicados de NLU.
4.  **Semantic Validation:** Tolerância e inteligência na interpretação.

O caminho para a refatoração está tecnicamente validado e documentado.
