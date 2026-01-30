"""
E2E Verification for Ticket 11909
"""
import sys
import logging
from pathlib import Path
from sqlalchemy import text

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from src.core import Database
from sync import run_sync

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("E2E_TEST")

# Override Ollama URL for Local Host execution (Windows)
import os
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
# Override DB Host if running from Windows (assuming port is mapped)
os.environ["POSTGRES_HOST"] = "localhost"

def check_ticket(session, glpi_id):
    """Query and print ticket details."""
    # Assuming DTIC context based on URL (cau.ppiratini usually DTIC?)
    # or SIS? The URL is generic glpi/front/ticket.
    # We will check both schemas or assume DTIC.
    # The user said "Projetos_Locais\BD_Cau_V2" which implies DTIC usually.
    # Let's check DTIC tickets first.
    
    query = text(f"SELECT glpi_id, titulo, status_id, atualizado_em FROM dtic.tickets WHERE glpi_id = {glpi_id}")
    try:
        result = session.execute(query).fetchone()
        if result:
            print(f"   ✅ FOUND in DTIC: {result}")
            return True
        else:
            print(f"   ❌ NOT FOUND in DTIC.")
            return False
    except Exception as e:
        print(f"   ⚠️ Error querying DTIC: {e}")
        return False

def main():
    print("=" * 60)
    print("🕵️ E2E TEST: Ticket #11909")
    print("=" * 60)
    
    session = Database.get_session(context='dtic')
    
    print("\n1. Initial Check:")
    exists = check_ticket(session, 11909)
    
    print("\n2. Running Incremental Sync (Force)...")
    try:
        # We run INCREMENTAL sync to simulate the daemon
        # We assume the config is set correctly in .env
        run_sync(context='dtic', sync_type='tickets', incremental=True)
    except Exception as e:
        print(f"   ❌ Sync Failed: {e}")
    
    print("\n3. Post-Sync Check:")
    check_ticket(session, 11909)

    print("\n4. Checking RAG Embedding...")
    try:
        query_rag = text(f"""
            SELECT k.id, k.ticket_id, substring(k.content, 1, 50) as snippet 
            FROM dtic.knowledge_entries k
            JOIN dtic.tickets t ON k.ticket_id = t.id
            WHERE t.glpi_id = 11909
        """)
        res_rag = session.execute(query_rag).fetchone()
        if res_rag:
            print(f"   ✅ FOUND Embedding: ID={res_rag.id}, Content='{res_rag.snippet}...'")
        else:
            print(f"   ❌ NOT FOUND Embedding for Ticket 11909.")
    except Exception as e:
         print(f"   ⚠️ Error checking RAG: {e}")
    
    session.close()

if __name__ == "__main__":
    main()
