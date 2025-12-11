# manual do Usuário: MCP Toolbox (Model Context Protocol)
## BD_Cau_V2

Este documento sintetiza o funcionamento, configuração e uso das ferramentas MCP criadas para o projeto `BD_Cau_V2`. Estas ferramentas foram desenhadas para serem utilizadas por Agentes de IA (via function calling) ou scripts de automação.

---

### 1. Visão Geral
O **MCP Toolbox** é um conjunto de módulos Python localizados em `mcp_toolbox/` que expõem operações críticas do sistema de forma segura e padronizada.

**Módulos Disponíveis:**
- **Database Ops**: Leitura e inspeção do PostgreSQL.
- **GLPI Ops**: Controle e monitoramento da sincronização de dados.
- **Agent Ops**: Simulação e teste de classificação de tickets via IA.
- **GCP Ops**: Integração com Google Cloud (BigQuery, Storage, Dataplex).
- **Git Ops**: Operações de versionamento e controle de código.

---

### 2. Pré-requisitos e Configuração

Para que as ferramentas funcionem corretamente, o ambiente onde elas são executadas (Host ou Container) deve atender aos requisitos:

#### Dependências Python
Instale as bibliotecas necessárias:
```bash
pip install psycopg2-binary google-cloud-bigquery google-cloud-storage google-cloud-datacatalog python-dotenv
```

#### Variáveis de Ambiente (.env)
O arquivo `.env` na raiz do projeto deve conter:

```ini
# Acesso ao Banco de Dados
POSTGRES_HOST=postgres       # Use 'localhost' se rodar fora do Docker
POSTGRES_DB=glpi_data
POSTGRES_USER=glpi_user
POSTGRES_PASSWORD=glpi_secure_2024

# Google Cloud Platform (Para GCP Ops)
GOOGLE_APPLICATION_CREDENTIALS=mcp_toolbox/secrets/gcp-key.json
GCP_PROJECT_ID=lofty-complex-465523-k0
```

#### Docker Containers
Algumas ferramentas dependem de containers ativos:
- `db_ops` requer `bd_cau_postgres` (ou acesso direto ao banco).
- `glpi_ops` requer `glpi-data-service`.
- `agent_ops` requer `glpi-agent-classificator-worker` (ou web interface compatível).

---

### 3. Guia de Uso das Ferramentas

Abaixo detalhamos cada ferramenta, seu propósito e exemplos de uso (simulação de como um Agente chamaria a função).

#### 3.1. Database Tools (`db_ops.py`)
Focadas em **leitura segura** do banco de dados analítico.

**Ferramenta: `db_list_tables`**
- **Descrição**: Lista tabelas nos schemas `public`, `dtic`, `sis`.
- **Exemplo de Uso**:
```json
{
  "name": "db_list_tables",
  "arguments": {
    "schema": "all"
  }
}
```

**Ferramenta: `db_read_sql`**
- **Descrição**: Executa SELECTs (Bloqueia INSERT/UPDATE/DELETE).
- **Exemplo de Uso**:
```json
{
  "name": "db_read_sql",
  "arguments": {
    "query": "SELECT id, name FROM dtic.glpi_tickets WHERE date > '2024-01-01' LIMIT 5"
  }
}
```

#### 3.2. GLPI Operations (`glpi_ops.py`)
Controle do pipeline de dados ETL.

**Ferramenta: `glpi_trigger_sync`**
- **Descrição**: Força a sincronização imediata de dados do GLPI.
- **Exemplo de Uso**:
```json
{
  "name": "glpi_trigger_sync",
  "arguments": {
    "context": "dtic",
    "sync_type": "tickets"
  }
}
```

**Ferramenta: `glpi_check_sync`**
- **Descrição**: Verifica logs para saber se a sincronização funcionou.
- **Exemplo de Uso**:
```json
{
  "name": "glpi_check_sync",
  "arguments": {}
}
```

#### 3.3. Agent Operations (`agent_ops.py`)
Permite invocar o modelo de IA do projeto para classificar textos arbitrários, sem passar pelo GLPI.

**Ferramenta: `agent_simulate_classification`**
- **Descrição**: Classifica um problema simulado.
- **Exemplo de Uso**:
```json
{
  "name": "agent_simulate_classification",
  "arguments": {
    "title": "Erro na Impressora",
    "description": "A impressora do 3º andar está piscando luz vermelha e não imprime."
  }
}
```
*Nota: Requer que o container do agente esteja rodando.*

#### 3.4. GCP Operations (`gcp_ops.py`)
Operações nativas de nuvem.

**Ferramenta: `bq_query`**
- **Descrição**: Executa SQL no BigQuery.
- **Exemplo de Uso**:
```json
{
  "name": "bq_query",
  "arguments": {
    "query": "SELECT * FROM `lofty-complex.dataset.table` LIMIT 10",
    "dry_run": false
  }
}
```

**Ferramenta: `gcs_list_files`**
- **Descrição**: Lista arquivos em um bucket.
- **Exemplo de Uso**:
```json
{
  "name": "gcs_list_files",
  "arguments": {
    "bucket_name": "meu-datalake-raw"
  }
}
```

#### 3.5. Git Operations (`git_ops.py`)
Controle de versão básico.

**Ferramenta: `git_status`**
- **Descrição**: Vê arquivos modificados.
- **Exemplo de Uso**:
```json
{
  "name": "git_status",
  "arguments": {}
}
```

---

### 4. Dicas para Agentes

1. **Segurança Primeiro**: Sempre use `db_read_sql` para exploração. Nunca tente alterar dados diretamente no banco via SQL.
2. **Setup do Ambiente**: Se receber erro "Host not found" no Postgres, verifique se está rodando localmente (`localhost`) ou via Docker (`postgres`).
3. **Erros de GCP**: Se receber "Credentials not found", verifique se o arquivo `gcp-key.json` existe e a variável `GOOGLE_APPLICATION_CREDENTIALS` aponta para ele corretamente.

---
**Fim do Manual**
