# Definição de Regras de Classificação - Agente GLPI

## 1. Análise do Estado Atual

### 1.1 Mapeamento de Categorias
Baseado na análise do dataset de validação e do contexto atual, o sistema possui uma taxonomia híbrida e, em alguns pontos, redundante.

*   **Total de Categorias Identificadas no Dataset:** 47 categorias distintas.
*   **Profundidade:** Varia de 1 a 3 níveis (ex: `PROA` vs `DTIC > EQUIPAMENTOS > CONFIGURAÇÃO`).
*   **Categorias de Alta Frequência:**
    *   `DTIC > EQUIPAMENTOS > CONFIGURAÇÃO` (5%)
    *   `DTIC > OUTROS` (5%)
    *   `PROA` (5%)

### 1.2 Padrões de Inconsistência Detectados
A análise revelou sobreposições significativas que dificultam a classificação automática precisa:

1.  **Redundância Semântica:**
    *   `WIFI` (Nível 1) vs `DTIC > WI-FI` (Nível 2) vs `Rede e Internet > Internet / WiFi`.
    *   `OUTROS` vs `DTIC > OUTROS` vs `Outros` (case sensitivity).
    *   `OFFICE 365` vs `EMAIL` vs `Email`.

2.  **Categorias Genéricas:**
    *   Uso excessivo de `OUTROS` e `DTIC` como "gavetas de bagunça", o que reduz a utilidade da classificação para relatórios.

3.  **Mistura de Escopo:**
    *   Algumas categorias descrevem o *objeto* (`IMPRESSORA`), outras a *ação* (`TROCA DE TONNER`), e outras o *departamento* (`DTIC`).

---

## 2. Definição de Requisitos para o Agente

### 2.1 Critérios de Classificação
O agente deve seguir a seguinte ordem de prioridade para decisão:

1.  **Correspondência Exata de Contexto (Léxica):** Se o ticket contiver palavras-chave fortes definidas em `category_context.json` (ex: "toner" -> `TROCA DE TONNER`).
2.  **Similaridade Semântica (Embeddings):** Uso do modelo `intfloat/multilingual-e5-large` para calcular proximidade vetorial entre o texto do ticket e a descrição da categoria.

### 2.2 Parâmetros de Decisão (Thresholds)
Os valores definidos no `.env` controlam a autonomia do agente:

*   **Confiança Alta (`AUTO_CONFIRM_THRESHOLD` >= 0.90):** Agente altera a categoria automaticamente e notifica.
*   **Confiança Média (0.75 - 0.89):** Agente sugere a categoria em nota privada (follow-up) mas não altera.
*   **Confiança Baixa (< 0.75):** Agente não realiza ação ou marca como `Triagem Manual`.
*   **Margem de Discrepância (`DISCREPANCY_ACT` >= 0.10):** Só alterar se a nova categoria for significativamente melhor que a atual.

### 2.3 Limites de Ação
*   **Nunca** fechar tickets automaticamente.
*   **Nunca** alterar tickets já atribuídos a um técnico (status != New), exceto se configurado explicitamente.
*   **Sempre** logar a justificativa da mudança (score de confiança + termo chave).

---

## 3. Estudo de Melhorias (Propostas)

### 3.1 Consolidação de Categorias
Recomenda-se unificar categorias redundantes para simplificar o trabalho do agente e dos técnicos:

| Categoria Atual (Exemplos) | Nova Categoria Proposta |
| :--- | :--- |
| `WIFI`, `DTIC > WI-FI`, `Rede e Internet` | `INFRAESTRUTURA > REDE E INTERNET` |
| `OUTROS`, `DTIC > OUTROS` | `SUPORTE GERAL > OUTROS` |
| `TROCA DE TONNER`, `IMPRESSORA` | `EQUIPAMENTOS > IMPRESSÃO` |

### 3.2 Métricas de Sucesso
*   **Acurácia Top-1:** % de vezes que a categoria correta é a primeira sugestão. Meta: > 85%.
*   **Taxa de Rejeição:** % de tickets reclassificados pelo agente que humanos revertem. Meta: < 5%.
*   **Cobertura:** % de tickets onde o agente tem confiança suficiente para atuar. Meta: > 60%.

---

## 4. Documentação das Regras (Lógica Técnica)

### 4.1 Fluxo de Processamento
1.  **Ingestão:** Recebe ID, Título e Descrição.
2.  **Pré-processamento:** Concatena Título + Descrição, remove HTML, normaliza texto.
3.  **Inferência:** Gera embedding do texto limpo usando modelo local.
4.  **Ranking:** Calcula similaridade cosseno contra embeddings das categorias (carregados na inicialização).
5.  **Pós-processamento:** Aplica regras de negócio e verifica thresholds.
6.  **Ação:** Executa update via API ou loga sugestão.

### 4.2 Casos de Borda
*   **Tickets Vazios:** Se descrição < 10 caracteres, ignorar.
*   **Múltiplos Assuntos:** Se o ticket menciona "impressora" e "wifi", o agente prioriza pela maior similaridade semântica ou marca para triagem.
*   **Língua:** O modelo é multilingue, mas deve-se monitorar tickets em inglês/espanhol se houver.

---

## 5. Validação e Manutenção

### 5.1 Teste de Conceito (PoC)
Antes de ativar em produção (escrita), executar o modo `SANDBOX=true` por 1 semana:
*   O agente lê tickets novos.
*   Registra no log "Eu teria mudado para X com confiança Y".
*   Comparamos com a classificação final dada pelo técnico.

### 5.2 Critérios de Aceite
*   O agente não deve gerar erros de API (500/400) em mais de 0.1% das requisições.
*   O tempo de processamento por ticket deve ser < 2 segundos (com GPU).

### 5.3 Revisão Periódica
*   Mensalmente, rodar `scripts/analysis/analyze_tickets.py` para ver novas categorias criadas no GLPI e atualizar o `category_context.json`.
