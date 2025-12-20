# Ticket Agent CLI

Agente de triagem de tickets via terminal.

## Pré-requisitos
- Node.js 18+
- Python 3.10+

## Instalação

```bash
npm install
cd python_ai
# Configurar venv se necessário
```

## Como usar

1. **Inicie o serviço de IA (Python)** em um terminal:
   ```bash
   cd python_ai
   .\venv\Scripts\python main.py
   ```
   *Aguarde aparecer "Uvicorn running..."*

2. **Inicie o Agente** em outro terminal:
   ```bash
   npm start
   ```

## Estrutura

- `agent_cli.ts`: Interface de linha de comando interativa.
- `server/triage/`: Núcleo do agente (Grafo, Extrator, Regras, Templates).
- `python_ai/`: Serviço de Inteligência Artificial (LLM/NLP).
- `shared/schema.ts`: Definições de tipos e esquemas Zod.
