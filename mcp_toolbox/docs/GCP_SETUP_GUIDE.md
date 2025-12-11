# Relatório de Auditoria e Guia de Configuração GCP

## PARTE 1: Auditoria de Variáveis (Status Atual)

| Variável | Valor Detectado | Status | Ação Necessária |
| :--- | :--- | :--- | :--- |
| **GIT_AUTHOR_NAME** | `Jonathan Moletta` | ✅ Pronto | Nenhuma. (Detectado via `git config`) |
| **GIT_AUTHOR_EMAIL** | `jonathan.moletta@gmail.com` | ✅ Pronto | Nenhuma. (Detectado via `git config`) |
| **GCP_PROJECT_ID** | *(vazio)* | ❌ Pendente | Criar/Selecionar no Console GCP. |
| **GCP_REGION** | *(vazio)* | ❌ Pendente | Definir (Ex: `us-central1` ou `southamerica-east1`). |
| **GOOGLE_APP_CREDS** | *(vazio)* | ❌ Pendente | Gerar chave JSON de Conta de Serviço. |
| **ALLOYDB_CLUSTER** | *(vazio)* | ❌ Pendente | Obter ID no Console. |

---

## PARTE 2: Guia Passo-a-Passo (Configuração GCP)

Este guia assume que você já possui uma conta no [Google Cloud Console](https://console.cloud.google.com/).

### PASSO 1: Configuração Inicial do Projeto
1.  **Acesse o Console**: https://console.cloud.google.com/
2.  **Selecione/Crie o Projeto**: 
    *   Clique no seletor de projetos (topo esquerdo, ao lado do logo Google Cloud).
    *   Anote o **ID do projeto** (ex: `bd-cau-v2-prod`). Este será o seu `GCP_PROJECT_ID`.

### PASSO 2: Criar Conta de Serviço (O "Robô" do MCP)
Esta conta permitirá que o Agente Antigravity acesse os recursos sem usar sua conta pessoal.

1.  **Navegue**: Menu Hambúrguer (☰) > **IAM e administrador** > **Contas de serviço**.
2.  **Criar**: Clique em **+ CRIAR CONTA DE SERVIÇO** (topo).
3.  **Detalhes**:
    *   **Nome**: `antigravity-agent`
    *   **ID**: `antigravity-agent` (automático)
    *   **Descrição**: "Conta para operações de MCP do Agente Antigravity"
    *   Clique em **CRIAR E CONTINUAR**.
4.  **Permissões (CRÍTICO)**:
    Adicione os seguintes **Papéis (Roles)** na caixa "Selecionar papel":
    *   **BigQuery** > **Usuário do BigQuery** (Permite rodar queries)
    *   **BigQuery** > **Visualizador de dados do BigQuery** (Permite ler tabelas)
    *   **Cloud Storage** > **Visualizador de objetos do Storage** (Permite ler arquivos/buckets)
    *   **Dataplex** > **Visualizador do Dataplex** (Para busca de metadados, se usar)
    *   **AlloyDB** > **Cliente do AlloyDB** (Permite conexão via Auth Proxy)
    *   *Opcional (apenas se for usar features de IA generativa no Vertex)*: **Vertex AI User**
    *   Clique em **CONCLUIR**.

### PASSO 3: Gerar e Baixar a Chave JSON
1.  Na lista de contas, clique no e-mail da conta recém-criada (`antigravity-agent@...`).
2.  Vá na aba **CHAVES** (Keys).
3.  Clique em **ADICIONAR CHAVE** > **Criar nova chave**.
4.  Tipo: **JSON** (já selecionado).
5.  Clique em **CRIAR**.
    *   O download começará automaticamente.
6.  **AÇÃO IMEDIATA**: Renomeie o arquivo baixado para `gcp-key.json`.
7.  **ONDE SALVAR**:
    *   Mova este arquivo para: `c:\Users\jonathan-moletta\Projetos_Locais\BD_Cau_V2\mcp_toolbox\secrets\gcp-key.json`
    *   *Nota*: Crie a pasta `secrets` se não existir. Certifique-se que ela está no `.gitignore`.

### PASSO 4: Obter IDs do AlloyDB (Se aplicável)
Se você já tem um cluster AlloyDB criado:
1.  **Navegue**: Menu (☰) > **AlloyDB** > **Clusters**.
2.  **Cluster ID**: Copie o nome do cluster (ex: `cluster-producao`).
3.  **Instance ID**: Clique no cluster e copie o nome da instância primária (ex: `cluster-producao-primary`).
4.  **Region**: Veja a região (ex: `us-central1`).

### PASSO 5: Preencher o .env
Adicione o bloco abaixo ao final do seu arquivo `.env` atual:

```bash
# ==============================================
# MCP TOOLBOX (GCP CONFIG)
# ==============================================
GCP_PROJECT_ID=seu-id-do-projeto-aqui
GCP_REGION=us-central1

# Caminho dentro do container (vamos mapear via volume)
# OU caminho absoluto local para testes locais (como o verify_advanced.py)
GOOGLE_APPLICATION_CREDENTIALS=mcp_toolbox/secrets/gcp-key.json

# AlloyDB (Preencha se tiver cluster ativo)
ALLOYDB_CLUSTER_ID=
ALLOYDB_INSTANCE_ID=
```

### Resumo para Execução
Após realizar estes passos:
1.  Salvar a chave em `mcp_toolbox/secrets/gcp-key.json`.
2.  Atualizar o `.env`.
3.  Rodar a validação novamente.
