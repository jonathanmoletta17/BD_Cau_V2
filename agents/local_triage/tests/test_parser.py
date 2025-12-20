
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

import asyncio
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage

mock_llm = MagicMock()

async def mock_response_reasoning(*args, **kwargs):
    return """
    A intenção do usuário é criar um ticket.
    Faltam dados de equipamento.
    Vou perguntar o modelo.
    ### RESPONSE
    Qual é o modelo do equipamento?
    """

mock_llm.chat_completion = mock_response_reasoning

async def test_parser():
    with patch("agents.local_triage.services_factory.get_llm_service", return_value=mock_llm):
        from agents.local_triage.smart_inquiry_node import smart_inquiry_node
        
        state = {"messages": [HumanMessage(content="Preciso de ajuda")]}
        result = await smart_inquiry_node(state)
        
        message = result["messages"][0].content
        print(f"Final Message: '{message}'")
        
        if "### RESPONSE" in message or "A intenção" in message:
            print("FAIL: Parser did not clean the output.")
        elif message.strip() == "Qual é o modelo do equipamento?":
            print("PASS: Parser cleaned the output correctly.")
        else:
            print(f"FAIL: Unexpected output '{message}'")

if __name__ == "__main__":
    asyncio.run(test_parser())
