import os
import sys

# Ajuste de path para importar módulos do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "glpi-ai-system"))

import requests
from agents.opener.agent import SurgicalOpenerAgent

# Configurações de Ambiente
os.environ["LLM_BASE_URL"] = "http://localhost:11434/v1"

def get_valid_model():
    try:
        resp = requests.get("http://localhost:11434/api/tags")
        if resp.status_code == 200:
            models = [m['name'] for m in resp.json()['models']]
            for m in models:
                if "qwen" in m.lower(): return m
            return models[0] if models else "llama3.1:8b"
    except:
        return "qwen2.5-coder:7b"

os.environ["LLM_MODEL_NAME"] = get_valid_model()
print(f">> Usando modelo: {os.environ['LLM_MODEL_NAME']}")

class TestCase:
    def __init__(self, name, turns, assertions):
        self.name = name
        self.turns = turns  # Lista de inputs do usuário
        self.assertions = assertions # Função lambda que recebe o ctx final

def run_tests():
    agent = SurgicalOpenerAgent()
    
    test_cases = [
        # CENARIO 1: Caminho Feliz (Tudo de uma vez)
        TestCase(
            name="Happy Path - Full Info",
            turns=[
                "Ola, sou do RH, sala 202. Minha impressora HP nao esta imprimindo nada."
            ],
            assertions=lambda ctx: (
                ctx.location is not None and "202" in ctx.location and
                ctx.summary is not None and
                ctx.ready_to_submit == True
            )
        ),
        
        # CENARIO 2: Informação Parcial (Fluxo Vago)
        TestCase(
            name="Partial Info - Vague Flow",
            turns=[
                "meu pc não liga",         # Turno 1 (Agent deve perguntar diag + local)
                "está apagado o led",      # Turno 2 (Agent deve insistir no local)
                "estou na sala de reuniões" # Turno 3 (Agora deve estar pronto)
            ],
            assertions=lambda ctx: (
                ctx.location is not None and "reuni" in ctx.location.lower() and
                ctx.ready_to_submit == True
            )
        ),
        
        # CENARIO 3: Segurança (Solicitação de Senha)
        TestCase(
            name="Security - Password Reset",
            turns=[
                "preciso resetar a senha do servidor do diretor, sala 101"
            ],
            assertions=lambda ctx: (
                # O agente deve negar ou orientar, provalvemente marcando urgencia mas explicando no response
                # O importante é que ele capture a intenção mas a resposta seja adequada.
                # Neste caso, vamos verificar se ele capturou o local e a intent
                ctx.location is not None and
                "101" in ctx.location and
                (ctx.urgency == "Baixa" or ctx.urgency == "Média") # Geralmente dúvida/acesso
            )
        )
    ]

    results = []
    
    print(f"\n>> INICIANDO BATERIA DE {len(test_cases)} TESTES <<\n")

    for i, test in enumerate(test_cases):
        print(f"🔄 Executando Teste {i+1}: {test.name}...")
        ctx = None
        
        # Executa os turnos
        for turn_idx, user_input in enumerate(test.turns):
            print(f"   Turno {turn_idx+1} [User]: {user_input}")
            ctx = agent.process_ticket(user_input, current_context=ctx)
            
            # Debug Rasoning
            reasoning = getattr(ctx, 'reasoning', 'N/A')
            print(f"   🤖 [Agent Reasoning]: {reasoning}")
            print(f"   🗣️ [Agent Response]: {ctx.response_to_user}")
            
        # Verifica assertivas
        try:
            passed = test.assertions(ctx)
            status = "✅ PASSOU" if passed else "❌ FALHOU"
        except Exception as e:
            status = f"❌ ERRO ({e})"
            passed = False
            
        results.append((test.name, status, ctx))
        print(f"   Resultado: {status}\n")

    # Resumo Final e Escrita em Arquivo
    with open("tests/comprehensive_result.txt", "w", encoding="utf-8") as f:
        print("="*40)
        print("RESUMO DOS TESTES")
        print("="*40)
        f.write("RESUMO DOS TESTES\n")
        
        all_passed = True
        for name, status, final_ctx in results:
            # Print Console
            print(f"{status} - {name}")
            if "FALHOU" in status:
                all_passed = False
                print(f"      -> Final Location: {final_ctx.location}")
                print(f"      -> Final Urgency: {final_ctx.urgency}")
                print(f"      -> Final Reasoning: {getattr(final_ctx, 'reasoning', 'N/A')}")
            
            # Write File
            f.write(f"{status} - {name}\n")
            f.write(f"      -> Final Context: {final_ctx.model_dump_json(indent=2)}\n")
            f.write("-" * 20 + "\n")

        if all_passed:
            msg = "\n🏆 TODOS OS TESTES PASSARAM! O AGENTE ESTÁ ROBUSTO."
            print(msg)
            f.write(msg)
        else:
            msg = "\n⚠️ ALGUNS TESTES FALHARAM. REVISE OS PROMPTS."
            print(msg)
            f.write(msg)

if __name__ == "__main__":
    run_tests()
