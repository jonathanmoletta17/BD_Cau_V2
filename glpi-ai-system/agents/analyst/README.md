# GLPI Analyst Agent 📊

Este agente utiliza **GenAI + Pandas** para analisar dados de chamados do GLPI através de linguagem natural.

## 🧠 Como Funciona (Arquitetura)
Baseado no padrão "LLM as a Reasoning Engine" (similar ao PandasAI), o fluxo é:

1.  **User Query:** O usuário faz uma pergunta (ex: "Qual setor tem mais chamados de hardware?").
2.  **Context Injection:** O agente injeta o esquema do DataFrame (colunas + valores únicos) no prompt do Sistema.
3.  **Code Generation:** O LLM (Llama 3 via Ollama) gera código Python (Pandas) para responder a pergunta.
4.  **Safe Execution:** O código é executado em um ambiente local controlado (`exec` com escopo restrito).
5.  **Explanation:** O resultado numérico/textual é enviado de volta ao LLM para gerar uma explicação em linguagem natural.

## 🛠️ Tecnologias
-   **LangChain / Custom Logic:** Implementação leve usando `requests` direto para Ollama (evitando overhead).
-   **Pandas:** Motor de análise de dados.
-   **Ollama:** LLM local (compatível com Llama 3, Mistral, Qwen).

## 🚀 Como Executar (Standalone)

### Pré-requisitos
-   Python 3.10+
-   PostgreSQL com dados do GLPI (Schema `dtic`)
-   Ollama rodando (`http://localhost:11434`)
-   Bibliotecas: `pandas`, `requests`, `sqlalchemy`, `psycopg2-binary`

### Configuração (.env)
Crie um arquivo `.env` na raiz ou defina as variáveis:
```env
LLM_BASE_URL=http://localhost:11434/v1
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=glpi_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### Rodar
```bash
# Se rodar do host (Windows) apontando para Ollama local
$env:LLM_BASE_URL="http://localhost:11434/v1"
python glpi-ai-system/agents/analyst/analyst_agent.py
```

## 🚧 Roadmap
- [x] Protótipo com Mock Data
- [ ] Conectar com Banco de Dados GLPI (PostgreSQL/MySQL) via `SQLAlchemy`
- [ ] Expor como API (FastAPI) para o frontend consumir
- [ ] Adicionar suporte a gráficos (retornar base64 da imagem plotada)
