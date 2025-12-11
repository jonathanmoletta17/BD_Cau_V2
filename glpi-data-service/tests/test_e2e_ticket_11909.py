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
    
    session.close()

if __name__ == "__main__":
    main()
