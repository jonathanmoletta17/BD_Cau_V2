# Inventário de Fontes de Dados GLPI - DTIC/RS

Este documento consolida o inventário das fontes de dados reais identificadas no ambiente da DTIC relacionadas ao GLPI, para uso em análise de dados e construção de agentes de apoio à decisão.

| Nome Lógico | Nome Técnico | Tipo da Fonte | Local/Tecnologia | Escopo de Dados | Nível de Atualização | Observações Relevantes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Banco de Dados Operacional (GLPI Data Service)** | `glpi_data` (PostgreSQL) | Banco Relacional (ODS/DW) | PostgreSQL (Docker Container) | Tickets, Usuários, Entidades, Categorias, SLAs, Logs de Sync | **Tempo Real** (< 15s delay) | Fonte centralizada e saneada. Mantém schemas separados: `dtic` (TI) e `sis` (Predial). |
| **API de Métricas Gerais** | `/api/routes/dashboard.py` | API REST | Python/FastAPI | Contagens de tickets por status, ranking de técnicos | Tempo Real | Endpoint otimizado para alimentar dashboards de gestão (React). |
| **API de Inventário de Carregadores** | `/api/routes/sis_carregadores.py` | API REST | Python/FastAPI | Status de carregadores, localização, ocupação | Tempo Real | Endpoint específico para controle de ativos físicos do SIS. |
| **API de Busca Avançada (Smart Search)** | `/api/routes/search.py` | API REST | Python/FastAPI | Tickets com score de relevância e filtros complexos | Tempo Real | Motor de busca textual com filtros combinados (requerente, data, etc.). |
| **Configuração de Sincronização** | `config.py` / `sync.py` | Código Fonte | Python | Regras de conexão, credenciais e lógica de ETL | N/A | Define a origem dos dados e parâmetros de atualização (intervalo de 15s). |
| **Logs de Sincronização** | `sync_history` / `sync_errors` | Tabela de Banco | PostgreSQL | Histórico de execuções, volumes e erros do ETL | Tempo Real | Essencial para monitorar a saúde do pipeline de dados. |

## Fontes Planejadas / Em Desenvolvimento

| Nome Lógico | Nome Técnico | Status | Observações |
| :--- | :--- | :--- | :--- |
| **Painel de Gestão de Carregadores** | `06.1.1-sis-carregadores-dashboard` | Em Desenvolvimento | Front-end React para visualização Kanban dos carregadores. |
| **Auditoria de Formulários Mobile** | `validate_all_forms.py` | Script | Robô de validação de canais de atendimento (Mobile App). |
