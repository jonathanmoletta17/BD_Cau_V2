
import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

mock_llm = MagicMock()

# Scenario 1: Vague Input "Oi" -> Should NOT Lock
async def mock_vague_input(*args, **kwargs):
    return """
    Análise: O usuário apenas cumprimentou. Não há intenção clara ainda.
    ### RESPONSE
    Olá! Como posso ajudar com TI hoje?
    """

# Scenario 2: Clear Input "Mouse quebrou" -> Should Lock
async def mock_clear_input(*args, **kwargs):
    return """
    INTENT: HARDWARE_ISSUE
    O usuário relatou quebra de equipamento.
    ### RESPONSE
    Qual o patrimônio?
    """

async def test_safety():
    with patch("agents.local_triage.services_factory.get_llm_service", return_value=mock_llm):
        from agents.local_triage.smart_inquiry_node import smart_inquiry_node
        
        print("--- Test 1: Vague Input ('Oi') ---")
        mock_llm.chat_completion = MagicMock(side_effect=mock_vague_input)
        
        state1 = {"messages": [HumanMessage(content="Oi")]}
        result1 = await smart_inquiry_node(state1)
        
        intent1 = result1.get("intent")
        print(f"Result Intent: {intent1}")
        
        if intent1 is None:
            print("PASS: System did NOT lock on vague input.")
        else:
            print(f"FAIL: System locked prematurely on '{intent1}'.")

        print("\n--- Test 2: Clear Input ('Mouse quebrou') ---")
        mock_llm.chat_completion = MagicMock(side_effect=mock_clear_input)
        
        state2 = {"messages": [HumanMessage(content="Meu mouse quebrou")]}
        result2 = await smart_inquiry_node(state2)
        
        intent2 = result2.get("intent")
        print(f"Result Intent: {intent2}")
        
        if intent2 == "HARDWARE_ISSUE":
            print("PASS: System locked correctly on clear input.")
        else:
            print(f"FAIL: Should have locked, but got '{intent2}'.")

if __name__ == "__main__":
    asyncio.run(test_safety())
