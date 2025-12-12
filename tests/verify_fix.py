import sys
import os

# Adiciona o diretório glpi-ai-system ao path para importar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "glpi-ai-system")))

from agents.opener.agent import SurgicalOpenerAgent
from agents.opener.schemas import TicketContext

# Configura para usar o Ollama local diretamente
os.environ["LLM_BASE_URL"] = "http://localhost:11434/v1"

import requests
def get_valid_model():
    try:
        resp = requests.get("http://localhost:11434/api/tags")
        if resp.status_code == 200:
            models = [m['name'] for m in resp.json()['models']]
            print(f">> Modelos disponíveis: {models}")
            # Tenta encontrar o Qwen ou usa o primeiro
            for m in models:
                if "qwen" in m.lower():
                    return m
            return models[0] if models else "llama3.1:8b"
    except Exception as e:
        print(f">> Erro ao listar modelos: {e}")
        return "qwen2.5-coder:7b" # Default fallback

# Define o modelo dinamicamente
os.environ["LLM_MODEL_NAME"] = get_valid_model()
print(f">> Usando modelo: {os.environ['LLM_MODEL_NAME']}")

def test_memory():
    print(">> INICIANDO TESTE DE MEMÓRIA DO AGENTE <<")
    agent = SurgicalOpenerAgent()
    
    # 1. Primeira Interação: Usuário reclama do PC
    print("\n[Turno 1] User: tela do pc nao liga")
    ctx = agent.process_ticket("tela do pc nao liga")
    
    resp_1 = ctx.response_to_user or "NO_RESPONSE"
    print(f"[Turno 1] Agent: {resp_1}")
    
    # 2. Segunda Interação: Usuário responde "apagado"
    print("\n[Turno 2] User: apagado")
    ctx = agent.process_ticket("apagado", current_context=ctx)
    
    resp_2 = ctx.response_to_user or "NO_RESPONSE"
    print(f"[Turno 2] Agent: {resp_2}") 
    
    # Validação
    history_dump = "\n".join(ctx.history)
    print("\n--- DUMP DO HISTÓRICO ---")
    print(history_dump)
    
    if resp_2 == "NO_RESPONSE":
        print("\n❌ FALHA CRÍTICA: O agente não retornou resposta (LLM Error?). Verifique logs.")
        return

    with open("tests/result.txt", "w", encoding="utf-8") as f:
        # Dump completo para debug
        f.write(f"--- CTX Turno 2 ---\n")
        f.write(f"Reasoning: {getattr(ctx, 'reasoning', 'N/A')}\n")
        f.write(f"Location: {ctx.location}\n")
        f.write(f"Ready: {ctx.ready_to_submit}\n")
        f.write(f"Response: {resp_2}\n")
        f.write(f"History: {history_dump}\n")
        f.write("-" * 20 + "\n")

        if "apagado" in history_dump and "sala" in resp_2.lower():
            msg = "SUCESSO"
            print(f"\n✅ {msg}")
            f.write(msg)
        else:
            msg = "FALHA"
            print(f"\n❌ {msg}")
            f.write(f"{msg}: Ver detalhes acima.")

if __name__ == "__main__":
    test_memory()
