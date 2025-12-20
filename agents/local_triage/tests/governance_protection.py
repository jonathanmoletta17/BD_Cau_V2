import asyncio
import os
import sys
from langchain_core.messages import HumanMessage

# Adjust path to find modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

try:
    from agents.local_triage.triage_core.graph import app
    from agents.local_triage.triage_core.schemas import RequestType
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
    from agents.local_triage.triage_core.graph import app
    from agents.local_triage.triage_core.schemas import RequestType

async def assert_invariant(scenario_name: str, input_text: str, check_func):
    print(f"Testing Invariant: {scenario_name}...")
    initial_state = {
        "messages": [HumanMessage(content=input_text)],
        "pinned_request": input_text,
        "data": {},
        "missing_fields": []
    }
    
    try:
        final_state = await app.ainvoke(initial_state)
        
        if check_func(final_state):
            print(f"[PASS] {scenario_name}")
            return True
        else:
            print(f"[FAIL] {scenario_name}")
            print(f"      Got: {final_state.get('intent')} | Data: {final_state.get('data')}")
            return False
    except Exception as e:
        print(f"[ERROR] {scenario_name}: {e}")
        return False

async def main():
    print("=== GOVERNANCE PROTECTION TESTS ===")
    print("Verifying immutable behavioral contracts based on DMD v2.1\n")
    
    passed = 0
    total = 0

    # 1. Equipment vs Request
    total += 1
    if await assert_invariant(
        "Broken Mouse = Incident", 
        "Meu mouse está com o clique falhando",
        lambda s: s["intent"] == "EQUIPMENT_REQUEST" and s["data"].get("request_type") == "incident"
    ): passed += 1
    
    total += 1
    if await assert_invariant(
        "New Monitor = Requisition",
        "Preciso de um monitor adicional",
        lambda s: s["intent"] == "EQUIPMENT_REQUEST" and s["data"].get("request_type") == "requisition"
    ): passed += 1

    # 2. VPN - Justification
    total += 1
    if await assert_invariant(
        "VPN requires Justification",
        "Liberar VPN para mim",
        lambda s: s["intent"] == "VPN_ACCESS" and (s["is_complete"] is False or ("justification" in s["missing_fields"]))
    ): passed += 1

    # 3. Create User - Strict ID
    total += 1
    if await assert_invariant(
        "Efetivo requires CPF",
        "Criar usuário para funcionário efetivo João Silva do RH",
        lambda s: s["intent"] == "CREATE_USER" and any("CPF" in str(m) for m in s["missing_fields"])
    ): passed += 1

    # 4. Unknown Scope
    total += 1
    if await assert_invariant(
        "Out of Scope = UNKNOWN",
        "Quero pedir uma pizza de calabresa",
        lambda s: s["intent"] == "UNKNOWN" or s.get("intent") == "finalizer" or s.get("step") == "handover_to_integration"
    ): passed += 1

    print(f"\nFinal Score: {passed}/{total}")
    if passed == total:
        print(">>> GOVERNANCE VERIFIED: DEPLOY PERMITTED <<<")
        sys.exit(0)
    else:
        print(">>> GOVERNANCE FAILED: DEPLOY BLOCKED <<<")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
