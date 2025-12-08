import sys
import os
import json
from typing import List, Dict

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from glpi_agent.glpi_client import GlpiClient
from glpi_agent.config import ENVIRONMENT
from agent.llm_connector import LLMConnector
from dotenv import load_dotenv

# Load Env
load_dotenv()

def run_chat_session():
    print("\n" + "="*60)
    print("🤖  ASSISTENTE VIRTUAL DE ABERTURA DE CHAMADOS (BETA)")
    print("============================================================")
    print("Descreva seu problema e eu irei te ajudar a abrir o chamado.")
    print("Digite 'sair' a qualquer momento para cancelar.")
    print("============================================================\n")

    # 1. Initialize dependencies
    client = GlpiClient(environment=ENVIRONMENT)
    client.init_session()
    
    if not client.session_token:
        print("❌ Erro: Não foi possivel conectar ao GLPI.")
        return

    connector = LLMConnector()

    # 2. System Prompt
    system_prompt = """
    Você é um Agente de Service Desk experiente e prestativo.
    Seu objetivo é coletar informações para abrir um ticket de suporte técnico.
    
    INFORMAÇÕES NECESSÁRIAS (Slots):
    1. Título (Resumo curto do problema)
    2. Descrição (Detalhes do que está acontecendo)
    3. Categoria Probável (Baseado no problema)
    4. Urgência (Baixa, Média, Alta - Baseado em quanto o usuário precisa disso)
    5. Impacto (Baixo, Médio, Alto - Baseado em quantas pessoas/processos são afetados)
    
    REGRAS DE INTERAÇÃO:
    - Fale em Português do Brasil de forma cordial e profissional.
    - Faça UMA pergunta por vez para preencher os slots vazios.
    - Se o usuário der uma descrição vaga, peça mais detalhes.
    - Inferir a Categoria, Urgência e Impacto se o contexto for claro, mas confirme com o usuário se tiver dúvida.
    - Quando você tiver TODAS as informações, pergunte: "Posso abrir o chamado com esses dados?" e mostre um resumo.
    
    FINALIZAÇÃO:
    - Se o usuário confirmar (disser "sim", "pode", "ok"), sua ÚLTIMA RESPOSTA deve ser APENAS um objeto JSON (sem markdown, sem texto extra) neste formato:
    {
        "finalizado": true,
        "dados": {
            "titulo": "...",
            "descricao": "...",
            "categoria": "...",
            "urgencia": "...",
            "impacto": "..."
        }
    }
    """

    messages: List[Dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Olá! Como posso ajudar você hoje?"}
    ]

    print(f"🤖 Agente: {messages[-1]['content']}")

    while True:
        try:
            # User Input
            user_input = input("\n👤 Você: ").strip()
            
            if user_input.lower() in ["sair", "exit", "cancelar"]:
                print("👋 Sessão encerrada.")
                break
                
            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})

            # LLM Thinking
            print("⏳ ...", end="\r")
            response = connector.chat_completion(messages)
            
            # Check for JSON termination
            if "finalizado" in response and "{" in response and "}" in response:
                try:
                    # Try to extract JSON from potential wrapper text
                    json_str = response
                    if "```json" in response:
                        json_str = response.split("```json")[1].split("```")[0]
                    elif "{" in response:
                        json_str = response[response.find("{"):response.rfind("}")+1]
                    
                    data = json.loads(json_str)
                    
                    if data.get("finalizado"):
                        ticket_data = data.get("dados", {})
                        create_ticket_in_glpi(client, ticket_data)
                        break
                except json.JSONDecodeError:
                    # Verify if it was just a conversational mention of finalizado
                    pass

            # Update History & Print
            messages.append({"role": "assistant", "content": response})
            print(f"🤖 Agente: {response}")

        except KeyboardInterrupt:
            print("\n👋 Sessão interrompida.")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            break

def create_ticket_in_glpi(client: GlpiClient, data: Dict):
    print("\n" + "="*50)
    print("🚀 ABRINDO CHAMADO NO GLPI...")
    print("="*50)
    print(f"Título: {data.get('titulo')}")
    print(f"Categoria (Sugerida): {data.get('categoria')}")
    print(f"Urgência: {data.get('urgencia')}")
    print(f"Impacto: {data.get('impacto')}")
    
    # Map Urgency/Impact to GLPI Integers (1-5)
    # This acts as a simple mapper. 
    # GLPI: 1=Very Low, 2=Low, 3=Medium, 4=High, 5=Very High
    level_map = {
        "baixa": 2, "baixo": 2,
        "média": 3, "media": 3, "médio": 3, "medio": 3,
        "alta": 4, "alto": 4, "urgente": 5, "crítico": 5
    }
    
    urgency_id = level_map.get(str(data.get("urgencia")).lower(), 3)
    impact_id = level_map.get(str(data.get("impacto")).lower(), 3)
    
    # Create
    final_desc = f"{data.get('descricao')}\n\n[Gerado via Chat Híbrido]\nDados Originais: {json.dumps(data, ensure_ascii=False)}"
    
    ticket_id = client.create_ticket(
        name=f"[CHAT] {data.get('titulo')}",
        content=final_desc,
        category_id=None # Leaving null for now to let the Backend Agent classify it properly? Or should we use the suggested one?
                         # Decision: Let the Backend Agent classify strictly (ID=None) OR if we mapped the category, pass it.
                         # For now, let's leave it to the Backend Agent to respect the 'simplicity' rule.
                         # But user asked for extraction. Let's include the extracted category in the description so the Agent can use it.
    )

    # Note: Currently create_ticket doesn't support urgency/impact in the wrapper.
    # We would need to update the ticket immediately after creation or update the wrapper.
    # For MVP, we stick to creating the ticket.
    
    if ticket_id:
        print(f"\n✅ SUCESSO! Chamado criado: {ticket_id}")
        
        # Update Urgency/Impact manually via raw update if possible, or just skip for MVP.
        # Let's try to update urgency if possible.
        try:
             client.update_item("Ticket", ticket_id, {"urgency": urgency_id, "impact": impact_id})
             print("✅ Urgência e Impacto definidos.")
        except:
             print("⚠️ Não foi possível definir urgência/impacto (MVP Limit).")
            
        print("👉 O Agente Classificador (Backend) irá processar a categoria final em breve.")
    else:
        print("\n❌ Falha ao criar chamado.")

if __name__ == "__main__":
    if "--test" in sys.argv:
        print("Test mode ignored. Run interactively.")
    else:
        run_chat_session()
