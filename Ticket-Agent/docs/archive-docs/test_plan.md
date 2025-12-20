# Comprehensive Test Plan for Triage Core

## Goals
Verify the robustness of the "Clean Core" with focus on:
1.  **Context Retention**: Can the agent hold a conversation over multiple turns?
2.  **Adaptive Routing**: Can the agent change course if the user changes their mind?
3.  **Resilience**: Can the agent handle partial errors and recover?
4.  **Fail-safe**: Does the agent correctly give up (Handover) when stuck?

## Test Cases

### 1. Happy Path: Multi-turn Printer Issue
*   **Input**: "Minha impressora não funciona"
*   **Expected**: Agent asks "Qual a impressora/modelo?"
*   **Input**: "É a Zebra de etiquetas"
*   **Expected**: Extractor parses "Zebra", intent `PRINTER_ISSUE`, Complete=True.

### 2. Edge Case: Intent Switching
*   **Input**: "Preciso de acesso à VPN"
*   **Expected**: Agent asks for "Login/User"
*   **Input**: "Na verdade, deixa pra lá, preciso de um mouse novo"
*   **Expected**: Router re-classifies to `EQUIPMENT_REQUEST`. Agent asks for "Justification" (or completes if "new mouse" is enough).

### 3. Edge Case: Validation Recovery (2 Strikes)
*   **Input**: "Quero um monitor"
*   **Agent**: "Qual o motivo?"
*   **Input**: "batata" (Fail 1)
*   **Input**: "cenoura" (Fail 2)
*   **Input**: "O antigo queimou" (Success 3)
*   **Expected**: `justification` = "O antigo queimou", Complete=True, `PENDING_MANUAL_TRIAGE` NOT present.

### 4. Failure Mode: 3-Strike Handover
*   **Input**: "Preciso de acesso"
*   **Agent**: "Qual sistema/tipo de acesso?" (or similar)
*   **Input**: "não sei" (Fail 1)
*   **Input**: "aaa" (Fail 2)
*   **Input**: "bbb" (Fail 3)
*   **Expected**: `data["justification"]` (or relevant field) == `PENDING_MANUAL_TRIAGE`. Complete=True.

## Implementation
*   File: `local-triage-core-clean/tests/exhaustive_test_suite.py` (New file)
*   Use `asyncio` and `langgraph` state simulation.
