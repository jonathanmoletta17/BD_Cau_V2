# Endpoint: Chat Interativo (`/chat`)

Endpoint conversacional projetado para interagir com o usuário final, coletar informações (triagem) e, quando houver dados suficientes, realizar a classificação automática.

## Detalhes da Requisição

- **URL**: `/chat`
- **Método HTTP**: `POST`
- **Autenticação**: Nenhuma (Pública/Interna)
- **Headers**:
    - `Content-Type: application/json`

## Parâmetros

### Query Parameters
| Parâmetro | Tipo | Obrigatório | Padrão | Descrição |
| :--- | :--- | :---: | :--- | :--- |
| `session_id` | `string` | Não | `"api_client"` | Identificador da sessão do usuário para logs ou persistência futura. |

## Corpo da Requisição (Request Body)
Uma lista de mensagens representando o histórico da conversa até o momento. Segue o modelo `List[ChatMessage]`.

### Exemplo de Requisição (cURL)
```bash
curl -X POST "http://localhost:8000/chat?session_id=user_123" \
     -H "Content-Type: application/json" \
     -d '[
           {"role": "assistant", "content": "Olá, como posso ajudar?"},
           {"role": "user", "content": "Preciso de um mouse novo."}
         ]'
```

## Resposta (Response)
Retorna um objeto JSON dinâmico. A estrutura varia dependendo se a IA decidiu apenas responder (conversar) ou se ela finalizou a triagem (classificou).

### Cenário 1: Conversa em Andamento (Coletando Info)
A IA fará uma pergunta para entender melhor o problema.

```json
{
  "role": "assistant",
  "content": "Qual é o modelo do seu computador ou é para uso em notebook?"
}
```

### Cenário 2: Triagem Concluída (Classificado)
Quando a IA determina que tem informações suficientes (`Viability Check = YES`), ela classifica e retorna a ação.

```json
{
  "role": "assistant",
  "content": "Entendido. Tenho informações suficientes.\n\n**Resumo do Chamado:**\n> **Assunto:** [Hardware] Solicitação de Mouse\n> **Categoria:** Hardware > Periféricos\n> **Urgência:** 3/5\n\nDeseja confirmar a abertura deste chamado?",
  "action": "classified",
  "details": {
    "selected_category_id": 5765,
    "selected_category_name": "Hardware > Periféricos",
    "confidence": 0.9,
    "reasoning": "Usuário solicitou explicitamente um mouse novo.",
    "ticket_type": 2,
    "urgency": 3,
    "impact": 3,
    "suggested_title": "[Hardware] Solicitação de Mouse",
    "candidates": [...]
  }
}
```

## Campos da Resposta

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `role` | `string` | Sempre `"assistant"`. |
| `content` | `string` | A mensagem textual para exibir ao usuário. |
| `action` | `string` | (Opcional) Se presente e igual a `"classified"`, indica que a triagem terminou. |
| `details` | `object` | (Opcional) Contém o objeto `ClassificationResponse` completo se `action="classified"`. |
