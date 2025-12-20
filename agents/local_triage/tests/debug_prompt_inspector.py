
import asyncio
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

mock_llm_service = MagicMock()

async def mock_chat_completion(messages, options=None):
    # We don't care about the result, we care about the 'messages' passed in
    print("\n[DEBUGGER] --- SYSTEM PROMPT ---")
    print(messages[0]['content'])
    print("\n[DEBUGGER] --- USER PROMPT ---")
    print(messages[1]['content'])
    return "### RESPONSE\nDEBUG_DONE"

async def debug_prompt_construction():
    mock_llm_service.chat_completion = mock_chat_completion
    
    with patch("agents.local_triage.services_factory.get_llm_service", return_value=mock_llm_service):
        from agents.local_triage.smart_inquiry_node import smart_inquiry_node
        
        # Recreating the User's Conversation History
        history = [
            HumanMessage(content="preciso solicitar um computador para um novo servidor ltoado em nosso departamento"),
            AIMessage(content="Qual tipo de equipamento você precisa (notebook/laptop) e qual é o modelo específico? Qual é a justificativa para essa solicitação?"),
            HumanMessage(content="é nootebok , preciso porque ele tambem vai atuar em home office"),
            AIMessage(content="Qual é o modelo de notebook que você precisa? (Ex: especificação do processador, memória RAM, etc.)"),
            HumanMessage(content="qualquer um"),
            AIMessage(content="Qual é o motivo exato da solicitação de um notebook? (Ex: Defeito, Novo Funcionário, Home Office)"),
            HumanMessage(content="Home Office") # The point where it looped
        ]
        
        state = {
            "messages": history,
            "intent": "EQUIPMENT_REQUEST" # Locked
        }
        
        print(f"--- Simulating Node Execution with {len(history)} messages ---")
        await smart_inquiry_node(state)

if __name__ == "__main__":
    asyncio.run(debug_prompt_construction())
