import sys
import os
import argparse
import logging
import time
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from glpi_agent.glpi_client import GlpiClient
from glpi_agent.config import ENVIRONMENT

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("TicketSimulator")

def main():
    load_dotenv()
    
    # Safety Check
    if ENVIRONMENT == "prod":
        logger.error("🚫 SAFETY: Cannot run this script in PRODUCTION!")
        sys.exit(1)

    # CLI Arguments
    parser = argparse.ArgumentParser(description="Create a test ticket and wait for Agent classification.")
    parser.add_argument("description", nargs="?", help="Description of the problem")
    args = parser.parse_args()

    # Get Input
    description = args.description
    if not description:
        print("\n📝 Digite a descrição do problema para criar um Ticket:")
        description = input("> ").strip()

    if not description:
        logger.warning("Empty description. Exiting.")
        sys.exit(0)

    # Initialize Client
    client = GlpiClient(environment=ENVIRONMENT)
    client.init_session()
    
    if not client.session_token:
        logger.error("Failed to connect to GLPI.")
        sys.exit(1)

    # Create Ticket
    user_name = "User_Test_Script"
    logger.info(f"Creating ticket: '{description}'...")
    
    ticket_id = client.create_ticket(
        name=f"[TEST] {description[:30]}...",
        content=description,
        category_id=None # Let the Agent categorize it!
    )
    
    if not ticket_id:
        logger.error("Failed to create ticket.")
        sys.exit(1)
        
    print(f"\n✅ Ticket Criado! ID: {ticket_id}")
    print("⏳ Aguardando classificação pelo Agente Híbrido (Container)...")
    
    # Polling Loop
    start_time = time.time()
    max_wait = 300 # 5 minutes max
    categorized = False
    
    while (time.time() - start_time) < max_wait:
        try:
            # Refresh Ticket Data
            ticket = client.get_item("Ticket", ticket_id)
            if not ticket:
                continue
                
            cat_id = ticket.get("itilcategories_id")
            
            # Check if categorized (not 0/None)
            if cat_id and cat_id not in [0, "0", None]:
                cat_name = client.get_category_name(cat_id)
                
                # Fetch Reasoning (Followups)
                reasoning = "Sem justificativa."
                followups = client.list_ticket_followups(ticket_id)
                if followups:
                    # Get the most recent followup content
                    last_msg = followups[-1].get("content", "")
                    # Extract Reason if formatted by Agent
                    if "Motivo (AI):" in last_msg:
                        reasoning = last_msg.split("Motivo (AI):")[-1].strip()
                    else:
                        reasoning = last_msg
                
                print("\n" + "="*50)
                print(f"🤖 RESULTADO DA CLASSIFICAÇÃO")
                print("="*50)
                print(f"📂 Categoria Final:  \033[92m{cat_name}\033[0m")
                print(f"🧠 Justificativa AI: {reasoning}")
                print("="*50 + "\n")
                
                categorized = True
                break
                
            time.sleep(5)
            print(".", end="", flush=True)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoramento interrompido.")
            break
        except Exception as e:
            logger.error(f"Error polling: {e}")
            break
            
    if not categorized:
        print("\n⚠️ Tempo limite excedido. O ticket ainda não foi classificado.")
        print("Verifique se o container 'glpi_classifier_service' está rodando.")

if __name__ == "__main__":
    main()
