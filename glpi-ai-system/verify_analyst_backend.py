from agents.analyst.analyst_agent import GLPIAnalystAgent
import sys

def verify_analyst():
    print("🚀 Initializing Analyst Agent for Backend Verification...")
    try:
        agent = GLPIAnalystAgent()
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        sys.exit(1)

    queries = [
        "Quantos chamados com urgência Alta?",
        "Qual a sala com mais problemas?",
        "Liste os 3 chamados mais recentes."
    ]
    
    success_count = 0
    
    for i, q in enumerate(queries, 1):
        print(f"\n🧪 Test {i}: '{q}'")
        try:
            response = agent.run(q)
            print(f"✅ Response received ({len(response)} chars)")
            print(f"👉 Output: {response[:150]}...") # Truncate for log cleanliness
            if "Erro" not in response and "Error" not in response:
                success_count += 1
            else:
                print("⚠️  Warning: Response contains error keywords.")
        except Exception as e:
            print(f"❌ Execution failed: {e}")

    print("\n" + "="*50)
    if success_count == len(queries):
        print(f"✅ VERIFICATION PASSED: {success_count}/{len(queries)} tests successful.")
    else:
        print(f"⚠️  VERIFICATION PARTIAL: {success_count}/{len(queries)} tests successful.")

if __name__ == "__main__":
    verify_analyst()
