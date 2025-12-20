# Análise Técnica Profunda

## 1. Análise de Componentes

### 1.1. Classificador (`ClassifierService`)
- **Ponto Forte**: Alta precisão devido à abordagem em duas etapas (Root -> Leaf). Isso reduz o espaço de busca da LLM, evitando alucinações comuns quando se apresenta 200+ categorias de uma vez.
- **Ponto Fraco (Acoplamento)**:
    - **Dependência de Arquivo Local**: O código espera ler `categories_list.json` do sistema de arquivos. Em ambientes containerizados efêmeros (Lambda/Serverless), isso exige montar volumes ou alterar a lógica para ler de S3/Banco.
    - **Estrutura Rígida**: Assume hierarquia de 2 níveis (Domínio > Categoria). Se o GLPI tiver 3 ou 4 níveis, a lógica atual achata ou ignora a profundidade extra.

### 1.2. LLM Service (`LLMService`)
- **Ponto Forte**: Abstração limpa. O método `extract_entities` é muito útil e genérico.
- **Risco**:
    - **Timeouts**: A chamada HTTP tem timeout fixo (60s). Modelos maiores ou servidores sobrecarregados podem falhar.
    - **Formato de Resposta**: Depende da LLM "obedecer" a instrução de retornar JSON limpo. O código tem um tratamento básico (`replace markdown`), mas modelos menores podem falhar na sintaxe JSON.

### 1.3. Modelos de Dados (`models/`)
- Uso de Pydantic V2 garante tipagem forte.
- **Acoplamento**: Os modelos misturam conceitos de GLPI (`GLPICategory`) com lógica de negócio (`ClassificationResponse`). Na exportação, é saudável manter, mas se o destino não for GLPI, esses nomes devem ser generalizados.

## 2. Padrões de Comportamento Críticos

1.  **Fallback Silencioso**: Se o passo 2 da classificação falha (JSON inválido ou erro de lógica), o sistema retorna a categoria Raiz (Passo 1). Isso é bom para não travar, mas pode gerar tickets genéricos ("Hardware" em vez de "Hardware > Mouse").
2.  **Viabilidade Bypassed**: Existe lógica (no código do Agente B, não no core exportado) que "pula" a verificação de viabilidade se a confiança for alta. Ao exportar apenas o Core, perde-se essa otimização de fluxo.

## 3. Requisitos de Desempenho e Escalabilidade

- **Latência**:
    - Classificação completa leva: `(Tempo LLM Passo 1) + (Tempo LLM Passo 2)`.
    - Com modelo 7B em GPU: ~2 a 4 segundos.
    - Em CPU: ~10 a 30 segundos (inviável para chat real-time).
- **Concorrência**: O `LLMService` usa `httpx.AsyncClient`, permitindo alta concorrência no Python, mas o gargalo real é a fila de inferência do Ollama. Se houver muitos usuários simultâneos, o tempo de resposta degradará linearmente a menos que o Ollama tenha balanceamento de carga (vLLM ou múltiplas réplicas).

## 4. Adaptações Necessárias para Migração

1.  **Generalização de Caminhos**: Remover dependência de caminhos relativos fixos para `categories_list.json`. Receber o caminho ou o conteúdo JSON no construtor.
2.  **Tratamento de Erros JSON**: Implementar um "retry" com parser mais robusto (ex: usar biblioteca `json_repair` ou tentar reenviar o prompt em caso de erro de sintaxe).
3.  **Configuração de Modelo Dinâmica**: Permitir passar o nome do modelo por requisição, não apenas na inicialização, para permitir testes A/B.
