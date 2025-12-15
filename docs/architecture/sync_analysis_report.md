# Relatório de Análise Técnica: Inconsistências de Sincronização e Fluxos de Produção

## Visão Geral
- Objetivo: mapear fluxos de sincronização, identificar inconsistências e pontos de falha, analisar a orquestração entre componentes e documentar definições faltantes que impactam a integridade dos dados.
- Componentes analisados: `glpi-data-service` (FastAPI), `glpi-sync-service` (daemon), Postgres (`dtic`, `sis`, `public`), `docker-compose.yml`.

## Inconsistências Críticas Identificadas

- Armadilha do Bootstrap (Falso Positivo de Sincronização)
  - Descrição: o sistema passa para modo incremental apenas porque existe registro em `SyncState`, sem garantir que o bootstrap concluiu com dados completos.
  - Evidências:
    - `glpi-data-service/scripts/daemon_sync.py:98–151` (bootstrap_if_needed executa full e depois inicializa SyncState, mesmo se houve erros; erros no bootstrap são logados e o daemon segue).
    - `glpi-data-service/scripts/init_sync_state.py:34–55` (define `last_sync` para `UTC-15 dias`, arbitrário, não baseado em dados processados).
  - Impacto: histórico anterior ao `last_sync` arbitrário pode ser ignorado; lacunas como tickets recentes (ex.: `11929`) ausentes enquanto mudanças na API referem esses tickets.

- Orquestração de Dependências (Drop Silencioso de Filhos)
  - Descrição: sincronização de filhos (`TicketChange`, `TicketItem`) depende estritamente da existência do pai (`Ticket`) local; sem ordem garantida e sem retry.
  - Evidências:
    - `glpi-data-service/src/services/sync_service.py:541–550` (descarta mudança se `ticket_glpi_id` não está em `tickets_map`).
  - Impacto: mudanças válidas são perdidas se o ticket não foi importado ainda; como o cursor incremental avança, essas mudanças não são revisitadas.

- Validação de Integridade Destrutiva
  - Descrição: importação de tickets rejeita ou degrada dados se metadados (usuários, entidades, locais) não estão previamente sincronizados.
  - Evidências:
    - `glpi-data-service/src/services/sync_service.py:348–360` (FKs são anuladas se não constarem em `valid_ids`).
  - Impacto: tickets ficam incompletos; dependências recém-criadas no GLPI podem gerar dados inconsistentes quando sincronização de metadados ainda não rodou.

- Definição de Última Sincronização Baseada em Execução, Não em Dados
  - Descrição: `SyncState.last_sync` é atualizado com o horário de início da execução, não com `MAX(date_mod)` realmente processado.
  - Evidências:
    - `glpi-data-service/scripts/sync.py:142–166` (usa `start_ticket_sync = datetime.utcnow()` para gravar estado; similar para mudanças em `180–188`).
  - Impacto: falhas parciais fazem o sistema marcar leitura até “agora”, descaracterizando reprocessamento e gerando lacunas de dados.

## Mapeamento dos Processos de Sincronização

```mermaid
flowchart TD
  A[Start Container] --> B[wait_for_db]
  B --> C[ensure_schema (create_db.py)]
  C --> D{sync_state vazio?}
  D -- sim --> E[run_sync(all, incremental=false)]
  E --> F[init_sync_state.py (define last_sync)]
  D -- não --> G[loop incremental (cada 30s)]
  F --> G
  G --> H[run_sync(tickets, incremental=true)]
  H --> I[update SyncState (hora início)]
  I --> G
```

- Sincronização de Tickets
  - Entrada: GLPI `Ticket` com paginação e filtros (`date_mod > last_sync` quando incremental).
  - Código: `glpi-data-service/src/services/sync_service.py:300–412`.
  - Validação e hidratação: define FKs condicionais com `valid_ids`.

- Sincronização de Mudanças (Logs)
  - Entrada: GLPI `Log` com `itemtype=Ticket`, ordenação e paginação/backoff.
  - Código: `glpi-data-service/src/services/sync_service.py:495–589`.
  - Dependência: requer `Ticket` local; caso contrário, ignora (`continue`).

- Atualização de `SyncState`
  - Ticket: `glpi-data-service/scripts/sync.py:156–166`.
  - Mudanças: `glpi-data-service/scripts/sync.py:181–188`.
  - Tabela: `glpi-data-service/src/core/models.py:12–23` (`public.sync_state`).

## Verificação da Consistência de Start/Stop

- Inicialização
  - `daemon_sync.py:154–168` (ordem: DB → Schema → Bootstrap → Loop).
  - Risco: falha em `run_sync(all)` não bloqueia entrada no loop; `init_sync_state.py` pode ter rodado e marcado estado indevidamente.

