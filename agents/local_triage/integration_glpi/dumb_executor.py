import os
import sys
import json
from typing import Dict, Any

# Ensure we can import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from agents.local_triage.triage_core.graph import app
from agents.local_triage.triage_core.state import AgentState
from langchain_core.messages import HumanMessage

# Placeholder for real GLPI Mapper
# from agents.local_triage.integration_glpi.glpi_mapper import map_to_glpi
# from agents.local_triage.integration_glpi.glpi_client import GLPIClient

async def run_agent_executor(user_input: str) -> Dict[str, Any]:
    """
    Dumb Executor:
    1. Calls Triage Core (Immutable).
    2. Receives Final State (Contract).
    3. Prints/Returns JSON for the external system.
    """
    print(f"--- [Executor] Received: {user_input} ---")
    
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "pinned_request": user_input,
        "data": {},
        "missing_fields": [],
        "is_complete": False
    }
    
    final_state = await app.ainvoke(initial_state)
    
    payload = final_state.get("output_payload")
    if not payload:
        # Fallback if result_node didn't run or failed
        payload = {
            "error": "No payload returned from Core",
            "raw_state": str(final_state)
        }
        
    print(f"--- [Executor] Output Contract: ---")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    # Integration Logic (Mocked for now or strictly separated)
    if payload.get("complete"):
        print(">>> TRIGGERING GLPI CREATION (Integration Layer) <<<")
        # ticket_id = create_ticket(payload["data"])
        # return {"status": "success", "ticket_id": ticket_id}
        pass
    else:
        print(">>> RETURNING QUESTION TO USER (Integration Layer) <<<")
        # return {"status": "inquiry", "message": payload["messages"][-1]}
        pass
        
    return payload

if __name__ == "__main__":
    import asyncio
    # Simple self-test
    asyncio.run(run_agent_executor("O mouse quebrou"))
