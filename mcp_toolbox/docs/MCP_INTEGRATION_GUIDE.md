# Guia de Integração e Uso do MCP Toolbox

Este documento explica como utilizar, configurar e "universalizar" o uso das ferramentas MCP criadas para o Agente Antigravity.

## 1. Como usar agora (Neste Projeto)

As ferramentas já estão implementadas em `mcp_toolbox/`. Para que a IA (Antigravity ou outra) possa usá-las, o **Servidor MCP** que você utiliza deve estar apontando para este arquivo de definição.

### Passo Único: Configuração do Cliente MCP
Adicione o seguinte ao seu arquivo de configuração de ferramentas (geralmente `config.json` ou nas configurações da extensão AI que você usa):

```json
{
  "mcpServers": {
    "bd_cau_toolbox": {
      "command": "python",
      "args": ["-m", "mcp.server.stdio"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "toolsConfig": "${workspaceFolder}/mcp_toolbox/tools.yaml" 
    }
  }
}
```

*Nota: A configuração exata depende de qual "Cliente MCP" você está usando (Claude Desktop, Cursor, VSCode extension, etc). O importante é apontar para o `tools.yaml`.*

---

## 2. Como usar em outros projetos ("Universalizar")

Para que a IA tenha acesso a essas ferramentas em **qualquer projeto**, você tem duas estratégias:

### Estratégia A: O "Sidecar" Universal (Recomendada)
Em vez de copiar os arquivos para cada projeto, rode o MCP Toolbox como um serviço Docker global na sua máquina.

1. **Crie um container global**:
   Mantenha este projeto (`BD_Cau_V2`) rodando ou extraia a pasta `mcp_toolbox` para um repositório isolado.

2. **Aponte os Agentes para ele**:
   Em qualquer outro projeto, configure o agente para conectar via SSE (Server-Sent Events) ou HTTP neste serviço central. Assim, o agente de outro projeto pode dizer: *"Vou consultar o banco de dados do projeto BD_Cau"* remotamente.

### Estratégia B: O Padrão de Pasta (Git Submodule)
Se você quer que cada projeto tenha seu próprio toolbox isolado:

1. Transforme a pasta `mcp_toolbox` em um repositório Git separado.
2. Em cada novo projeto, adicione como sub-módulo:
   ```bash
   git submodule add git@github.com:seu-user/mcp-toolbox-padrao.git .mcp_toolbox
   ```
3. A IA reconhecerá automaticamente a existência da pasta `.mcp_toolbox` se você instruí-la em suas regras globais.

---

## 3. Como instruir o Antigravity (Regras Globais)

Para garantir que o Antigravity **sempre** saiba usar isso, adicione o seguinte bloco ao seu `.cursorrules` ou Prompt de Sistema Global:

```markdown
# 🛠️ MCP TOOLBOX AWARENESS
Você tem acesso a ferramentas externas definidas em `mcp_toolbox/tools.yaml`.
ANTES de dizer "não consigo acessar o banco" ou "não sei o status do sync":
1. Verifique se a ferramenta existe no `tools.yaml`.
2. Use `db_list_tables`, `check_sync_status` ou `simular_classificacao` conforme necessário.
3. Não tente adivinhar nomes de tabelas; use `db_list_tables` primeiro.
```

## Resumo das Ferramentas Disponíveis

| Ferramenta | Comando (Function Call) | Quando usar? |
|------------|-------------------------|--------------|
| **DB Explorer** | `db_list_tables`, `db_read_sql` | Para responder perguntas sobre dados reais no banco. |
| **GLPI Ops** | `glpi_trigger_sync`, `glpi_check_sync` | Quando os dados parecerem desatualizados ou faltantes. |
| **Agent AI** | `agent_simulate_classification` | Para testar se a IA do projeto classificaria um ticket corretamente. |
