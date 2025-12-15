import asyncio
import os
import sys
import json
from pathlib import Path

# Setup Python Path to include agents/triage
current_dir = Path(__file__).resolve().parent.parent # .
triage_path = current_dir / "agents" / "triage"
sys.path.append(str(triage_path))

# Override ENV for Local Test
os.environ["ENV"] = "test"
# Fix local LLM access if needed (assuming user has port 9000 open for vLLM)
# If .env says host.docker.internal, we usually need localhost for windows host usage
os.environ["LLM_BASE_URL"] = "http://localhost:9000/v1" 

# Manual Import after env set
try:
    from main import Container
    from src.models import ChatMessage
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Path is: {sys.path}")
    sys.exit(1)

async def run_tests():
    # Output to file
    log_file = current_dir / "tests" / "verification_log.txt"
    log_file.parent.mkdir(exist_ok=True)
    
    with open(log_file, "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            f.write(msg + "\n")

        log("🚀 Iniciando Teste de Integração (Triage Agent)...")
        
        # 1. Instantiate Container
        container = Container()
        
        # 2. Sync Categories (Vital for classifier)
        log("🔄 Sincronizando Categorias (Mock/Real)...")
        try:
            await container.sync_service.sync_categories()
            log(f"✅ Categorias carregadas: {len(container.sync_service.categories)}")
        except Exception as e:
            log(f"⚠️ Erro no sync (pode ser fatal se não tiver cache): {e}")

        # 3. Define Test Scenarios
        scenarios = [
            "Meu computador Dell não está ligando, a luz pisca laranja.",
            "Preciso que liberem meu acesso ao sistema GLPI, esqueci a senha.",
            "A impressora do RH está manchando as folhas de toner.",
            "A internet no setor de TI está caindo toda hora.",
            "Gostaria de solicitar um novo monitor para o estagiário."
        ]

        results = []

        for i, user_input in enumerate(scenarios, 1):
            log(f"\n--- Cenário {i}: '{user_input}' ---")
            
            # Simulate Chat Flow
            history = [ChatMessage(role="user", content=user_input)]
            
            try:
                # 1. Chat Response
                response = await container.chat_service.handle_message(history)
                
                log(f"🤖 Agente diz: {response.get('content')[:100]}...")
                
                if response.get("action") == "classified":
                    log("✅ EUREKA! Classificação detectada.")
                    details = response.get("details", {})
                    log(f"   > Categoria: {details.get('selected_category_name')} (ID: {details.get('selected_category_id')})")
                    log(f"   > Urgência: {details.get('urgency')} | Impacto: {details.get('impact')}")
                    
                    # 2. Simulate Ticket Creation (The "Action")
                    log("📝 Criando Ticket no GLPI...")
                    ticket_res = await container.glpi_client.create_ticket(
                        title=f"[TESTE IA] {user_input[:40]}",
                        description=user_input,
                        category_id=details.get("selected_category_id"),
                        urgency=details.get("urgency"),
                        impact=details.get("impact"),
                        ai_analysis=details.get("reasoning", "Teste Automatizado")
                    )
                    
                    tid = ticket_res.get("id")
                    log(f"🎉 TICKET CRIADO: #{tid}")
                    results.append({"scenario": user_input, "status": "SUCCESS", "id": tid, "cat": details.get("selected_category_name")})
                else:
                    log("⚠️ Falha: Agente não disparou classificação.")
                    results.append({"scenario": user_input, "status": "FAILED_NO_action", "response": response})
                    
            except Exception as e:
                log(f"❌ Erro Crítico: {e}")
                results.append({"scenario": user_input, "status": "ERROR", "error": str(e)})

        # Summary
        log("\n\n=== RESUMO DOS TESTES ===")
        success_count = len([r for r in results if r["status"] == "SUCCESS"])
        for r in results:
            log(f"[{r['status']}] {r['scenario'][:30]}... -> Ticket {r.get('id', 'N/A')} ({r.get('cat', '-')})")
            
        if success_count == len(scenarios):
            log("\n✅ TODOS OS 5 TESTES PASSARAM COM SUCESSO!")
        else:
            log(f"\n⚠️ Apenas {success_count}/{len(scenarios)} passaram.")

if __name__ == "__main__":
    asyncio.run(run_tests())
