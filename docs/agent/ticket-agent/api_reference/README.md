# Documentação da API - Agente de Triagem GLPI V2

## Visão Geral
Esta API fornece serviços de inteligência artificial para triagem, classificação e pré-atendimento de chamados de suporte técnico (GLPI). Ela é construída sobre **FastAPI** e utiliza modelos de linguagem (LLMs) locais via Ollama.

**Base URL**: `http://localhost:8000` (Padrão em Dev)

## Autenticação
Atualmente, a API opera em modo **interno/confiável**.
- **Não há autenticação obrigatória** (Bearer Token ou API Key) implementada nos endpoints HTTP.
- A segurança deve ser provida pela infraestrutura (Firewall, API Gateway, Kubernetes Network Policies) ou rodando em rede localhost restrita.
- As chamadas externas *feitas pela API* (para o GLPI) utilizam `App-Token` e `User-Token` configurados via variáveis de ambiente.

## Versionamento
- **Versão Atual**: `2.1.0-fullcontext`
- A API não utiliza versionamento na URL (ex: `/v1/`). Alterações de contrato (breaking changes) devem ser coordenadas com os clientes.

## Protocolos
- **Formato de Dados**: JSON (`application/json`) para requisição e resposta.
- **Charset**: UTF-8.
- **Tratamento de Erros**:
    - `200 OK`: Sucesso.
    - `422 Unprocessable Entity`: Erro de validação nos dados de entrada (formato JSON inválido ou campos faltando).
    - `500 Internal Server Error`: Falha no processamento (erro no LLM, erro de conexão com GLPI, etc).

## Documentação Complementar

- **[Guia de Integração](GUIDE.md)**: Fluxos de trabalho comuns e melhores práticas de integração.
- **[Modelos de Dados](data_models.md)**: Definição detalhada de todos os objetos, campos e tipos de dados.

## Índice de Endpoints

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | [`/classify`](endpoints/classify.md) | Classifica um texto de chamado em uma categoria GLPI. |
| `POST` | [`/chat`](endpoints/chat.md) | Endpoint conversacional para triagem interativa. |
| `GET` | [`/health`](endpoints/health.md) | Verifica o status e a saúde da aplicação. |
