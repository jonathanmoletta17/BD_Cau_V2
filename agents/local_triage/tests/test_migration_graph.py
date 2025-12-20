import sys
import os
import asyncio
from pathlib import Path
from langchain_core.messages import HumanMessage

# Add project root
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

# CRITICAL: Bootstrap Agent A environment for Engine & Client Support
agent_a_root = project_root / "agents" / "triage"
sys.path.insert(0, str(agent_a_root))

from agents.local_triage.new_graph import app
from agents.local_triage.state import AgentState

async def test_migration():
    print("--- Testing Migrated Graph (Agent B + Engine A) ---")
    
    # Test Case: "Mein mouse quebrou" (Should be viable and classified)
    inputs = {
        "messages": [HumanMessage(content="Meu mouse da Dell quebrou na sala 10")],
        "data": {},
        "ticket_payload": None,
        "classification_result": {},
        "viability_score": 0.0,
        "requester_id": 123
    }
    
    print(f"\nUser Input: {inputs['messages'][0].content}")
    
    try:
        final_state = await app.ainvoke(inputs)
        
        print(f"\n✅ Final State Reached")
        print(f"   Intent: {final_state.get('intent')}")
        print(f"   Viability: {final_state.get('viability_score')}")
        
        if 'ticket_payload' in final_state and final_state['ticket_payload']:
             payload = final_state['ticket_payload']
             input_data = payload.get('input', {})
             print(f"   Payload Title: {input_data.get('name')}")
             print(f"   Category ID: {input_data.get('itilcategories_id')}")
             print("   SUCCESS: Graph Generated Ticket Payload!")
        else:
             print("   WARNING: No ticket payload generated.")
             
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_migration())
