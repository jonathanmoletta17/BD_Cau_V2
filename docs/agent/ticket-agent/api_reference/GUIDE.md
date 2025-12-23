# Guia de Integração da API

Este guia descreve os fluxos de trabalho comuns para integrar sistemas externos (como frontends, chatbots ou sistemas de automação) com a API do Agente de Triagem.

## Fluxo 1: Classificação Direta de Chamados

Utilize este fluxo quando você já possui o título e a descrição do problema (ex: vindo de um formulário web) e deseja obter a categoria GLPI mais provável.

1.  **Verifique a disponibilidade da API**
    *   Chame `GET /health` para garantir que o serviço e o LLM estão online.
2.  **Envie a requisição de classificação**
    *   Chame `POST /classify` com o `title` e `description`.
    *   Recomendamos enviar `max_candidates: 3` para receber alternativas caso a primeira não seja adequada.
3.  **Processe a resposta**
    *   O campo `best_match` contém a categoria sugerida com maior confiança.
    *   O campo `candidates` lista outras possibilidades com seus respectivos scores de confiança (`confidence_score`).
    *   **Lógica de Negócio Sugerida**: Se `confidence_score` < 0.6, considere encaminhar para uma fila de triagem humana ou solicitar mais informações ao usuário.

## Fluxo 2: Triagem Interativa (Chat)

Utilize este fluxo para construir uma interface de chat onde o agente faz perguntas ao usuário para refinar o problema antes de classificar.

1.  **Inicie a Sessão**
    *   O cliente deve manter o histórico da conversa (`messages`).
    *   A primeira mensagem geralmente é do usuário descrevendo o problema.
2.  **Loop de Conversação**
    *   Chame `POST /chat` enviando o histórico completo de mensagens.
    *   **Analise a resposta**:
        *   Se `type` for `conversation`: Exiba o conteúdo de `content` para o usuário e aguarde a resposta dele. Adicione a resposta do assistente e a nova resposta do usuário ao histórico e repita o passo 2.
        *   Se `type` for `classification`: O agente determinou que tem informações suficientes. O campo `classification` conterá os dados da categoria (id, name, path). Encerre o chat e abra o chamado no GLPI com esses dados.
3.  **Persistência**
    *   A API é *stateless* (não guarda estado). O cliente é responsável por armazenar e reenviar o contexto da conversa a cada requisição.

## Tratamento de Erros e Retentativas

*   **Timeouts**: As chamadas de inferência de IA podem levar alguns segundos (5-30s dependendo do hardware). Configure seus timeouts de cliente adequadamente (recomendado: 60s).
*   **Erros 500**: Geralmente indicam falha na comunicação com o Ollama ou erro interno. Implemente uma estratégia de *exponential backoff* para tentar novamente.
*   **Validação**: Erros 422 indicam payload inválido. Verifique se os campos obrigatórios (definidos em [Modelos de Dados](data_models.md)) estão presentes.
