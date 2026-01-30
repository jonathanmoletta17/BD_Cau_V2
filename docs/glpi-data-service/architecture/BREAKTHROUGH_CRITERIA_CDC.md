# Critérios de Ruptura: Migração para Fase 3 (CDC)

Este documento estabelece os gatilhos objetivos que forçarão a interrupção da Abordagem A (Log-based Polling) e o início imediato da Fase 3 (CDC/Streaming).

## 1. Gatilho de Escala (Volume e Latência)
A Abordagem A baseia-se na eficiência do banco de origem em responder queries de polling.
- **Métrica**: O tempo de processamento de um lote de 1.000 eventos for superior ao intervalo de polling (ex: processar 5 min de logs leva 6 min).
- **Ação**: Início da migração para CDC para eliminar a carga de query e reduzir a latência para near-real-time.

## 2. Gatilho de Integridade (Ações Fantasmas)
A Abordagem A assume que o framework do GLPI registra todas as mudanças críticas.
- **Métrica**: Detecção de >5% de discrepância persistente entre o estado do Read Model e o estado da API (Snapshot) que não possua correspondência em `glpi_logs`.
- **Ação**: Migração para CDC para capturar mutações ao nível de binlog, garantindo a captura física de mudanças "por fora" do framework.

## 3. Gatilho de Retenção (Morte do Replay)
A Abordagem A depende da disponibilidade dos logs originais para reconstrução de história.
- **Métrica**: Decisão administrativa de reduzir a retenção da `glpi_logs` para um período inferior à janela mínima de BI (ex: reduzir para 30 dias em um BI que consulta 12 meses).
- **Ação**: Aceleração do **Raw Event Store** e migração para CDC para garantir que o sistema de dados tenha sua própria fonte de verdade independente do admin do GLPI.

## 4. Gatilho de Requisito de Negócio (SLA < 1 min)
Mudança nas necessidades dos stakeholders.
- **Métrica**: Necessidade formal de dashboards com latência inferior a 60 segundos por razões de monitoramento crítico.
- **Ação**: Migração para CDC/Streaming (Debezium + Kafka) para atingir latências de milissegundos.

---
**Data**: 2026-01-23
**Aprovação**: Stakeholder Técnico / Arquiteto
