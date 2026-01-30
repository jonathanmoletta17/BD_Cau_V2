# Manifesto Arquitetural: Data Sync Phase 1 & 2

## 1. Conclusão da Fase 1: O "Bug Epistemológico"

O diagnóstico de consistência de 92.77% foi provado **conceitualmente incorreto**. A discrepância não era uma falha de sincronização, mas sim uma indefinição de **fronteiras temporais**.

> [!NOTE]
> **SLA Δ (Delta)**: Em sistemas distribuídos baseados em polling, "sincronizado" não é um estado estático, mas uma promessa de completude dentro de uma janela temporal.

**O que aprendemos:**
- O modelo de atores (requesters/assignees) em sync incremental exige que o ticket pai exista no destino.
- Sem um `event_log` imutável, dependemos de modelos de estado (`date_mod`), o que gera condições de corrida.

## 2. Dívida Técnica Arquitetural (O Estado Atual)

Embora o sistema esteja **correto** sob o SLA definido, ele é **frágil**:

- **Polling de Estado**: Depender de `date_mod` é vulnerável a atualizações em massa que podem "pular" janelas de polling se não houver precisão de milisegundos ou cursores robustos.
- **Orphan Changes (DLQ)**: A existência de uma lógica de `reprocess_orphan_changes` é prova de que o sistema luta para manter integridade referencial em um fluxo de dados desordenado.
- **Acoplamento de Escrita**: O Worker de Sync compete por recursos com o Write Model (GLPI) e o Read Model (PostgreSQL), escalando linearmente com o volume de tickets.

## 3. Roadmap Estratégico para Fase 2

A Fase 2 não é sobre corrigir bugs, mas sobre **mudar o paradigma de escala**.

### Eixo 1: Modelo de Eventos (Event Sourcing Light)
Transformar transações em eventos explícitos (`ticket.created`, `actor.assigned`). 
*   **Abordagem Sugerida**: Captura via `ticket_changes` ou CDC (Change Data Capture) diretamente do MySQL do GLPI.

### Eixo 2: Separação de Modelos (CQRS)
Isolar completamente o **Write Model** (GLPI) do **Read Model** (Dashboard BI).
*   **Ação**: O Read Model deve ser alimentado por um `Event Log` imutável, permitindo "replay" de dados em caso de falha de consistência.

### Eixo 3: Escala e Sustentabilidade
- Reduzir o reprocessamento ineficiente.
- Implementar Background Workers especializados por tipo de evento.
- Preparar para volumes superiores a 3 milhões de registros em `ticket_changes`.

---

> "Engenharia madura não é apenas fazer funcionar, é saber exatamente por que funciona e sob quais condições deixará de funcionar."
