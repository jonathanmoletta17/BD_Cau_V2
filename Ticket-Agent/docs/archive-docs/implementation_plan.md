# Implementation Plan: Context Amnesia & Handover

## Goal
Fix the infinite loop (Context Amnesia) by making nodes context-aware and implement a 3-attempt limit for mandatory fields, triggering a handover (N2) if exceeded.

## Proposed Changes

### 1. State (`state.py`)
Add `attempt_counts` to track how many times a field meant missing.
```python
class AgentState(TypedDict):
    # ... existing fields ...
    attempt_counts: Dict[str, int] # Track retries per field
```

### 2. Router (`nodes/router.py`)
Modify input logic to consider conversation context.
*   **Change**: Construct input using `pinned_request` (context) AND `latest_message` (focus).
*   **Logic**:
    ```python
    input_text = state['pinned_request']
    if state['messages']:
        last_msg = state['messages'][-1]
        if isinstance(last_msg, HumanMessage):
             input_text = f"Context: {state['pinned_request']}\nUser Follow-up: {last_msg.content}"
    ```

### 3. Extractor (`nodes/extractor.py`)
Modify prompt to see the user's answer.
*   **Change**: Similar to Router, pass the conversation history or at least the latest response to the LLM.
*   **Logic**:
    ```python
    request_text = state['pinned_request']
    if state['messages']: # Append latest user response
         # ... logic to append ...
    ```

### 4. Validator (`nodes/validator.py`)
Implement the 3-strike rule.
*   **Logic**:
    *   Initialize `attempt_counts` if missing.
    *   For each missing field detected:
        *   Increment counter.
        *   If counter >= 3:
            *   **Handover**: Set `data[field] = "PENDING_MANUAL_TRIAGE"`.
            *   Remove from `missing` list (so we stop asking).
    *   This naturally resolves `is_complete` to True, exiting the loop.

## Verification
*   **Manual Test (`run_cli.py`)**:
    1.  Start "3 earphones" scenario.
    2.  Agent asks justification.
    3.  User replies "It broke".
    4.  **Expectation**: Agent validates and completes.
*   **Handover Test**:
    1.  Start scenario.
    2.  Agent asks.
    3.  User replies nonsense "potato".
    4.  Agent asks again (Attempt 2).
    5.  User replies "carrot".
    6.  Agent asks again (Attempt 3).
    7.  User replies "banana".
    8.  **Expectation**: Agent sets `PENDING_MANUAL_TRIAGE` and completes.
