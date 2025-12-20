
import asyncio
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

mock_llm = MagicMock()

# Sample JSON from get_system_info.py
SAMPLE_JSON = {
    "system": {
        "hostname": "DESKTOP-TEST",
        "os": "Microsoft Windows 11 Pro",
        "build": "22631",
        "architecture": "AMD64"
    },
    "network": {
        "ip": "192.168.1.105"
    },
    "hardware": {
        "serial_number": "PF3X2Y1Z",
        "battery": "Not Detected"
    },
    "monitors": []
}

async def test_parsing():
    # Mock services so we don't actually call LLM if logic bypass fails
    with patch("agents.local_triage.services_factory.get_llm_service", return_value=mock_llm):
        from agents.local_triage.smart_inquiry_node import smart_inquiry_node
        
        # Simulate User pasting the JSON
        user_msg = f"Aqui está o relatório: {json.dumps(SAMPLE_JSON)}"
        state = {"messages": [HumanMessage(content=user_msg)], "data": {}}
        
        print("--- Testing System Info Parsing ---")
        result = await smart_inquiry_node(state)
        
        print(f"Result Messages: {result.get('messages')}")
        new_data = result.get("data", {})
        print(f"Extracted Data: {new_data}")
        
        # Assertions
        if new_data.get("hostname") == "DESKTOP-TEST":
             print("PASS: Hostname extracted.")
        else:
             print("FAIL: Hostname mismatch.")

        if new_data.get("serial_number") == "PF3X2Y1Z":
             print("PASS: Serial Number extracted.")
        else:
             print("FAIL: Serial Number mismatch.")
             
        if "Obrigado! Recebi" in result["messages"][0].content:
             print("PASS: Confirmation message correct.")
        else:
             print("FAIL: Confirmation message missing.")

if __name__ == "__main__":
    asyncio.run(test_parsing())
