# Static Analysis Report - Agent B (Local Triage)

## 1. Executive Summary
This report documents the findings from a static code analysis and logic audit of the `agents/local_triage` module. The primary focus was on State Management, Conversational Logic, and Performance Optimization.

**Key Findings:**
1.  **Intent Drift (Critical)**: The agent was re-evaluating user intent at every turn, causing "identity switching". (FIXED)
2.  **Redundant Viability Check (Performance)**: The `viability_node` is executed on every turn but its output is largely ignored by the current routing logic, resulting in wasted latency and tokens.
3.  **Graph Entry Point**: The entry point forces a re-check of viability even when deep in a slot-filling conversation.

---

## 2. Issue Analysis & Fixes

### 2.1 Intent Drift (Identity Crisis)
**Problem:** `smart_inquiry_node.py` evaluated the entire conversation history against *all* possible intents at every turn.
- **Symptom:** User answers a question about "Hardware" with a username, and Agent switches to "Create User" intent.
- **Root Cause:** Lack of state persistence for the identified Intent.
- **Fix Implemented:** "Intent Locking".
    - **Mechanism:** Once an intent is identified (via LLM `INTENT:` output), it is saved to `state["intent"]`.
    - **Enforcement:** In subsequent turns, `smart_inquiry_node` checks for `state["intent"]` and filters the configuration to show *only* the locked intent to the LLM.

### 2.2 Redundant Viability Check
**Problem:** `viability_node.py` prompts the LLM to score conversation viability on *every* message.
**Observation:**
- In `new_graph.py`, the `route_viability` function directs **ALL** traffic to `ask_more` (Smart Inquiry), regardless of the score.
```python
def route_viability(state):
    # ... logic ...
    if score >= 0.5: return "ask_more"
    return "ask_more" # All roads lead to Rome
```
- **Impact:** We are paying for an LLM call (Latency + Cost) that has **zero effect** on the flow control.
- **Risk:** If the user provides a short answer (e.g., "Lenovo") to a slot-filling question, `viability_node` might rate it as "Not Viable" (low score), contaminating the state metadata, even if the flow continues.

**Recommendation:**
- **Short Term:** Implement a "Logic Bypass" in `viability_node`. If `state["intent"]` is present, return `score=1.0` immediately without calling LLM.
- **Long Term:** Remove `viability_node` from the loop for active conversations, or merge its logic into `smart_inquiry_node`.

## 3. Audited Components

| Component | Status | Notes |
| :--- | :--- | :--- |
| `smart_inquiry_node.py` | **OPTIMIZED** | Intent Locking & Output Parser implemented. |
| `viability_node.py` | **INEFFICIENT** | Redundant LLM calls. Needs Logic Bypass. |
| `new_graph.py` | **SAFE** | Routing is safe (favors slot filling) but could be cleaner. |
| `new_nodes_migration.py`| **STABLE** | Context Context aggregation is working correctly. |

## 4. Next Steps
1.  **Apply Logic Bypass** to `viability_node.py` to save tokens/time during slot filling.
2.  Refactor `new_graph.py` to potentially skip `viability` node entirely for subsequent steps (requires Graph topology change).
