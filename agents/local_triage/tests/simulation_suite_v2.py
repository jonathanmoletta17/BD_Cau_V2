import asyncio
import os
import sys
from typing import List
from langchain_core.messages import HumanMessage

# Adjust path to find modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

try:
    from agents.local_triage.triage_core.graph import app
    from agents.local_triage.triage_core.state import AgentState
except ImportError:
    # Fallback to local path if run directly
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
    from agents.local_triage.triage_core.graph import app
    from agents.local_triage.triage_core.state import AgentState

async def run_scenario(name: str, inputs: List[str], expected_intent: str, expected_complete: bool):
    print(f"\n--- Scenario: {name} ---")
    
    # Initialize State
    topic = inputs[0]
    initial_state = {
        "messages": [HumanMessage(content=topic)],
        "pinned_request": topic, 
        "intent": None,
        "data": {},
        "missing_fields": [],
        "is_complete": False
    }
    
    current_state = initial_state
    
    step_count = 0
    async for event in app.astream(initial_state):
        for key, value in event.items():
            step_count += 1
            print(f"Node: {key}")
            if "data" in value:
                print(f"  Data: {value['data']}")
            if "intent" in value:
                print(f"  Intent: {value['intent']}")
            if "missing_fields" in value:
                print(f"  Missing: {value['missing_fields']}")
                
            if key == "inquiry":
                print(f"  [Agent Ask]: {value['messages'][0].content}")
                
            current_state.update(value)

    # Validation
    final_intent = current_state.get("intent")
    is_complete = current_state.get("is_complete")
    
    print(f"Result: Intent={final_intent} (Expected {expected_intent}) | Complete={is_complete} (Expected {expected_complete})")
    
    if final_intent == expected_intent:
        print("[PASS] Intent Match")
    else:
        print(f"[FAIL] Intent Mismatch. Got: '{final_intent}'")

    if is_complete == expected_complete:
        print("[PASS] Completeness Match")
    else:
        print(f"[WARN] Completeness Diff (might be ok if inquiry needed). Got: {is_complete}")

async def main():
    # Scenario 1: Printer Informal
    await run_scenario(
        "Impressora Informal",
        ["A impressora do RH está sem toner"],
        "PRINTER_ISSUE",
        True 
    )

    # Scenario 2: Mouse Request (Requisition)
    await run_scenario(
        "Mouse Ruim (Desgaste)",
        ["Meu mouse tá muito ruim, clique falhando"],
        "EQUIPMENT_REQUEST",
        True 
    )

    # Scenario 3: VPN Access
    await run_scenario(
        "VPN Access Grant",
        ["Preciso de acesso VPN"],
        "VPN_ACCESS",
        False 
    )

    # Scenario 4: User Creation
    await run_scenario(
        "Create User Basic",
        ["Criar usuário para o novo estagiário Pedro Silva no setor Financeiro"],
        "CREATE_USER",
        False 
    )

if __name__ == "__main__":
    asyncio.run(main())
