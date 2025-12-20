# Endpoint: Classificar Chamado (`/classify`)

Este endpoint recebe a descrição de um problema e utiliza Inteligência Artificial para determinar a categoria GLPI mais adequada, além de inferir urgência, impacto e sugerir um título.

## Detalhes da Requisição

- **URL**: `/classify`
- **Método HTTP**: `POST`
- **Autenticação**: Nenhuma (Pública/Interna)
- **Headers**:
    - `Content-Type: application/json`

## Parâmetros
Não há parâmetros de Query ou Path.

## Corpo da Requisição (Request Body)
O corpo deve seguir o modelo `ClassificationRequest`.

| Campo | Tipo | Obrigatório | Descrição |
| :--- | :--- | :---: | :--- |
| `description` | `string` | **Sim** | Texto descrevendo o problema do usuário. |
| `title` | `string` | Não | Título opcional para auxiliar no contexto. |
| `max_candidates` | `int` | Não | Quantas sugestões secundárias retornar (Padrão: 5). |

### Exemplo de Requisição (cURL)
```bash
curl -X POST "http://localhost:8000/classify" \
     -H "Content-Type: application/json" \
     -d '{
           "description": "Estou tentando acessar a pasta de RH na rede mas recebo acesso negado.",
           "title": "Erro de Permissão",
           "max_candidates": 3
         }'
```

## Resposta (Response)
Retorna um objeto JSON seguindo o modelo `ClassificationResponse`.

### Exemplo de Sucesso (`200 OK`)
```json
{
  "selected_category_id": 5744,
  "selected_category_name": "Acesso > Pastas de Rede",
  "confidence": 0.98,
  "reasoning": "O usuário menciona explicitamente 'acesso negado' a uma 'pasta de rede' (RH), o que configura um incidente de permissão de acesso.",
  "ticket_type": 1,
  "urgency": 3,
  "impact": 3,
  "suggested_title": "[Acesso] Erro de Permissão na Pasta RH",
  "candidates": [
    {
      "category_id": 5744,
      "name": "Acesso > Pastas de Rede",
      "score": 1.0,
      "description": ""
    },
    {
      "category_id": 5740,
      "name": "Acesso > Conta de Rede",
      "score": 0.4,
      "description": ""
    }
  ]
}
```

### Códigos de Erro Comuns
- `422 Unprocessable Entity`: Se o campo `description` estiver faltando.
- `500 Internal Server Error`: Se o serviço de classificação falhar (ex: LLM offline ou arquivo de categorias ausente).
