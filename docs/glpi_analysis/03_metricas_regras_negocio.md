# Métricas e Regras de Negócio - GLPI DTIC

Este documento descreve os indicadores de desempenho (KPIs) e as regras de negócio implementadas nos dashboards e relatórios da DTIC, com base no código fonte e configurações do sistema.

## 1. Indicadores Principais (KPIs)

### Volumetria de Chamados por Status
*   **Descrição:** Quantidade de tickets em cada fase do ciclo de vida.
*   **Fórmula (SQL Simplificado):** `SELECT status, COUNT(*) FROM tickets WHERE is_deleted = false GROUP BY status`
*   **Categorias de Gestão:**
    *   **Novos:** Status `NOVO`
    *   **Em Progresso:** Status `ATRIBUIDO` + `PLANEJADO`
    *   **Pendentes:** Status `PENDENTE`
    *   **Resolvidos:** Status `SOLUCIONADO` + `FECHADO`
*   **Fonte:** `dashboard.py` (Endpoint `/metrics-gerais`)
*   **Atualização:** Tempo Real.

### Ranking de Técnicos (Produtividade)
*   **Descrição:** Top 10 técnicos com maior volume de tickets atribuídos no período.
*   **Fórmula:** `SELECT tecnico, COUNT(*) FROM tickets GROUP BY tecnico ORDER BY count DESC LIMIT 10`
*   **Filtros:** Exclui tickets deletados e técnicos 'N/A'.
*   **Fonte:** `dashboard.py` (Endpoint `/ranking-tecnicos`)

### Ranking de Categorias/Entidades (Demandas)
*   **Descrição:** Identifica quais serviços (Categorias) ou órgãos (Entidades) geram mais demanda.
*   **Fórmula:** `SELECT categoria, COUNT(*) ... GROUP BY categoria`
*   **Fonte:** `sis_dashboard.py`

### Ocupação de Carregadores (Inventário SIS)
*   **Descrição:** Monitora ativos em uso vs. disponíveis.
*   **Lógica:**
    *   **Ocupado:** Carregador vinculado a ticket ativo (não fechado/solucionado).
    *   **Tempo de Uso:** `NOW() - ticket.criado_em` (em minutos).
*   **Fonte:** `sis_carregadores.py`

## 2. Regras de Negócio e Lógica de ETL

### Normalização de Status
O sistema mapeia os IDs numéricos de status do GLPI para nomes legíveis em caixa alta:
*   `1` -> `NOVO`
*   `2` -> `ATRIBUIDO`
*   `3` -> `PLANEJADO`
*   `4` -> `PENDENTE`
*   `5` -> `SOLUCIONADO`
*   `6` -> `FECHADO`

### Derivação de Nível de Suporte (Grupos)
O nível de suporte (N1, N2, N3, N4) é derivado automaticamente do nome do grupo atribuído, buscando palavras-chave:
*   **N1:** "n1", "nivel 1", "suporte 1"
*   **N2:** "n2", "nivel 2", "suporte 2"
*   (Lógica definida em `transformer.py`)

### Pontuação de Relevância (Smart Search)
A busca utiliza um algoritmo de pesos para ordenar resultados:
*   Título exato: Peso 1.0
*   Correspondência no título: Peso 0.8
*   Correspondência no requerente: Peso 0.5
*   Correspondência na descrição: Peso 0.3
*   (Lógica definida em `search.py`)

### Sincronização Incremental
*   **Critério:** Verifica tickets modificados desde a última execução (`date_mod > last_sync`).
*   **Integridade:** Calcula hash MD5 de campos críticos (título, status, descrição) para detectar mudanças reais e evitar updates desnecessários.
*   **Janela:** Executa a cada 15 segundos (configurável em `config.py`).
