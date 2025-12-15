# Inteligência de Dados: Análise de Ticket Changes (Audit Log)

**Data de Criação:** 12/12/2025  
**Contexto:** DTIC / GLPI V3  
**Status:** Implementado

---

## 1. Visão Geral
A tabela `ticket_changes` é o coração da auditoria e da inteligência de processos dentro do GLPI. Ela armazena o histórico completo de modificações de um chamado, permitindo reconstruir a "vida" de um ticket passo a passo.

Este documento detalha o mapeamento dos dados, as métricas derivadas implementadas e como o Agente de IA utiliza essas informações para fornecer insights avançados.

---

## 2. Mapeamento de Dados (`dtic.ticket_changes`)

| Coluna | Tipo | Descrição Semântica | Uso em IA/Análise |
| :--- | :--- | :--- | :--- |
| `id` | Int | PK Local | Indexação interna. |
| `glpi_id` | Int | ID Original (GLPI) | Rastreabilidade e links externos. |
| `ticket_id` | Int (FK) | ID do Ticket | Agrupamento de eventos (Timeline). |
| `data_mudanca` | Timestamp | Data do Evento | Cálculo de SLA real, gargalos e tempos de espera. |
| `usuario_nome` | String | Ator | Identificação de quem realizou a ação (Técnico vs Sistema vs Usuário). |
| `campo` | String | Tipo de Mudança | Variável categórica principal (`status`, `technician`, `priority`, `content`). |
| `valor_antigo` | Text | Estado Anterior | Detecção de direção (ex: Reabertura = Fechado -> Novo). |
| `valor_novo` | Text | Estado Novo | Estado atual após o evento. |

---

## 3. Métricas e Insights Implementados

A partir dos dados brutos, derivamos as seguintes métricas de inteligência ("Feature Engineering"):

### A. Linha do Tempo Humanizada (Timeline)
Reconstrução narrativa do ticket para leitura rápida por humanos e LLMs.
*   **Antes:** Lista de JSONs com IDs numéricos.
*   **Agora:** "Em 10/10 às 14:00, João mudou status de Novo para Processando."

### B. Saúde do Ticket (Health Check)
Diagnóstico automático de problemas no atendimento.
1.  **Ping-Pong (Reatribuições Excessivas):**
    *   Contagem de trocas de técnico (`campo IN ('technician', 'group')`).
    *   *Regra:* > 3 trocas = Saúde "Ruim".
2.  **Reaberturas (Rework):**
    *   Detecção de transição de status "Solucionado/Fechado" para "Processando/Novo".
    *   *Impacto:* Indica falha na primeira resolução.

### C. Gargalos de Processo (Process Mining)
Análise macroscópica (Global) para gestores.
*   **Dwell Time (Tempo de Permanência):** Média de horas que os tickets passam em cada status.
*   *Exemplo:* "A fase de 'Aprovação' está levando em média 96 horas, sendo o maior gargalo atual."

---

## 4. Implementação Técnica

### Backend (`glpi-data-service`)
Novos endpoints foram criados para expor essa inteligência via API REST.

*   **Arquivo:** `src/modules/dtic/tickets/analysis_service.py`
*   **Endpoints:**
    *   `GET /api/v1/analysis/tickets/{id}/timeline`
    *   `GET /api/v1/analysis/tickets/{id}/health`
    *   `GET /api/v1/analysis/global/bottlenecks?days=30`

### Agente de IA (`glpi-ai-system`)
O Agente Analista (`AnalystAgent`) foi equipado com ferramentas nativas (Tools) para consultar essas métricas diretamente no banco de dados, sem depender de alucinação ou processamento pesado de texto.

**Tools Disponíveis para o LLM:**
1.  `self.get_ticket_timeline(ticket_id)`
2.  `self.get_ticket_health(ticket_id)`
3.  `self.get_process_bottlenecks(days)`

**Exemplo de Raciocínio do Agente:**
> **Usuário:** "Por que o ticket 11909 demorou tanto?"
> **Agente (Pensamento):** Preciso ver o histórico. Vou chamar `get_ticket_timeline(11909)`.
> **Agente (Ação):** Analisa o retorno e percebe que ficou 5 dias em "Aguardando Peça".
> **Agente (Resposta):** "O ticket demorou principalmente porque ficou paralisado por 5 dias aguardando uma peça externa entre 12/10 e 17/10."

---

## 5. Próximos Passos Recomendados

1.  **Análise de Sentimento em Followups:**
    *   Utilizar a coluna `valor_novo` quando `campo='content'` para analisar o tom das mensagens trocadas.
2.  **Predição de Atraso (SLA Preditivo):**
    *   Treinar um modelo simples (Regressão/Random Forest) usando `historico_mudancas` para prever se um ticket vai estourar o prazo.
3.  **Detecção de Anomalias:**
    *   Alertar quando um ticket segue um fluxo de status nunca visto antes (ex: "Novo" -> "Fechado" sem passar por "Processando").

---
*Documento gerado automaticamente pelo Assistente de Engenharia de IA.*
