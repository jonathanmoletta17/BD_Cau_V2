# Strategy: System Info & Smart Intents

**Objective**: Automate data collection (Serial, IP) to reduce friction and eliminate the "Patrimony Loop".

## 1. Intent Refinement (Completed)
We identified that "Mouse" request was triggering `HARDWARE_ISSUE` (Consolation/Repair) instead of `PERIPHERALS_REQUEST` (Replacement).
- **Action**: Removed `mouse`, `teclado` from `HARDWARE_ISSUE` keywords.
- **Result**: "Meu mouse quebrou" will now match `PERIPHERALS_REQUEST`.
- **Policy**: `PERIPHERALS_REQUEST` does **NOT** require patrimony. Loop fixed.

## 2. System Info Tool Analysis
The script `tools/get_system_info.py` is comprehensive. It collects:
- Hostname, OS, IP.
- Serial Number (Crucial for cross-referencing).
- Disk Space, Battery, Monitors (Detects serials too!).

### Architectural Challenge
*   **Agent B** runs in Docker (Linux).
*   **User** uses Windows Host.
*   The Agent cannot run `subprocess.call` on the User's machine through the chat window.

### Integration Proposal
**Scenario A: Desktop Agent (Ideal)**
A small Python daemon runs on the user's PC. The Chat Interface connects to `localhost:AgentPort` to fetch this JSON before starting the chat.

**Scenario B: User-Assisted (Immediate)**
The Agent can say: *"Para facilitar, execute o script de diagnóstico e cole o resultado aqui."*
Then, `smart_inquiry_node` parses the JSON and fills the Slots automatically.

**Scenario C: Chainlit Feature (Advanced)**
If using Chainlit React Client, we can inject a JS instruction to fetch basic info (User Agent, maybe Logic ID if integrated with SSO), but Hardware Serial is restricted by Browser Sandbox.

**Recommendation**: Start with **Scenario B** (Parsing JSON input) or integrate into a future **Desktop Launcher**.

## 3. Data Strategy
- **IP Address**: Capture from `get_system_info` or Request Header (X-Forwarded-For).
- **Serial Number**: If collected, query GLPI API to find the assigned asset `id`.
- **Cross-Reference**: Use `GLPIClient.search_assets(serial=X)` to silently populate the `patrimonio` / `inventory_number` field.

This documentation serves as the blueprint for the next development phase.
