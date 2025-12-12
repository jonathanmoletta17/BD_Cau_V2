import sys
import os
import time

# Adicionar o diretório atual ao path para importação
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import SurgicalOpenerAgent
from glpi_service import GLPIService

def log(msg):
    print(msg)
    with open("simulation_log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def run_scenario(name, inputs):
    log(f"\n{'='*20} CENÁRIO: {name} {'='*20}")
    agent = SurgicalOpenerAgent()
    glpi = GLPIService()
    ctx = None
    
    log(f"🔹 Iniciando Sessão GLPI...")
    if glpi.init_session():
        log(f"✅ GLPI Conectado.")
    else:
        log(f"❌ Falha ao conectar no GLPI (Verifique .env). Continuando apenas simulação de chat...")
    
    for user_input in inputs:
        log(f"\n👤 User: {user_input}")
        
        # Processa
        ctx = agent.process_ticket(user_input, current_context=ctx)
        
        # Mostra Resposta
        log(f"🤖 Agent: {ctx.response_to_user}")
        
        # Depuração do Estado Interno
        log(f"   [Estado] Ready: {ctx.ready_to_submit} | Impact: {ctx.impact} | Missing: {ctx.missing_info}")
        
        if ctx.ready_to_submit:
            log(f"\n🚀 TICKET REVIEW:")
            log(f"   - Resumo: {ctx.summary}")
            log(f"   - Descrição: {ctx.description}")
            log(f"   - Local: {ctx.location}")
            log(f"   - Urgência: {ctx.urgency}")
            log(f"   - Impacto: {ctx.impact}")
            
            # Tentar Criar no GLPI
            if glpi.session_token:
                log("\n📨 Enviando para GLPI...")
                result = glpi.create_ticket(
                    title=ctx.summary,
                    description=ctx.description,
                    location=ctx.location,
                    urgency=ctx.urgency,
                    impact=ctx.impact or "Individual"
                )
                log(f"✅ Resultado GLPI: {result}")
            else:
                log("⚠️ Pulo envio GLPI (Sem Token)")
            break
            
    glpi.kill_session()
    log(f"{'='*50}")

if __name__ == "__main__":
    # Cenário 1: Desbloqueio de Senha (Testar regra de NÃO pedir ID)
    run_scenario("Desbloqueio de Senha (Teste Regra ID)", [
        "Olá, bloqueei minha senha de rede, pode me ajudar?",
        "Sou do setor de Protocolo, sala 10"  # Usuário fornece local, agente deve aceitar sem pedir ID
    ])

    # Cenário 2: Impacto Organizacional
    run_scenario("Queda Geral de Internet (Teste Impacto)", [
        "A internet parou de funcionar no prédio inteiro!",
        "Estou na recepção do térreo"
    ])
