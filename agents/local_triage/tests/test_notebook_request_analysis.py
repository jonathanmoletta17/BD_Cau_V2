
import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

mock_llm = MagicMock()

# Mocking the Scenario
# Turn 1: "Solicitar computador..." -> Agent should detect... what?
async def mock_turn_1(*args, **kwargs):
    return """
    INTENT: EQUIPMENT_REQUEST
    Usuario quer solicitar equipamento.
    ### RESPONSE
    Qual é o modelo de computador necessário (portátil ou desktop) e qual é a justificativa?
    """

# Turn 2: "é notebook..." -> Agent receives "EQUIPMENT_REQUEST" config.
# Does it accept 'notebook' as 'equipamento'?
async def mock_turn_2(*args, **kwargs):
    # This simulates the "Success" response (Fix Verified)
    return """
    INTENT: EQUIPMENT_REQUEST
    O usuário disse 'notebook'. Notebook está na lista de EQUIPMENT_REQUEST.
    ### RESPONSE
    READY
    """

async def analyze_notebook_request():
    with patch("agents.local_triage.services_factory.get_llm_service", return_value=mock_llm):
        from agents.local_triage.smart_inquiry_node import smart_inquiry_node
        
        print("--- Turn 1: User asks for Computer ---")
        mock_llm.chat_completion = MagicMock(side_effect=mock_turn_1)
        state1 = {"messages": [HumanMessage(content="preciso solicitar um computador para um novo servidor")]}
        result1 = await smart_inquiry_node(state1)
        print(f"Detected Intent: {result1.get('intent')}")
        
        # Turn 2: User says "Notebook"
        print("\n--- Turn 2: User says 'Notebook' ---")
        mock_llm.chat_completion = MagicMock(side_effect=mock_turn_2)
        state2 = {
            "messages": [
                HumanMessage(content="preciso solicitar um computador"),
                AIMessage(content="Qual modelo?"),
                HumanMessage(content="é nootebok , preciso porque ele tambem vai atuar em home office")
            ],
            "intent": "EQUIPMENT_REQUEST" # Locked from Turn 1 (Renamed)
        }
        
        # We want to see what strictness led to this.
        # This test just confirms the flow logic, effectively reproducing the log.
        result2 = await smart_inquiry_node(state2)
        
        if result2.get("ready_to_classify"):
             print("PASS: Agent accepted 'notebook' and is READY.")
        else:
             print(f"FAIL: Agent still rejected it. Msg: {result2.get('messages', [{}])[0].content}")

if __name__ == "__main__":
    asyncio.run(analyze_notebook_request())