- Parada
  - `daemon_sync.py:37–45` (handler de sinais) e `199–202` (saída graciosa).
  - Consistência: sem rollback de estados parciais; se crash ocorrer antes de conclusão, `SyncState` pode estar adiantado.

## Orquestração entre Componentes

- `docker-compose.yml:5–26, 31–67, 68–98, 176–200, 202–226, 232–234`
  - Serviços: `postgres`, `data-service`, `glpi-sync` dependem de `postgres` saudável.
  - Healthcheck: `postgres` usa `pg_isready`; `data-service` usa `/health`.
  - Observação: nomes fixos de containers e volumes (`postgres_data`) podem conflitar entre projetos (vide `docs/CONFLICT_ANALYSIS.md:26–60`).

- `glpi-data-service/src/main.py:1–34, 72–95`
  - Endpoints: `dtic`, `sis`, `knowledge`, health.
  - DB: `src/core/database.py:48–72` configura `search_path` por contexto (schema).

## População de Dados e Sincronização em Tempo Real

- Tickets
  - Contagem/intervalo atual: exemplo observado `11433` tickets (`MAX(glpi_id)=11925, MIN=1`).
  - Gap: IDs como `11929` presentes na API (via logs) ainda não existem localmente.

- Mudanças (Logs)
  - `sync_ticket_changes` exige ticket local; mudanças recentes citando tickets fora do banco são descartadas.
  - Backoff: `_fetch_with_backoff` (HTTP 400/416) em `sync_service.py:72–102`.

## Definições Faltantes e Inconsistências

- Flag explícito de conclusão de bootstrap
  - Falta mecanismo “atômico” indicando que full sync concluiu com sucesso.

- Políticas de atualização de `SyncState`
  - Baseadas em horário de execução; ausência de cursor baseado em dados (`MAX(date_mod)` efetivamente gravado).

- Fila de reprocessamento para órfãos
  - Ausência de mecanismo para registrar e reprocessar `TicketChange`/`Item_Ticket` sem pai.

- Lookback no incremental
  - Falta sobreposição temporal para evitar perder eventos de borda.

## Pontos Críticos que Necessitam Correção

- Garantir Bootstrap Atômico antes de iniciar modo incremental.
- Evitar avanço indevido de `SyncState` em execuções parciais/falhas.
- Introduzir DLQ (Dead Letter Queue) para filhos órfãos e reprocessamento.
- Implementar `last_sync` baseado em dados processados (`MAX(date_mod)`), não em tempo de execução.
- Adotar janela de lookback ao calcular critérios `date_mod > last_sync`.
- Melhorar logging em pontos de `continue` para diagnósticos e auditoria.

## Recomendações

- Bootstrap Atômico
  - Introduzir `bootstrap_completed` em `public` e bloquear incremental até flag verdadeiro.
  - Em caso de falha, retomar bootstrap do ponto de parada (checkpoint por entidade).

- Janela de Lookback
  - Recuar `last_sync` em X minutos/horas para evitar perdas por latência ou clock drift.

- DLQ para Órfãos
  - Persistir filhos sem pai em `public.orphan_changes` com `glpi_log_id`, `items_id`, `primeira_visita`, `tentativas`, `última_tentativa`.
  - Criar rotina de reconciliação pós-sync de tickets.

- Cursor por Dados
  - Atualizar `SyncState` com o maior `date_mod` confirmado no banco para cada entidade.

- Validação de Metadados Lazy
  - Ao detectar referência inexistente, registrar aviso/contador e agendar sync de metadados imediato.

## Referências no Código

- Daemon bootstrap e loop: `glpi-data-service/scripts/daemon_sync.py:98–151, 154–202`
- Sync CLI e atualização de estado: `glpi-data-service/scripts/sync.py:142–166, 180–188`
- Lógica de tickets: `glpi-data-service/src/services/sync_service.py:300–412`
- Lógica de mudanças: `glpi-data-service/src/services/sync_service.py:495–589`
- Gating de mudanças: `glpi-data-service/src/services/sync_service.py:541–550`
- Configuração DB e schemas: `glpi-data-service/src/core/database.py:48–72`
- Modelos chave: `glpi-data-service/src/core/models.py:12–23`, `src/modules/dtic/tickets/models.py:19–69`, `src/modules/dtic/tickets/relationship_models.py:49–67`
- Compose: `docker-compose.yml:5–26, 31–67, 68–98, 176–200, 202–226, 232–234`

---

Este relatório consolida a compreensão dos fluxos atuais e os riscos que causam inconsistências em produção. As recomendações são projetadas para robustez sem alterar o objetivo funcional, e servem de base para uma fase de correção focada e segura.

