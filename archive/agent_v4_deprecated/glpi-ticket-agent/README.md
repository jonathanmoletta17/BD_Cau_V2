
# Ticket Agent V2 (Reset/Clean State)

Este projeto contém o Agente de IA para triagem de tickets do GLPI.

## Estado Atual (Pós-Limpeza)
O agente foi "resetado". A lógica antiga foi arquivada e agora ele é uma plataforma pronta para novas definições.

### Estrutura
- `src/index.ts`: Servidor API minimalista (Porta 8000).
- `src/services/`: Clientes de conexão (GLPI, LLM/Ollama).
- `src/agent/`: Lógica do Agente (Atualmente vazia/esqueleto).

## Como Rodar

1. **Dependências**:
   ```bash
   npm install
   ```

2. **Inicar (Dev)**:
   ```bash
   npm start
   ```

3. **Testar Sanidade**:
   ```bash
   npm test
   ```

## Variáveis de Ambiente
O agente lê o arquivo `.env` da raiz do monorepo (`../../.env`). Certifique-se de configurar:
- `LLM_BASE_URL` (Ollama)
- `GLPI_PROD_URL_CONFIG` (GLPI)
