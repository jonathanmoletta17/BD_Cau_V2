"""
GLPI Sync Service - SIS Context
Dedicated daemon for synchronizing SIS data.
"""
import sys
import time
import logging
import signal
from sqlalchemy import text # Import text logic
from pathlib import Path

# Add common library to path
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
import src.models.carregadores.models as carregadores

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SIS-SYNC - %(levelname)s - %(message)s',
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
    """Return model map for SIS."""
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
        'TicketItem': tickets.TicketItem, # SIS has TicketItem
        'TicketKnowledge': tickets.TicketKnowledge, # AI / RAG
        'Carregador': carregadores.Carregador 
    }

def run_once(models):
    """Single sync iteration."""
    # SIS Credentials
    url = config.GLPI_SIS_URL
    app_token = config.GLPI_SIS_APP_TOKEN
    user_token = config.GLPI_SIS_USER_TOKEN
    
    if not url:
        logger.error("❌ GLPI SIS URL not configured.")
        return

    session = Database.get_session(schema='sis')
    
    try:
        with GLPIClient(url, app_token, user_token) as client:
            client.init_session() # [FIX] Ensure session is initialized for metadata calls
            
            # 1. Sync Metadata (Full Sync Pattern)
            SyncService.sync_entities(client, session, models['Entity'])
            SyncService.sync_locations(client, session, models['Location'])
            SyncService.sync_groups(client, session, models['Group'])
            SyncService.sync_users(client, session, models['User'])
            SyncService.sync_categories(client, session, models['Category'])
            SyncService.sync_profiles(client, session, models['Profile'])
            
            # Load IDs for validation (Refresh after sync)
            valid_ids = {
                'users': set(r.id for r in session.query(models['User'].id).all()),
                'groups': set(r.id for r in session.query(models['Group'].id).all()),
                'entities': set(r.id for r in session.query(models['Entity'].id).all()),
                'locations': set(r.id for r in session.query(models['Location'].id).all()),
                'categories': set(r.id for r in session.query(models['Category'].id).all()),
                'profiles': set(r.id for r in session.query(models['Profile'].id).all()), # Added for relationships
            }
            
            # Sync Relationships
            SyncService.sync_groups_users(client, session, models['GroupUser'], valid_ids)
            SyncService.sync_profiles_users(client, session, models['ProfileUser'], valid_ids)

            # 2. Sync Tickets (Incremental)
            st = session.query(SyncState).filter_by(context='sis', entity_type='Ticket').first()
            since_date = st.last_sync if st else None
            
            def update_state(max_date):
                if not max_date: return
                local_st = session.query(SyncState).filter_by(context='sis', entity_type='Ticket').first()
                if not local_st:
                    local_st = SyncState(context='sis', entity_type='Ticket')
                    session.add(local_st)
                local_st.last_sync = max_date
                session.commit()

            SyncService.sync_tickets(
                client, session, models, valid_ids, context='sis', limit=None, 
                since_date=since_date,
                sync_state_manager=update_state
            )

            # Sync Ticket Actors
            SyncService.sync_ticket_actors(client, session, models, valid_ids, limit=None)

            # Sync Ticket Items
            if 'TicketItem' in models:
                 SyncService.sync_ticket_items(client, session, models, valid_ids, limit=None)

            # Sync Carregadores
            if 'Carregador' in models:
                 SyncService.sync_carregadores(client, session, models['Carregador'])
                 
            # 3. Sync Ticket Changes (Incremental)
            st_ch = session.query(SyncState).filter_by(context='sis', entity_type='TicketChange').first()
            since_changes = st_ch.last_sync if st_ch else None
            
            max_ch = SyncService.sync_ticket_changes(
                client, session, models, valid_ids, limit=None, since_date=since_changes
            )
            
            if max_ch:
                local_ch = session.query(SyncState).filter_by(context='sis', entity_type='TicketChange').first()
                if not local_ch:
                    local_ch = SyncState(context='sis', entity_type='TicketChange')
                    session.add(local_ch)
                local_ch.last_sync = max_ch
                session.commit()
            
            client.close_session() # Cleanup regex
            
    except Exception as e:
        logger.error(f"Error in sync loop: {e}")
    finally:
        session.close()

def main():
    logger.info("🚀 Starting SIS Sync Daemon...")
    
    # Init DB Schema
    logger.info("⚙️  Initializing Database Schema (SIS)...")
    try:
        engine = Database.get_engine()
        # Ensure 'sis' schema exists (Postgres specific) using raw SQL
        # However, create_all usually handles tables, not schema creation if it's not default?
        # Safe bet: Raw SQL for schema, then create_all
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS sis"))
            conn.commit()
            
        Base.metadata.create_all(engine)
        logger.info("✅ Database Schema Ready.")
    except Exception as e:
        logger.error(f"❌ Failed to init DB: {e}")
        # Retrying or exiting? Let's sleep and retry via restart policy
        sys.exit(1)

    killer = GracefulKiller()
    models = get_models()
    
    while not killer.kill_now:
        run_once(models)
        if not killer.kill_now:
            time.sleep(LOOP_INTERVAL)
            
    logger.info("🛑 Daemon Stopped.")

if __name__ == "__main__":
    main()
