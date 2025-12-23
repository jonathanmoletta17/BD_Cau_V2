
import sys
import os
import logging
from sqlalchemy import text

# Add paths to sys.path to ensure modules are found
current_dir = os.path.dirname(os.path.abspath(__file__)) # scripts/
parent_dir = os.path.dirname(current_dir) # glpi-sync-dtic/
common_dir = os.path.join(os.path.dirname(parent_dir), 'common') # glpi-db-services/common

sys.path.append(parent_dir)
sys.path.append(common_dir)

from src.core.database import Database
from src.models.dashboard.service import get_ticket_details

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fetch_ticket():
    session = None
    try:
        session = Database.get_session(schema="dtic")
        
        # 1. Get a valid ticket ID (latest one)
        logger.info("Fetching latest ticket to get a valid ID...")
        latest_ticket = session.execute(
            text("SELECT glpi_id FROM dtic.tickets WHERE is_deleted = false ORDER BY criado_em DESC LIMIT 1")
        ).fetchone()
        
        if not latest_ticket:
            logger.error("No tickets found in the database!")
            return

        ticket_id = latest_ticket[0]
        logger.info(f"Found Ticket ID: {ticket_id}")
        
        # 2. Fetch Details
        logger.info(f"Fetching details for Ticket #{ticket_id}...")
        details = get_ticket_details(session, ticket_id)
        
        if details:
            logger.info("Successfully fetched ticket details:")
            import json
            print(json.dumps(details, indent=2, default=str))
        else:
            logger.error("Failed to fetch ticket details (returned None).")
            
    except Exception as e:
        logger.error(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if session:
            session.close()

if __name__ == "__main__":
    test_fetch_ticket()
