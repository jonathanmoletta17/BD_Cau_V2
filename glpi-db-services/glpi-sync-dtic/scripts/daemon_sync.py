"""
GLPI Sync Service - DTIC Context
Dedicated daemon for synchronizing DTIC data.
"""
import sys
import time
import logging
import signal
from sqlalchemy import text # Import text logic
from pathlib import Path
from datetime import datetime

# Add common library to path (assuming Docker mount or copy)
# In Docker, we'll put common at /app/common or similar via PYTHONPATH
# For local dev, we add relative path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'common'))
# Add local src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import config
from src.core.database import Database
from src.core.base import Base  # Import Base for metadata
from src.core.glpi_client import GLPIClient
from src.core.models import SyncState
from src.services.sync import SyncService

# Import Models
import src.models.metadata as metadata
import src.models.tickets as tickets

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - DTIC-SYNC - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

LOOP_INTERVAL = 30

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    def exit_gracefully(self, signum, frame):
        self.kill_now = True

def get_models():
    """Return model map for DTIC."""
    return {
        'User': metadata.User,
        'Group': metadata.Group,
        'Entity': metadata.Entity,
        'Location': metadata.Location,
        'Category': metadata.ITILCategory,
        'Profile': metadata.Profile,
        'GroupUser': metadata.GroupUser,
        'ProfileUser': metadata.ProfileUser,
        'Ticket': tickets.Ticket,
        'TicketUser': tickets.TicketUser,
        'TicketGroup': tickets.TicketGroup,
        'TicketChange': tickets.TicketChange,
        'TicketKnowledge': tickets.TicketKnowledge # AI / RAG
    }

def run_once(models):
    """Single sync iteration."""
    url = config.GLPI_DTIC_URL
    app_token = config.GLPI_DTIC_APP_TOKEN
    user_token = config.GLPI_DTIC_USER_TOKEN
    
    if not url:
        logger.error("❌ GLPI URL not configured.")
        return

    session = Database.get_session(schema='dtic')
    
    try:
        with GLPIClient(url, app_token, user_token) as client:
            client.init_session() # [FIX] Ensure session is initialized
            
            # 1. Sync Metadata
            SyncService.sync_entities(client, session, models['Entity'])
            SyncService.sync_locations(client, session, models['Location'])
            SyncService.sync_groups(client, session, models['Group'])
            SyncService.sync_users(client, session, models['User'])
            SyncService.sync_categories(client, session, models['Category'])
            SyncService.sync_profiles(client, session, models['Profile'])
            
            # Load IDs for validation
            valid_ids = {
                'users': set(r.id for r in session.query(models['User'].id).all()),
                'groups': set(r.id for r in session.query(models['Group'].id).all()),
                'entities': set(r.id for r in session.query(models['Entity'].id).all()),
                'locations': set(r.id for r in session.query(models['Location'].id).all()),
                'categories': set(r.id for r in session.query(models['Category'].id).all()),
                'profiles': set(r.id for r in session.query(models['Profile'].id).all()),
            }
            
            # Sync Relationships
            SyncService.sync_groups_users(client, session, models['GroupUser'], valid_ids)
            SyncService.sync_profiles_users(client, session, models['ProfileUser'], valid_ids)

            # 2. Sync Tickets (Incremental)
            st = session.query(SyncState).filter_by(context='dtic', entity_type='Ticket').first()
            since_date = st.last_sync if st else None
            
            def update_state(max_date):
                if not max_date: return
                # Re-query to avoid stale object issues
                local_st = session.query(SyncState).filter_by(context='dtic', entity_type='Ticket').first()
                if not local_st:
                    local_st = SyncState(context='dtic', entity_type='Ticket')
                    session.add(local_st)
                local_st.last_sync = max_date
                session.commit()

            SyncService.sync_tickets(
                client, session, models, valid_ids, context='dtic', limit=None, 
                since_date=since_date,
                sync_state_manager=update_state
            )
            
            # Sync Ticket Actors
            SyncService.sync_ticket_actors(client, session, models, valid_ids, limit=None)
            
            # 3. Sync Changes
            st_ch = session.query(SyncState).filter_by(context='dtic', entity_type='TicketChange').first()
            since_changes = st_ch.last_sync if st_ch else None
            
            max_ch = SyncService.sync_ticket_changes(
                client, session, models, valid_ids, limit=None, since_date=since_changes
            )
            
            if max_ch:
                local_ch = session.query(SyncState).filter_by(context='dtic', entity_type='TicketChange').first()
                if not local_ch:
                    local_ch = SyncState(context='dtic', entity_type='TicketChange')
                    session.add(local_ch)
                local_ch.last_sync = max_ch
                session.commit()
                
            client.close_session()
            
    except Exception as e:
        logger.error(f"Error in sync loop: {e}")
    finally:
        session.close()

def main():
    logger.info("🚀 Starting DTIC Sync Daemon...")
    
    # Init DB Schema
    logger.info("⚙️  Initializing Database Schema (DTIC)...")
    try:
        engine = Database.get_engine()
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS dtic"))
            conn.commit()
            
        Base.metadata.create_all(engine)
        logger.info("✅ Database Schema Ready.")
    except Exception as e:
        logger.error(f"❌ Failed to init DB: {e}")
        sys.exit(1)

    killer = GracefulKiller()
    
    models = get_models()
    
    # Ensure DB Ready (Simple check)
    # Generic wait_for_db?
    
    while not killer.kill_now:
        run_once(models)
        if not killer.kill_now:
            time.sleep(LOOP_INTERVAL)
            
    logger.info("🛑 Daemon Stopped.")

if __name__ == "__main__":
    main()
