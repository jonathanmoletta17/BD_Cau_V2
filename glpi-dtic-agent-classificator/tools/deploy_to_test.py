import os
import sys
import logging
from datetime import datetime
import time

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.simple_agent import SimpleAgent, CONFIDENCE_THRESHOLD

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"deploy_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", encoding='utf-8')
    ]
)
logger = logging.getLogger("DeployAgent")

def main():
    print("="*60)
    print("🚀 INICIANDO DEPLOY DE RECLASSIFICAÇÃO (AMBIENTE DE TESTES)")
    print("="*60)
    print("⚠️  ATENÇÃO: Este script vai ALTERAR categorias no GLPI de TESTE.")
    print("    Certifique-se de que GLPI_TEST_URL aponta para o ambiente correto.")
    print("="*60)
    
    # 1. Initialize Agent
    agent = SimpleAgent()
    
    # Force Sandbox OFF (We want to write)
    # Note: simple_agent logic checks SANDBOX from config, but we can override if needed
    # However, let's respect the agent's internal logic, assuming environment="test" allows updates.
    
    if agent.client.env == "prod":
        logger.error("❌ PERIGO: Cliente conectado em PRODUÇÃO. Abortando imediatamente.")
        return

    logger.info(f"✅ Conectado em ambiente: {agent.client.env}")
    
    # 2. Fetch ALL Tickets (Pagination)
    logger.info("📡 Buscando TODOS os tickets (pode levar um tempo)...")
    
    # Using list_items_range logic or just search_items with big range
    # search_items usually returns all if no range specified, or paginated.
    # checking glpi_client implementation: _get uses Range=0-499 by default?
    # No, _get uses Range=0-499 HARDCODED.
    # We need to loop.
    
    all_tickets = []
    chunk_size = 500
    offset = 0
    
    while True:
        logger.info(f"   Fetching range {offset}-{offset+chunk_size}...")
        try:
            # We use list_items_range exposed or construct manual range
            # simple_agent doesn't expose pagination loop. We'll use client directly.
            chunk = agent.client.list_items_range("Ticket", offset, offset + chunk_size)
            if not chunk:
                break
            
            all_tickets.extend(chunk)
            offset += chunk_size
            
            # Safety break
            if offset > 10000: 
                logger.warning("⚠️ Limite de segurança de 10k tickets atingido.")
                break
                
        except Exception as e:
            logger.error(f"Erro na paginação: {e}")
            break
            
    logger.info(f"📦 Total de tickets encontrados: {len(all_tickets)}")
    
    # 3. Process Logic
    total = len(all_tickets)
    processed = 0
    updated = 0
    
    for ticket in all_tickets:
        processed += 1
        pct = (processed / total) * 100
        print(f"\rProcessando {processed}/{total} ({pct:.1f}%)", end="")
        
        # Check if ticket is closed/solved - maybe we skip? 
        # User said "ALL tickets", so we process all.
        
        # Use Agent's process_ticket which calls update
        # We need to temporarily Hijack stats or just rely on agent logging
        
        # NOTE: agent.process_ticket handles:
        # - Understanding Text
        # - Matching Category
        # - Checking Confidence
        # - UPDATING GLPI if confident
        
        try:
            agent.process_ticket(ticket)
        except Exception as e:
            logger.error(f"Erro ticket {ticket.get('id')}: {e}")

    print("\n\n" + "="*60)
    print("🏁 DEPLOY FINALIZADO")
    print(f"   Tickets Processados: {agent.stats['processed']}")
    print(f"   Tickets Atualizados: {agent.stats['updated']}")
    print("="*60)

if __name__ == "__main__":
    main()
