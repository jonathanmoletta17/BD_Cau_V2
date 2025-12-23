# Estudo de Fundação Arquitetural: Diagnóstico e Evolução para Agentes Conversacionais

**Data:** 17 de Dezembro de 2025
**Contexto:** Investigação das falhas observadas na simulação do "Local Triage Agent" (Taxa de sucesso de 0%).
**Objetivo:** Estabelecer uma base teórica sólida sobre Sistemas de Memória, Arquiteturas Orientada a Estado e Validação Semântica para guiar a refatoração do agente.

---

## 1. O Problema da Memória: "Amnésia do Agente"
A falha mais crítica observada foi o "Efeito Goldfish", onde o agente esquecia informações fornecidas no início da conversa (ex: nome do usuário, sistema afetado).

### 1.1 Diagnóstico Técnico: Janela Deslizante Ingênua
O agente atual utiliza uma implementação ingênua de "Janela Deslizante" (`messages[-10:]`).
*   **Mecanismo:** A cada nova interação, as mensgens mais antigas são descartadas estritamente por contagem.
*   **Consequência:** Em interações verbosas ou com múltiplas trocas de validação, a mensagem inicial (que contém o contexto vital e a intenção original) desliza para fora da janela de contexto do LLM.
*   **Resultado:** O LLM perde o acesso à "Semente da Conversa". Ele sabe *que* deve responder, mas não sabe mais *sobre o que* ou *quem* é o usuário.

### 1.2 Soluções Arquiteturais: Context Pinning & Memória Híbrida
A literatura e práticas de engenharia de prompt modernas sugerem abandonar a janela deslizante pura em favor de estratégias de retenção seletiva.

#### Estratégia A: Context Pinning (Pinagem de Contexto)
Em vez de tratar todas as mensagens como iguais, certas mensagens são marcadas como "Imutáveis" ou "Fixas" no prompt.
*   **System Message:** Sempre presente (já implementado).
*   **Messagem Inicial (User Request):** Deve ser "pinada". Mesmo que a conversa tenha 50 turnos, a primeira mensagem do usuário deve ser injetada no contexto logo após o System Prompt.
*   **Implementação:** `Context = [SystemPrompt] + [User_Message_0] + [Sliding_Window_Recent_N]`

#### Estratégia B: Memória de Estado (State-Store)
Mover a responsabilidade de "lembrar" do *chat history* (texto não estruturado) para o *State Schema* (dados estruturados).
*   **Conceito:** Se o usuário diz "Meu nome é Carlos", o agente deve extrair `user_name="Carlos"` e salvar isso no objeto de estado.
*   **Benefício:** O histórico de chat pode ser apagado, mas o *conhecimento* persiste no objeto de estado, que é reinjetado a cada turno.

---

## 2. O Problema do Controle: Chat-Driven vs. State-Driven
O agente exibiu comportamento de "Looping" e hesitação, falhando em avançar para a criação do ticket mesmo com dados suficientes.

### 2.1 Chat-Driven (Atual)
*   **Lógica:** O fluxo é determinado implicitamente pelo LLM a cada turno, baseado apenas no histórico de texto.
*   **Falha:** O LLM é probabilístico. Se o prompt pede "confirme todos os dados", o LLM pode entrar em um loop de confirmação infinita se não houver um "gatilho" explícito de transição de estado. Ele tende a ser "educado demais" ou "cauteloso demais".
*   **Vulnerabilidade:** Suscetível a *drifting* (perda de foco) e alucinação de requisitos (pedir dados que não são estritamente necessários).

### 2.2 State-Driven (Recomendado - LangGraph Moderno)
*   **Lógica:** O fluxo é determinado por uma Máquina de Estados Finita (FSM) ou Grafo de Estados.
*   **Slot Filling Explícito:** O agente não "conversa para ver se descobre algo". Ele entra em um estado `Coletando_Dados`.
*   **Transição Determinística:**
    *   `Estado`: Coletando_Dados
    *   `Entrada`: Usuário fornece a última peça que faltava.
    *   `Regra`: Se `Completeness_Check` == True -> Transição para `Confirmacao`.
*   **Benefício:** Elimina loops. O agente *sabe* que terminou a coleta porque a regra lógica (não o LLM) disse que sim. O LLM é usado apenas para extrair a informação (NLU) e gerar a resposta (NLG), não para controlar o fluxo (Flow Logic).

---

## 3. O Problema da Extração: Chat Implícito vs. NER Explícito
O agente atual tenta extrair e validar dados organicamente durante a conversa, misturando "entender" com "conversar".

### 3.1 Extração com LLM (Pydantic/Structured Output)
Modelos modernos (como os usados via Ollama/LangChain) suportam *Structured Outputs*.
*   **Padrão:** Em vez de pedir ao LLM "Responda ao usuário perguntando o patrimônio", deve-se usar um nó de extração silencioso.
*   **Fluxo Ideal:**
    1.  Usuário envia mensagem.
    2.  **Nó Extrator (Silencioso):** Analisa a mensagem e tenta preencher o schema JSON (NER). Não gera texto para o usuário.
    3.  **Atualização de Estado:** O JSON extraído atualiza o `AgentState`.
    4.  **Nó Decisor:** Verifica o estao. Faltam campos? -> Manda para Nó de Pergunta. Estão completos? -> Manda para Nó de Criação.

Isso desacopla a "memória dos fatos" da "memória da conversa".

---

## 4. O Problema da Validação: Rigidez vs. Semântica
O agente rejeitou entradas válidas (ex: usuário diz "quebrado", agente quer "defeito físico") gerando frustração.

### 4.1 Validação Rígida (String Matching)
A abordagem atual tenta comparar strings ou espera que o usuário use a terminologia exata do JSON de configuração.

### 4.2 Validação Semântica (Fuzzy & Embedding)
*   **Validação via LLM ("Judge"):** Usar uma chamada leve de LLM para validar a entrada.
    *   *Prompt:* "O usuário disse 'tela trincada'. Isso se qualifica como 'Hardware Defect' para o campo 'Problema'? Responda Sim/Não."
*   **Validação via Embeddings:**
    *   Calcular vetor de "tela trincada".
    *   Calcular vetor de "Hardware Defect".
    *   Se Similaridade(A, B) > 0.8 -> Aceitar.
*   **Aplicação:** Permite que o agente seja flexível ("vibe coding") na interface com o usuário, mas rígido ("structured data") na interface com o sistema (GLPI).

---

## 5. Roadmap de Evolução Arquitetural (Próximos Passos Recomendados)

Com base nesta pesquisa, a refatoração do Agente de Triagem Local deve seguir esta ordem de prioridade para eliminar as falhas de raiz:

1.  **Migração para State-Driven:**
    *   Redefinir o grafo (Graph.py) para que as transições sejam baseadas na *completude do estado* e não na decisão do LLM de conversa.
    *   Implementar `Structured Output` para a extração de dados.

2.  **Implementação de Contexto Híbrido:**
    *   Modificar a construção do prompt (`history_text`) para garantir que a mensagem #0 (Request Inicial) nunca seja truncada.
    *   Injetar o `Resumo do Estado Atual` (campos já coletados) no System Prompt a cada turno como memória de trabalho fixa.

3.  **Validador Semântico:**
    *   Substituir verificações de string exata por validação lógica via LLM (node "Judge" ou "Critic") para evitar loops de rejeição.

Esta fundação teórica explica *por que* o agente atual falha (exaustão de contexto, falta de determinismo no fluxo) e *como* a arquitetura deve evoluir para ser robusta, auditável e eficiente.
