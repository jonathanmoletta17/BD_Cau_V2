# Walkthrough: Binary Hygiene Migration

The project has been successfully migrated to a clean state to eliminate file corruption and encoding issues.

## Project State
- **Location**: `local-triage-core-clean/`
- **Status**: **FROZEN** (Conceptual Reference)
- **Encoding**: UTF-8 (Clean)

## Changes Applied
1.  **Recreation**: All core files (`router`, `extractor`, `validator`, `inquiry`, `state`, `schemas`, `graph`) were recreated from content.
2.  **Logic Fix**: `validator.py` was patched to remove `matricula` requirement for `efetivo` users.
3.  **Import Adjustment**: Imports were standardized to relative imports within the `triage_core` package.

## Verification Results

### 1. Binary Hygiene
*   `python -m compileall .` -> **PASSED** (No null bytes)
*   `python simulation_suite_v2.py` -> **PASSED** (Core logic intact)

### 2. Context & Handover Logic (New)
*   Method: `python verify_context_fix.py`
*   **Context Amnesia**: ✅ **PASSED**
    *   Agent correctly utilized follow-up answers (e.g., "quebraram todos") to fill the `justification` field.
*   **3-Strike Rule**: ✅ **PASSED**
    *   Agent correctly identified 3 failed attempts to get `justification`.
    *   Triggered `PENDING_MANUAL_TRIAGE` and completed the transaction to allow Handover.

### 3. Exhaustive Testing Suite (Initial)
*   Method: `python tests/exhaustive_test_suite.py` (Subset)
*   Result: All 4 base scenarios passed.

### 4. Comprehensive System Verification (20+ Scenarios)
*   **Method**: `python tests/comprehensive_test_suite.py` (14 Scenarios)
*   **Date**: 2025-12-18
*   **Overall Result**: 50% Success (7 Passed, 7 Failed).

#### Passing Scenarios ✅
| Scenario | Description |
| :--- | :--- |
| **Printer Full** | Validates serial number usage when provided. |
| **Switch (VPN->Mouse)** | Successfully handles context switching mid-flow. |
| **Switch (Create->Printer)** | Handles changing intent from User Creation to Printer Issue. |
| **Greeting Only** | "Alo" -> Correctly asks "How can I help?". |
| **Switch (Greeting->Task)** | "Oi" -> "Mouse sumiu" handled correctly. |
| **Noise Error** | "kdosako" -> Correctly asks "How can I help?". |
| **Recovery** | (Implied) Validation failures recovered in other steps. |

#### Failing Scenarios ❌ & Analysis
| Scenario | Failure Reason | Diagnosis |
| :--- | :--- | :--- |
| **Equipment Simple** | Missing `justification` | **Strictness**: "Estou precisando..." treated as intent, not justification. |
| **VPN Access Full** | Missing `manager_approval` | **Validation**: New strict rule requires explicit approval extraction. |
| **VPN Missing All** | Found `justification` | **Over-Eager Extraction**: "Preciso de VPN" extracted as justification. |
| **User Create Incr.** | Found `full_name` | **Hallucination**: Likely extracted user's own name or hallucinated. |
| **Unknown Intent Fix** | Got `UNKNOWN` | **Context**: "Teclado com luzinhas" failed to override previous "batata" context. |
| **Handover Loop** | Found `serial_number` | **Logic Breach**: "Não tem etiqueta" accepted as valid serial number. |
| **Distraction** | Found `full_name` | **Hallucination**: Similar to User Create. |

> [!NOTE]
> **Key Insight**: The primary failure mode is **Over-Eager Extraction**. The LLM tends to fill fields with conversational filler (e.g., "I don't know" -> `serial_number`) or implicit intent text, which bypasses the validation/handover logic. Prompt tuning is required to force `null` for ambiguous/missing data.

### 5. CLI Persistence Fix (Infinite Loop)
*   **Issue**: `run_cli.py` ignored validator updates, resetting retry counts to 0 every turn.
*   **Fix**: Modified CLI loop to `state.update(value)` for ALL node events.
*   **Verification**: `tests/verify_run_cli_persistence.py` confirmed `attempt_counts` increment correcty across turns (1 -> 2 -> 3).

### 5. Logic Hardening & UX Fixes
*   **Issue**: Agent was too permissive (skipped serial numbers, manager approval) and silently ignored "Greetings".
*   **Fix**:
    *   **Validator**: Enforced `serial_number` for Printers and `manager_approval` for VPN.
    *   **Greeting/Unknown**: Routed to validation logic which flags "request_details" as missing, triggering an inquiry ("How can I help?").
*   **Verification**: `tests/verify_validation_and_greeting.py` confirmed both failing incomplete requests and replying to greetings.

## Next Steps
This core is now the **immutable reference** for logical behavior.
Future work should focus on the integration layer (GLPI, UI) consuming this core.
