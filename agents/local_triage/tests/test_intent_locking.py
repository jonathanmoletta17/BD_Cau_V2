
import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

mock_llm = MagicMock()

# Scenario 1: First turn - Detect Intent
async def mock_first_turn(*args, **kwargs):
    return """
    INTENT: PERIPHERALS_REQUEST
    Usuario quer mouse.
    ### RESPONSE
    Qual modelo?
    """

# Scenario 2: Second turn - Locked Intent (Should respect lock)
async def mock_second_turn(*args, **kwargs):
    return """
    INTENT: PERIPHERALS_REQUEST
    Confirmado modelo.
    ### RESPONSE
    READY
    """

mock_llm.chat_completion = mock_first_turn

async def test_locking():
    with patch("agents.local_triage.services_factory.get_llm_service", return_value=mock_llm):
        from agents.local_triage.smart_inquiry_node import smart_inquiry_node
        
        print("--- Turn 1: Initial Detection ---")
        state = {"messages": [HumanMessage(content="Preciso de um mouse")]}
        # First call
        result1 = await smart_inquiry_node(state)
        
        detected_intent = result1.get("intent")
        print(f"Detected Intent: {detected_intent}")
        
        if detected_intent != "PERIPHERALS_REQUEST":
            print("FAIL: Did not detect intent.")
            return

        print("--- Turn 2: Locked State ---")
        # Simulate state persistence
        state["intent"] = detected_intent
        state["messages"].append(AIMessage(content="Qual modelo?"))
        state["messages"].append(HumanMessage(content="Lenovo"))
        
        mock_llm.chat_completion = MagicMock(side_effect=mock_second_turn)
        
        # We want to verify if the LLM received the LOCKED config
        # We spy on the call args of chat_completion
        result2 = await smart_inquiry_node(state)
        
        # Check call args
        call_args = mock_llm.chat_completion.call_args
        system_prompt = call_args[0][0][0]["content"]
        
        if "INTENÇÃO ATUAL: PERIPHERALS_REQUEST" in system_prompt:
            print("PASS: System Prompt reflects LOCKED intent.")
        else:
            print("FAIL: System Prompt does not show locked intent.")
            print(f"Prompt snippet: {system_prompt[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_locking())
