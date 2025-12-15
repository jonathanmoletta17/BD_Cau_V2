"""
E2E Full Lifecycle Test
Validates: Create -> Sync -> RAG -> Delete -> Sync Deletion
"""
import sys
import logging
import time
import os
from pathlib import Path
from sqlalchemy import text

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent))
# Add scripts folder specifically for top-level script imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from src.core import Database, Config
from src.core.glpi_client import GLPIClient
from src.services.sync import SyncService
# The file is scripts/sync.py, so `import sync` works if scripts/ is on path
from sync import run_sync

# Override for local execution
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
os.environ["POSTGRES_HOST"] = "localhost"

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - E2E - %(levelname)s - %(message)s')
logger = logging.getLogger("E2E_LIFECYCLE")

def create_test_ticket(client, title):
    """Create a ticket via API."""
    logger.info(f"Creating Ticket: {title}")
    # Minimal payload
    payload = {
        "input": {
            "name": title,
            "content": "Automated E2E Test Content with RAG verification.",
            "status": 1, # New
            "priority": 3,
            "urgency": 3,
            "impact": 3,
            "itilcategories_id": 0 # Unknown/Root
        }
    }
    # Using the low-level _post from client if available or implement raw
    # GLPIClient usually has some helpers, let's use the session directly if needed or client methods
    # Checking client source... it has create_ticket? No, mostly fetch.
    # We will use raw request using client.session
    url = f"{client.base_url}/Ticket"
    res = client.session.post(url, json=payload)
    res.raise_for_status()
    return res.json()['id']

def delete_ticket(client, ticket_id, purge=False):
    """Delete (Trash) or Purge a ticket."""
    url = f"{client.base_url}/Ticket/{ticket_id}"
    logger.info(f"Deleting Ticket {ticket_id} (Purge={purge})...")
    
    if purge:
        # Purge requires force_purge parameter usually or specific endpoint
        # For GLPI, DELETE /Ticket/ID moves to trash.
        # DELETE /Ticket/ID?force_purge=true deletes permanently.
        url += "?force_purge=true"
    
    res = client.session.delete(url)
    if res.status_code not in [200, 204]:
        logger.warning(f"Failed to delete {ticket_id}: {res.status_code} {res.text}")

def check_db_features(session, glpi_id, expect_deleted=False):
    """Check DB for Ticket and Embedding."""
    # 1. Check Ticket
    t_query = text(f"SELECT id, glpi_id, titulo, is_deleted FROM dtic.tickets WHERE glpi_id = {glpi_id}")
    ticket = session.execute(t_query).fetchone()
    
    if not ticket:
        if expect_deleted: 
            logger.info(f"   ✅ Ticket {glpi_id} correctly REMOVED from DB (or not found).")
            return
        else:
            logger.error(f"   ❌ Ticket {glpi_id} NOT FOUND in DB (Expected exists).")
            return

    if expect_deleted:
        if ticket.is_deleted:
             logger.info(f"   ✅ Ticket {glpi_id} marked as DELETED in DB.")
        else:
             logger.error(f"   ❌ Ticket {glpi_id} found in DB but NOT marked deleted.")
        return

    logger.info(f"   ✅ Ticket {glpi_id} found. ID: {ticket.id}")

    # 2. Check Embedding
    k_query = text(f"SELECT id FROM dtic.knowledge_entries WHERE ticket_id = {ticket.id}")
    embedding = session.execute(k_query).fetchone()
    
    if embedding:
        logger.info(f"   ✅ RAG Embedding found. Entry ID: {embedding.id}")
    else:
        logger.error(f"   ❌ RAG Embedding MISSING for Ticket {glpi_id}.")

def main():
    logger.info("🎬 Starting E2E Lifecycle Test")
    
    # Context: DTIC (Prod mapped)
    context = 'dtic'
    session = Database.get_session(context=context)
    
    # Config
    url = Config.get_glpi_url(context)
    app_token = Config.get_glpi_app_token(context)
    user_token = Config.get_glpi_user_token(context)
    
    # ------------------------------------------------------------
    # Phase 1: Create & Sync
    # ------------------------------------------------------------
    new_id = None
    with GLPIClient(url, app_token, user_token) as client:
        # 1. Create
        title = f"E2E_TEST_RAG_AUTO_{int(time.time())}"
        try:
             new_id = create_test_ticket(client, title)
             logger.info(f"   👉 Created Ticket ID: {new_id}")
        except Exception as e:
             logger.error(f"   ❌ Failed to create ticket: {e}")
             return

    # 2. Sync (Incremental)
    logger.info("🔄 Running Sync (Ticket Only)...")
    try:
        run_sync(context=context, sync_type='tickets', incremental=True)
    except Exception as e:
        logger.error(f"   ❌ Sync Failed: {e}")
    
    # 3. Verify
    logger.info("🔍 Verifying Creation & RAG...")
    check_db_features(session, new_id, expect_deleted=False)
    
    # ------------------------------------------------------------
    # Phase 2: Delete & Cleanup (11942, 11943)
    # ------------------------------------------------------------
    targets = [new_id, 11942, 11943]
    logger.info(f"🗑️ Deleting Tickets: {targets}")
    
    with GLPIClient(url, app_token, user_token) as client:
        for tid in targets:
            try:
                # We move to trash first (default DELETE)
                delete_ticket(client, tid)
            except Exception as e:
                logger.warning(f"   ⚠️ Could not delete {tid}: {e}")

    # 5. Sync Again (Capture Changes/Deletions)
    logger.info("🔄 Running Sync (Post-Deletion)...")
    try:
        run_sync(context=context, sync_type='tickets', incremental=True)
    except Exception as e:
        logger.error(f"   ❌ Sync Failed: {e}")

    # 6. Verify Deletions
    logger.info("🔍 Verifying Deletions...")
    for tid in targets:
        check_db_features(session, tid, expect_deleted=True)
        
    session.close()
    logger.info("🏁 E2E Test Complete.")

if __name__ == "__main__":
    main()
