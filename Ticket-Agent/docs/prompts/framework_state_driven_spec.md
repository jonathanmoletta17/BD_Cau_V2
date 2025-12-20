# Universal Prompt: State-Driven Architecture Definition

## Context
We are implementing a **State-Driven System**. This prompt helps define the "Logical Constitution" of that system.

## The Paradigm
*   **Chat:** Just an input/output channel.
*   **State:** The only source of truth.
*   **Code:** The state machine that transitions logic based on State, not Chat.

## Metadata Definition Task
For the functionality **[FEATURE_NAME]**, explicit define:

### 1. The State Object
Define the precise JSON schema that represents knowledge.
```json
{
  "field_1": "type (required)",
  "field_2": "type (optional)"
}
```

### 2. Inference Policy (Silent Extraction)
*   **What can be assumed?** (e.g., "If user says 'mouse', assume 'peripherals'").
*   **What must be explicit?** (e.g., "Confirmation of shipping address").

### 3. Error Policy (The Guardrails)
*   **Retry Logic:** How many times do we ask for missing data? (Standard: 3).
*   **Fallout:** What happens after max retries? (e.g., Handover to human).

## Output
Produce a Markdown specification defining these three pillars (Object, Inference, Error) for the requested feature.
