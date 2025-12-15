import asyncio
import sys
import os
from pathlib import Path

# Setup Path
current_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(current_dir))

from main import container
from src.models import ChatMessage

TEST_SCENARIOS = [
    {
        "input": "O servidor principal pegou fogo e estamos sem sistema!",
        "expected_urgency": [4, 5],
        "expected_type": 1, # Incident
        "desc": "Critical Server Failure"
    },
    {
        "input": "Gostaria de solicitar um novo mouse para o estagiário.",
        "expected_urgency": [1, 2],
        "expected_type": 2, # Request
        "desc": "Mouse Request"
    },
    {
        "input": "Minha internet está muito lenta hoje, não consigo abrir sites.",
        "expected_urgency": [3],
        "expected_type": 1, # Incident
        "desc": "Slow Internet"
    },
    {
        "input": "Esqueci minha senha do GLPI, preciso resetar.",
        "expected_urgency": [2, 3],
        "expected_type": 1, # Incident (usually)
        "desc": "Password Reset"
    },
    {
        "input": "Preciso que liberem o acesso à pasta de RH na rede.",
        "expected_urgency": [2, 3],
        "expected_type": 2, # Request
        "desc": "Access Request"
    }
]

async def run_tests():
    print("🚀 Starting Extensive Metadata Validation via ChatService...\n")
    
    # Ensure services are initialized
    # container.wire(modules=[__name__]) # If needed
    
    chat_service = container.chat_service
    
    passes = 0
    fails = 0
    
    for scenario in TEST_SCENARIOS:
        print(f"🧪 Testing: {scenario['desc']}")
        print(f"   Input: '{scenario['input']}'")
        
        history = [ChatMessage(role="user", content=scenario['input'])]
        
        try:
            response = await chat_service.handle_message(history)
            
            if response.get("action") != "classified":
                print(f"   ❌ FAILED: Not classified. Response: {response.get('content')[:50]}...")
                fails += 1
                continue
                
            details = response.get("details", {})
            
            # Extract
            got_type = details.get("ticket_type")
            got_urg = details.get("urgency")
            got_cat = details.get("selected_category_name")
            got_title = details.get("suggested_title")
            
            print(f"   --> Analysis: Category='{got_cat}' | Type={got_type} | Urgency={got_urg} | Impact={details.get('impact')}")
            print(f"   --> Generated Title: '{got_title}'")
            
            # Verify Title
            title_ok = got_title and "[" in got_title and "]" in got_title
            title_status = "✅" if title_ok else f"❌ (Expected pattern [Category]...)"
            
            # Verify Type
            type_ok = got_type == scenario['expected_type']
            type_status = "✅" if type_ok else f"❌ (Exp: {scenario['expected_type']})"
            
            # Verify Urgency
            urg_ok = got_urg in scenario['expected_urgency']
            urg_status = "✅" if urg_ok else f"❌ (Exp: {scenario['expected_urgency']})"
            
            print(f"   --> Validation: Type: {type_status} | Urgency: {urg_status} | Title: {title_status}")
            
            if type_ok and urg_ok and title_ok:
                passes += 1
            else:
                fails += 1
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            fails += 1
            
        print("-" * 60)
        
    print(f"\n📊 Summary: {passes} Passed | {fails} Failed | Total {len(TEST_SCENARIOS)}")
    if fails == 0:
        print("✅ ALL TESTS PASSED - Metadata extraction logic is robust.")
    else:
        print("⚠️ SOME TESTS FAILED - Review prompts or logic.")

if __name__ == "__main__":
    asyncio.run(run_tests())
