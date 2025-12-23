# Dependências e Requisitos Técnicos

## 1. Bibliotecas Python (Core)

Baseado na análise do código fonte, as bibliotecas essenciais para rodar o módulo de inteligência são:

| Biblioteca | Uso Principal | Versão Recomendada |
| :--- | :--- | :--- |
| `httpx` | Cliente HTTP Assíncrono para comunicação com Ollama/GLPI | `>=0.24.0` |
| `pydantic` | Validação de dados e Schemas (Models) | `>=2.0.0` |
| `python-dotenv` | Carregamento de variáveis de ambiente | `>=1.0.0` |

*Nota: O projeto original pode conter mais dependências (ex: FastAPI, LangChain), mas para **exportar a inteligência pura** (LLM + Classificador), apenas as acima são estritamente necessárias.*

## 2. Requisitos de Infraestrutura

### 2.1. Servidor de Inferência (LLM)
- **Software**: Ollama (Recomendado) ou compatível com OpenAI API.
- **Hardware Mínimo**:
    - GPU: NVIDIA com 8GB+ VRAM (para modelos 7B quantizados).
    - CPU: AVX2 support (se rodar em CPU, será lento).
    - RAM: 16GB+ (se rodar modelo em RAM).
- **Conectividade**: Acesso via HTTP (porta padrão 11434).

### 2.2. Conectividade de Rede
- Acesso ao servidor GLPI (para sincronização de categorias).
- Acesso à Internet (apenas se for baixar modelos novos, runtime é offline).

## 3. Variáveis de Ambiente (.env)

Configurações obrigatórias para o funcionamento do módulo exportado:

```ini
# Configuração LLM
INFERENCE_SERVER_URL=http://localhost:11434  # URL do Ollama
LLM_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct-AWQ # Nome do modelo no Ollama

# Configuração GLPI (Para Sync)
GLPI_API_URL=https://seu-glpi.com/apirest.php
GLPI_APP_TOKEN=seu_app_token
GLPI_USER_TOKEN=seu_user_token
```

## 4. Artefatos de Dados
- **`categories_list.json`**: Deve estar presente no diretório de execução ou configurado via path.
- **`prompts.json`**: Arquivo de templates de prompt.
