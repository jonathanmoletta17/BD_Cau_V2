import sys
import os
# Ajusta path para importar modules se executado de dentro da pasta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.opener.agent import SurgicalOpenerAgent
from agents.opener.glpi_service import GLPIService

def test_real_glpi_submission():
    print("\n[TEST] Cenario Real: Envio para GLPI Teste.")
    # Instancia agente e serviço
    agent = SurgicalOpenerAgent()
    glpi = GLPIService()
    
    input_text = "Estou realizando um teste automatizado do Agente Opener. A impressora do 2o andar parou. (Teste End-to-End)"
    print(f"Input: {input_text}")
    
    # Processa
    ctx = agent.process_ticket(input_text)
    
    if ctx.ready_to_submit:
        print("✅ Agente marcou como pronto para envio.")
        print(f"Resumo: {ctx.summary}")
        
        # Tenta criar o ticket
        result = glpi.create_ticket(
            title=ctx.summary,
            description=ctx.description, 
            location=ctx.location,
            urgency=ctx.urgency
        )
        
        if "id" in result:
            print(f"✅ Ticket criado com sucesso no GLPI! ID: {result['id']}")
        else:
            print(f"❌ Falha ao criar ticket: {result}")
    else:
        print(f"❌ Agente não finalizou o ticket para envio. Contexto: {ctx.model_dump_json()}")

def test_interactive_flow():
    print("\n[TEST] Cenario Interativo: Internet (Sem Local Inicial).")
    # Instancia agente (Mockando URL para test local se necessario, mas assumindo env var)
    agent = SurgicalOpenerAgent()
    
    # Passo 1: Usuário reclama mas não diz onde (FSM deve bloquear)
    msg1 = "Minha internet caiu"
    print(f"User (1): {msg1}")
    ctx = agent.process_ticket(msg1)
    
    print(f"Agent (1): {ctx.response_to_user}")
    
    if ctx.ready_to_submit:
        print("❌ FALHA: Agente aceitou ticket sem localização!")
        return

    # Passo 2: Usuário responde o local
    msg2 = "Estou no setor de RH"
    print(f"User (2): {msg2}")
    
    # Passamos o contexto atualizado de volta
    ctx = agent.process_ticket(msg2, current_context=ctx)
    
    print(f"Agent (2): {ctx.response_to_user}")
    
    if ctx.ready_to_submit:
        print(f"✅ Agente marcou como pronto! Resumo: {ctx.summary}")
    else:
        print("❌ FALHA: Agente não finalizou mesmo após receber local.")

if __name__ == "__main__":
    try:
        test_real_glpi_submission()
        test_interactive_flow()
    except Exception as e:
        print(f"Erro fatal nos testes: {e}")
