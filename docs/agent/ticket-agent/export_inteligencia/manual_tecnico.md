# Manual Técnico de Migração da IA

## Introdução
Este manual consolida as informações necessárias para exportar o núcleo de inteligência (Classificação e LLM) do Agente de Triagem atual para um novo ambiente.

## Conteúdo do Pacote
A pasta `export_inteligencia` contém:
1.  `arquitetura_atual.md`: Detalhes de funcionamento interno.
2.  `analise_tecnica.md`: Pontos de atenção e limitações.
3.  `dependencias_requisitos.md`: O que instalar.
4.  `plano_implementacao.md`: Passo a passo da migração.
5.  `estrategia_testes.md`: Como validar.

## Guia Rápido de Instalação (No Novo Projeto)

1.  **Copie os Arquivos**:
    - Transfira `llm_service.py` e `classifier_service.py` para a pasta de serviços do novo projeto.
    - Transfira `models/` para a pasta de modelos.
    - Copie `categories_list.json` para a raiz (ou configure o caminho).

2.  **Instale Dependências**:
    ```bash
    pip install httpx pydantic python-dotenv
    ```

3.  **Configure o .env**:
    Certifique-se que o novo projeto tem as variáveis:
    ```ini
    INFERENCE_SERVER_URL=http://localhost:11434
    LLM_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct-AWQ
    ```

4.  **Teste Inicial**:
    ```python
    from services.llm_service import LLMService
    from services.classifier_service import ClassifierService
    from models import ClassificationRequest
    
    # Init
    llm = LLMService()
    classifier = ClassifierService(llm_service=llm)
    
    # Run
    req = ClassificationRequest(description="Teste de migração")
    res = await classifier.classify(req)
    print(res)
    ```

## Troubleshooting Comum

| Sintoma | Causa Provável | Solução |
| :--- | :--- | :--- |
| **Erro "Connection refused"** | URL do Ollama errada ou serviço parado | Verifique `INFERENCE_SERVER_URL` e se o Ollama está rodando. |
| **Erro "FileNotFound: categories_list.json"** | Caminho do arquivo incorreto | Verifique onde o script está rodando vs onde o arquivo está. Edite `classifier_service.py` linha `CATEGORIES_FILE`. |
| **Classificação sempre retorna "Root"** | Passo 2 falhando (JSON inválido) | Verifique os logs. Pode ser necessário ajustar o prompt ou aumentar a temperatura levemente. |
| **Erro "404 Not Found" no LLM** | Nome do modelo incorreto | Verifique se o modelo definido em `LLM_MODEL` foi baixado no Ollama (`ollama list`). |

## Lições Aprendidas e Recomendações
- **Isolamento**: Mantenha a lógica de IA desacoplada da lógica de framework web (FastAPI/Flask). O `ClassifierService` deve receber objetos puros e retornar objetos puros.
- **Cache**: O carregamento do JSON de categorias é rápido, mas se o arquivo for gigante (>10MB), considere usar um banco de dados ou Redis. Atualmente é arquivo plano por simplicidade.
- **Versionamento**: Versionar o `categories_list.json` junto com o código ajuda a garantir que a IA "conhece" as mesmas categorias que o código espera.
