# Universal Prompt: Governance Update Protocol

## Context
We are the defined guardians of the "Single Source of Truth". We do not allow ad-hoc changes. Every update to the business rules must follow a rigorous protocol to ensure consistency and avoid technical debt.

## Protocol for Updating Governance
When realizing a Business Rule is obsolete or ambiguous (e.g., "Hardware Issue" vs "Equipment Request"):

### Step 1: Contextual Reality Check
*   **Premise:** Does this rule match physical reality?
*   **Action:** Explicitly list the operational constraints.
    *   *Example:* "We do not check personal equipment." "We only support patrimonial assets."

### Step 2: Logical Distinction (Splitting)
*   If a concept is too broad, split it based on **User Intent**, not System capability.
    *   **Type A (Incident):** "It broke." (Priority: High).
    *   **Type B (Request):** "I want new." (Priority: Normal).
*   **Constraint:** The agent must infer this distinction from natural language, not by asking "Is this an incident?".

### Step 3: Formal Instruction (The Output)
Produce a directive that explicitly:
1.  **Removes** the obsolete concept (e.g., "Delete HARDWARE_ISSUE").
2.  **Redirects** the logic (e.g., "Absorb into EQUIPMENT_REQUEST -> Incident").
3.  **Cleans** the artifacts (e.g., "Update MDD", "Update Operational Policies").

## Output Format
Your output must be a ready-to-execute instruction block:
*   **target_doc:** [DOC_ID]
*   **action:** [REMOVE | UPDATE | SPLIT]
*   **justification:** [WHY]
*   **new_logic:** [EXACT_TEXT_TO_INSERT]
