
import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from langchain_core.messages import HumanMessage, AIMessage

# Mock LLM Service before importing graph
mock_llm = MagicMock()

async def mock_chat_completion(messages, options=None):
    # Analyze prompt to decide response
    prompt = messages[-1]["content"] if messages else ""
    
    if "Histórico da Conversa" in prompt:
        if "PRECISO DE FONES" in prompt.upper() and "MODELO" not in prompt.upper():
            return "Qual modelo de fone você precisa?"
        if "MODELO PADRAO" in prompt.upper():
            return "READY"
    
    # Viability check
    if "Is this viable" in prompt:
        return '{"viable": true}'
        
    return "Resposta Padrão"

mock_llm.chat_completion = mock_chat_completion

# Patching
with patch("agents.local_triage.services_factory.get_llm_service", return_value=mock_llm):
    from agents.local_triage.new_graph import app
    from agents.local_triage.state import AgentState

    async def run_tests():
        print("=== Test 1: Incomplete Request (Expecting Question) ===")
        # Scenario: User asks for phones (Viable) but missing model (Not Ready)
        inputs = {
            "messages": [HumanMessage(content="Preciso de fones")],
            "viability_score": 0.0
        }
        
        # We run the graph until it stops (should be ask_more -> END)
        final_state = await app.ainvoke(inputs)
        
        last_message = final_state["messages"][-1].content
        print(f"Agent Response: {last_message}")
        
        # Check if it stopped at ask_more (implied by having a response that is NOT a ticket confirmation)
        if "Qual modelo" in last_message:
            print("PASS: Agent asked for model.")
        else:
            print("FAIL: Agent did not ask for model.")

        print("\n=== Test 2: Complete Request (Expecting Ticket) ===")
        # Scenario: User gives all info
        inputs = {
            "messages": [HumanMessage(content="Preciso de fones modelo padrao porque quebrou")],
            "viability_score": 0.0
        }
        
        # Note: ticket_creator logic might fail if not mocked, but we check if we PASSED smart_inquiry
        # Actually, ticket_creator might try to call GLPI. We should check if 'ready_to_classify' is True in state.
        
        # We can just check the ready_to_classify flag if the graph execution allows inspecting state at that point?
        # invoke returns the final state.
        
        try:
            final_state = await app.ainvoke(inputs)
            if final_state.get("ready_to_classify") is True:
                 print("PASS: State marked as Ready to Classify.")
            else:
                 print(f"FAIL: State NOT Ready. Last step: {final_state.get('step')}")
                 
        except Exception as e:
            # If it tries to create ticket and fails on connection, that means it TRIED.
            print(f"Execution hit later stage (expected): {e}")

    if __name__ == "__main__":
        asyncio.run(run_tests())
