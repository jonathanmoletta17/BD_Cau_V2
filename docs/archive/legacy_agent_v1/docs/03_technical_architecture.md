# 03_technical_architecture.md

> **ID:** DOC-003
> **Status:** Draft
> **Responsável:** Arquiteto de Software
> **Última Atualização:** 2025-12-19

## 1. Contexto e Objetivo
Este documento define a arquitetura técnica obrigatória para o Local Triage Agent (LTA). Baseado na auditoria de falhas anteriores (loops infinitos, amnésia), este modelo impõe uma mudança de paradigma de **Chat-Driven** (o LLM decide o fluxo) para **State-Driven** (o Código decide o fluxo).

## 2. Princípios Arquiteturais

### A. State-Driven vs Chat-Driven
*   **Antigo (Proibido):** O histórico do chat (`user: x, bot: y`) é a única fonte de verdade. O LLM decide o próximo passo com base na leitura do chat.
*   **Novo (Obrigatório):** Uma **State Store** (objeto JSON estruturado) é a única fonte de verdade. O Código decide o próximo passo com base no preenchimento dos campos do State Store. O Chat é apenas a interface de I/O.

### B. Silent Extraction (Extração Silenciosa)
O Agente não deve perguntar e depois esperar a resposta na próxima rodada.
*   **Padrão:** Em CADA turno, o Extrator lê **TODO** o histórico da conversa e tenta preencher os campos vazios do State Store.
*   **Benefício:** Se o usuário já informou o dado 3 mensagens atrás, o Extrator o captura, o State fica "Completo", e o Router avança sem perguntar novamente. Isso elimina a "Amnésia".

### C. Validação Semântica
*   Não usar Regex rígido. Não usar "contém a palavra X".
*   Usar o LLM como validador booleano:
    *   *Input:* "O monitor piscou e desligou" -> *Campo:* Descrição do Problema.
    *   *Validação:* "O texto descreve um sintoma técnico?" -> SIM.

## 3. Máquina de Estados Finita (FSM)
O fluxo deve ser modelado como um grafo direcionado (ex: LangGraph).

1.  **START**
2.  **EXTRACT** (Atualiza State com histórico)
3.  **ROUTER** (Decisão Determinística):
    *   Se `Intent` == NULL -> **CLASSIFY**
    *   Se `Intent` != NULL E `Missing_Fields` > 0 -> **QUESTION**
    *   Se `Intent` != NULL E `Missing_Fields` == 0 -> **ACTION**
    *   Se `Attempts` > 3 -> **HANDOVER** (Transbordo)

## 4. Persistência e Limites
*   **State Store:** Deve persistir `attempt_count` para cada campo.
*   **Regra de 3 Strikes:** Se o `attempt_count` de um campo chegar a 3, o sistema aborta a coleta automática e transfere para humano (Handover). O sistema NÃO deve tentar uma 4ª vez.

## 5. Integração
*   A lógica de conversação deve ser **desacoplada** da integração GLPI.
*   O Agente produz um JSON estruturado final (`Structured Output`). Um serviço externo (`GLPI Sync`) consome esse JSON e abre o ticket. O Agente não chama API do GLPI diretamente durante a conversa (para evitar latência e erros de rede na UX).
