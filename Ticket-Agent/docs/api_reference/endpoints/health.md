# Endpoint: Health Check (`/health`)

Verifica a saúde da aplicação, versão e status dos componentes críticos (como carregamento de categorias).

## Detalhes da Requisição

- **URL**: `/health`
- **Método HTTP**: `GET`
- **Autenticação**: Nenhuma

## Parâmetros
Nenhum.

## Resposta (Response)

### Exemplo de Sucesso (`200 OK`)
```json
{
  "status": "healthy",
  "version": "2.1.0-fullcontext",
  "ready": true,
  "details": {
    "loaded_categories": 165,
    "architecture": "Full Context (No RAG)"
  }
}
```

### Campos da Resposta

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `status` | `string` | Estado geral (`healthy` ou `unhealthy`). |
| `version` | `string` | Versão do deploy atual. |
| `ready` | `boolean` | `true` se o agente carregou as categorias e está pronto para classificar. |
| `details` | `object` | Informações de diagnóstico adicionais. |
