"""
E2E Real-Time Sync Verification Script
Performs CRUD operations on GLPI API and verifies local DB replication.

Flow:
1. CREATE Ticket in GLPI.
2. WAIT for Local DB Sync.
3. UPDATE Ticket in GLPI.
4. WAIT for Local DB Sync.
5. DELETE Ticket in GLPI.
6. WAIT for Local DB Sync (is_deleted=True).
"""
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Config, Database
from src.core.glpi_client import GLPIClient
from src.modules.dtic.tickets.models import Ticket

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - TEST - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
CONTEXT = 'dtic'
POLL_INTERVAL = 5
TIMEOUT = 120 # 2 minutes timeout per step

def wait_for_ticket_state(session, glpi_id, check_func, description):
    """Polls local DB until check_func returns True."""
    logger.info(f"⏳ Waiting for: {description}...")
    start = time.time()
    while time.time() - start < TIMEOUT:
        # Expunge to ensure fresh data from DB
        session.expire_all()
        ticket = session.query(Ticket).filter_by(glpi_id=glpi_id).first()
        
        if ticket and check_func(ticket):
            logger.info(f"✅ Verified: {description}")
            return ticket
        
        time.sleep(POLL_INTERVAL)
        print(".", end="", flush=True)
    
    logger.error(f"❌ Timeout waiting for: {description}")
    return None

def main():
    logger.info("🚀 Starting Real-Time CRUD E2E Test...")
    
    # 1. Setup Clients
    url = Config.get_glpi_url(CONTEXT)
    app_token = Config.get_glpi_app_token(CONTEXT)
    user_token = Config.get_glpi_user_token(CONTEXT)
    
    session = Database.get_session(context=CONTEXT)
    
    try:
        with GLPIClient(url, app_token, user_token) as client:
            # Prepare Headers (Need to manually grab session token)
            headers = {
                'App-Token': client.app_token,
                'Session-Token': client.session_token,
                'Content-Type': 'application/json'
            }

            # =================================================================
            # STEP 1: CREATE
            # =================================================================
            logger.info("\n[1/3] Creating Test Ticket in GLPI...")
            ticket_payload = {
                "name": f"E2E Test Ticket - {datetime.now().isoformat()}",
                "content": "Automated test for sync verification.",
                "status": 1, # New
                "priority": 1
            }
            # Use raw post because client helper might be read-only optimized
            res = client.session.post(f"{client.base_url}/Ticket", json={"input": ticket_payload}, headers=headers)
            res.raise_for_status()
            glpi_id = res.json()['id']
            logger.info(f"   -> Ticket Created in GLPI. ID: {glpi_id}")
            
            # Wait for Sync
            def check_created(t): return t is not None
            if not wait_for_ticket_state(session, glpi_id, check_created, "Ticket Creation Persisted"):
                sys.exit(1)

            # =================================================================
            # STEP 2: UPDATE
            # =================================================================
            logger.info("\n[2/3] Updating Test Ticket in GLPI...")
            new_title = f"E2E Test Ticket - UPDATED - {datetime.now().isoformat()}"
            update_payload = {
                "id": glpi_id,
                "name": new_title,
                "priority": 2
            }
            res = client.session.put(f"{client.base_url}/Ticket/{glpi_id}", json={"input": update_payload}, headers=headers)
            res.raise_for_status()
            logger.info(f"   -> Ticket Updated in GLPI.")
            
            # Wait for Sync
            def check_updated(t): return t.titulo == new_title[:500] and t.prioridade_id == 2
            if not wait_for_ticket_state(session, glpi_id, check_updated, "Ticket Update Persisted"):
                sys.exit(1)

            # =================================================================
            # STEP 3: DELETE (Soft)
            # =================================================================
            logger.info("\n[3/3] Deleting Test Ticket in GLPI (Trash)...")
            # In GLPI API, DELETE usually moves to trash (is_deleted=1)
            # Or we can explicitly set is_deleted=1 via PUT if we want to be safe, but DELETE verb is standard
            # Let's try DELETE verb first.
            res = client.session.delete(f"{client.base_url}/Ticket/{glpi_id}", headers=headers)
            res.raise_for_status()
            logger.info(f"   -> Ticket Deleted in GLPI.")
            
            # Wait for Sync
            def check_deleted(t): return t.is_deleted == True
            if not wait_for_ticket_state(session, glpi_id, check_deleted, "Ticket Deletion (is_deleted=1) Persisted"):
                sys.exit(1)

            logger.info("\n✨ SUCCESS! Real-Time Sync Verified for all CRUD operations.")
            
            # Cleanup: Purge from GLPI? (Optional, maybe manually later)

    except Exception as e:
        logger.error(f"❌ Test Failed: {e}")
        # Print response content if available in exception
        if hasattr(e, 'response') and e.response is not None:
             logger.error(f"   Response Body: {e.response.text}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()
