# Ticket Agent Architecture (V2)

## Overview
This project follows a **Semantic Agent** architecture, moving away from rigid state machines (Regex) to LLM-driven State Extraction and Routing.

## Directory Structure (`src/`)

### 1. `core/` (The Brain)
*   **`engine.ts`**: The main orchestration loop. It manages the lifecycle of a request: `Load State -> Input -> Process -> Save State -> Output`.
*   **`types.ts`**: Global type definitions (AgentContext, FlowData).

### 2. `skills/` (The Capabilities)
*   **`extractor.ts`**: Uses LLM to extract structured JSON (Entities) from chat history.
*   **`summarizer.ts`**: Uses LLM to generate Ticket Titles and Descriptions.
*   *(Future)* `classifier.ts`: Decides the intent of the user.

### 3. `services/` (The I/O Layer)
Low-level integrations with external APIs.
*   **`glpi.ts`**: GLPI REST API Client.
*   **`llm_service.ts`**: Wrapper for Ollama/OpenAI.
*   **`asset_service.ts`**: Network scanning/IP lookup.

### 4. `repositories/` (The Memory)
*   **`redis_repository.ts`**: Persists `AgentContext` to Redis.

### 5. `config.ts`
*   Centralized configuration Loader (Environment Variables).

## Core Concepts

### Gateway Pattern (Authentication)
The Agent assumes the user is **already authenticated** by an upstream provider (Frontend/Gateway).
*   The `index.ts` (API Layer) receives `userId`.
*   The `AgentEngine` trusts this `userId` and loads the corresponding session.

### Semantic Extraction
We do not use `if (msg.contains('printer'))`.
Instead, we pass the *entire history* to `extractor.ts`, which returns:
```json
{
  "problemType": "PRINTER",
  "location": "Sala 204",
  "extension": "3321"
}
```
The Engine uses this data to decide if it has enough info to act.
