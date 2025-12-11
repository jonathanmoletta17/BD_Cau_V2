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

if __name__ == "__main__":
    try:
        test_real_glpi_submission()
    except Exception as e:
        print(f"Erro fatal nos testes: {e}")
