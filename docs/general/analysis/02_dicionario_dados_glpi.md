# Dicionário de Dados e Entidades GLPI

Este documento detalha as principais tabelas, entidades e relacionamentos do banco de dados analítico do GLPI (`glpi_data`), estruturado para suportar as operações da DTIC e SIS.

## 1. Tabelas Principais

### `tickets` (Fato / Entidade Principal)
Tabela central que armazena todos os chamados sincronizados. Existe uma cópia idêntica em cada schema (`dtic.tickets` e `sis.tickets`).

**Descrição Funcional:** Contém o registro histórico e atual de cada solicitação de serviço, incluindo dados de classificação, tempos, atores envolvidos e descrição do problema.

| Campo | Tipo | Descrição de Negócio | Sensível? | Chave? |
| :--- | :--- | :--- | :--- | :--- |
| `id` | SERIAL | Identificador interno do Data Service | Não | PK |
| `glpi_id` | INTEGER | Número do ticket original no GLPI | Não | UK |
| `titulo` | VARCHAR | Título resumido da solicitação | **Sim** (Pode conter nomes) | - |
| `descricao` | TEXT | Descrição completa (HTML original) | **Sim** (Dados pessoais/senhas) | - |
| `descricao_md` | TEXT | Descrição convertida para Markdown | **Sim** | - |
| `status` | VARCHAR | Estado atual (NOVO, ATRIBUIDO, etc.) | Não | - |
| `prioridade` | VARCHAR | Nível de prioridade (BAIXA, MEDIA, ALTA, etc.) | Não | - |
| `categoria` | VARCHAR | Nome da categoria de serviço (ex: "Rede", "Pintura") | Não | - |
| `entidade` | VARCHAR | Nome do órgão/departamento solicitante | Não | - |
| `tecnico` | VARCHAR | Nome do técnico responsável | **Sim** (Dado pessoal) | - |
| `requerente` | VARCHAR | Nome do usuário que abriu o chamado | **Sim** (Dado pessoal) | - |
| `criado_em` | TIMESTAMP | Data/hora de abertura | Não | - |
| `solucionado_em` | TIMESTAMP | Data/hora de solução | Não | - |
| `sla_ttr_id` | INTEGER | ID do SLA de tempo de resolução | Não | FK (GLPI) |
| `time_to_resolve` | TIMESTAMP | Prazo limite para solução (SLA) | Não | - |

### `carregadores` (Ativo / Inventário - Apenas SIS)
Tabela específica do schema `sis` para controle de equipamentos (carregadores).

**Descrição Funcional:** Cadastro dos dispositivos físicos disponíveis para empréstimo ou uso.

| Campo | Tipo | Descrição de Negócio | Sensível? | Chave? |
| :--- | :--- | :--- | :--- | :--- |
| `id` | SERIAL | Identificador do carregador | Não | PK |
| `name` | VARCHAR | Nome/Código do carregador | Não | - |
| `location_name` | VARCHAR | Localização atual (Sala/Prédio) | **Sim** (Segurança física) | - |
| `is_deleted` | BOOLEAN | Marcador de exclusão lógica | Não | - |

### `carregador_tickets` (Relacionamento N:N)
Tabela de ligação que conecta tickets a carregadores.

**Descrição Funcional:** Registra qual ticket está utilizando qual carregador num dado momento.

| Campo | Tipo | Descrição de Negócio | Sensível? | Chave? |
| :--- | :--- | :--- | :--- | :--- |
| `tickets_id` | INTEGER | ID do ticket (GLPI ID) | Não | FK |
| `items_id` | INTEGER | ID do carregador | Não | FK |

## 2. Relacionamentos Importantes

### Tickets -> Atores (Técnicos, Requerentes)
*   **Cardinalidade:** N:1 (No modelo simplificado atual, armazena apenas o ator principal em coluna de texto).
*   **De/Para:** `tickets.tecnico` (Nome) e `tickets.tecnico_id` (ID).
*   **Nota:** O GLPI original suporta N:N, mas o Data Service denormaliza para facilitar análise (1 ticket = 1 técnico principal na visão analítica).

### Tickets -> Categorias
*   **Cardinalidade:** N:1
*   **De/Para:** `tickets.categoria_id` -> Tabela de Categorias do GLPI (virtual).
*   **Junção:** O nome da categoria já vem resolvido no campo `tickets.categoria`.

### Tickets -> Carregadores (Schema SIS)
*   **Cardinalidade:** N:N
*   **De/Para:** `tickets.glpi_id` <-> `carregador_tickets.tickets_id` <-> `carregadores.id`
*   **Uso:** Permite saber "Quais tickets usaram o carregador X?" e "Quantos carregadores o ticket Y solicitou?".
