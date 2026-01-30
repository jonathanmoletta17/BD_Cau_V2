# ADR-001: Event Stream Canônico & Raw Event Store

## Status
Aprovado

## Contexto
O sistema GLPI (Write Model) é a fonte primária de verdade operacional, mas sua estrutura e persistência são mutáveis e sujeitas a intervenções externas (purgas de logs, scripts corretivos, restores parciais). Para alimentar Read Models (BI, Dashboards) de forma confiável e escalável, precisamos de uma história imutável e reprocessável que não dependa da fragilidade do estado atual ou da retenção volátil do GLPI.

## Decisão
Adotaremos a **Abordagem A (Log-based Polling)** como estratégia de captura, mas com uma separação rigorosa entre *Captura* e *Preservação*.

1.  **Fonte de Captura**: A tabela `glpi_logs` será a fonte de extração, consumida via cursor monotônico por ID.
2.  **Raw Event Store**: Implementaremos uma camada de persistência externa append-only (PostgreSQL / S3). Cada evento lido da `glpi_logs` deve ser gravado nesta camada ANTES de qualquer processamento.
3.  **Autoridade**: O **Raw Event Store** passa a ser a verdade canônica para o sistema de sincronização e BI, não mais o GLPI.

## Alternativas Consideradas
- **Abordagem B (Controlled State Capture)**: Descartada por ser epistemologicamente frágil e gerar inconsistências irreversíveis (State Shadowing).
- **Abordagem C (CDC/Debezium)**: Adiada devido à alta complexidade de infraestrutura e falta de semântica de negócio imediata, embora reconhecida como o sucessor natural da Abordagem A.

## Consequências Positivas
- **Independência de Retenção**: Se o GLPI deletar logs antigos, o Raw Event Store preserva a história.
- **Capacidade de Replay**: Podemos reconstruir qualquer estado passado ou corrigir bugs de projeção sem depender do banco de origem.
- **Auditabilidade**: Prova-se cada métrica do BI através do evento original capturado.

## Riscos Aceitos
- **Latência Δ**: Aceita-se um atraso de até 5 minutos (SLA Δ) entre o GLPI e o destino.
- **Acoplamento Semântico**: Dependência da consistência dos logs gerados pelo framework do GLPI.

## Riscos NÃO Aceitos
- **Divergência Silenciosa**: Não aceitaremos mudanças de estado no GLPI que não gerem logs (Ações Fantasmas). Caso identificadas, devem disparar a migração para CDC.
- **Mutação de História**: Não aceitaremos que o estado do Read Model seja alterado sem um correspondente no Event Store.

## Critérios de Migração (Fase 3 - CDC)
A migração para CDC será obrigatória se:
1. O volume de logs exceder a capacidade de polling dentro do SLA Δ.
2. Identificarmos que >5% das ações críticas de negócio ocorrem sem registro na `glpi_logs`.
3. A latência exigida pelo negócio for inferior a 1 minuto.

---
**Data**: 2026-01-23
**Responsável**: Arquitetura de Dados
