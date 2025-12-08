"""
Unified Sync CLI Script
Orchestrates synchronization for specified contexts.

Usage:
  python scripts/sync.py [--context <dtic|sis|all>] [--type <metadata|tickets|all>]
"""
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Config, Database
from src.core.glpi_client import GLPIClient
from src.services.sync_service import SyncService

# Import Models dynamically
import src.modules.dtic.metadata as dtic_meta
import src.modules.dtic.tickets as dtic_tickets
import src.modules.sis.metadata as sis_meta
import src.modules.sis.tickets as sis_tickets
import src.modules.sis.carregadores.models as sis_carregadores

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SYNC - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_models(context):
    """Return model classes for a context."""
    if context == 'dtic':
        return {
            'User': dtic_meta.User,
            'Group': dtic_meta.Group,
            'Entity': dtic_meta.Entity,
            'Location': dtic_meta.Location,
            'Category': dtic_meta.ITILCategory,
            'Profile': dtic_meta.Profile,
            'GroupUser': dtic_meta.GroupUser,
            'ProfileUser': dtic_meta.ProfileUser,
            'Ticket': dtic_tickets.Ticket,
            'TicketUser': dtic_tickets.TicketUser,
            'TicketGroup': dtic_tickets.TicketGroup,
            'TicketChange': dtic_tickets.TicketChange
            # DTIC doesn't have TicketItem usage yet
        }
    elif context == 'sis':
        return {
            'User': sis_meta.User,
            'Group': sis_meta.Group,
            'Entity': sis_meta.Entity,
            'Location': sis_meta.Location,
            'Category': sis_meta.ITILCategory,
            'Profile': sis_meta.Profile,
            'GroupUser': sis_meta.GroupUser,
            'ProfileUser': sis_meta.ProfileUser,
            'Ticket': sis_tickets.Ticket,
            'TicketUser': sis_tickets.TicketUser,
            'TicketGroup': sis_tickets.TicketGroup,
            'TicketChange': sis_tickets.TicketChange,
            'TicketItem': sis_tickets.TicketItem,
            'Carregador': sis_carregadores.Carregador
        }
    return None


def run_sync(context, sync_type, limit=None):
    print("\n" + "=" * 60)
    print(f"[START] SYNC: Context={context.upper()}, Type={sync_type.upper()}{f', Limit={limit}' if limit else ''}")
    print("=" * 60)
    
    # 1. Models
    models = get_models(context)
    if not models:
        logger.error(f"❌ Unknown context: {context}")
        return
    
    # 2. Config & Client
    url = Config.get_glpi_url(context)
    app_token = Config.get_glpi_app_token(context)
    user_token = Config.get_glpi_user_token(context)
    
    if not url:
        logger.error(f"❌ Configuration missing for {context} (URL not set)")
        return

    try:
        # 3. Session
        session = Database.get_session(context=context)
        
        with GLPIClient(url, app_token, user_token) as client:
            
            # --- Metadata Sync ---
            if sync_type in ['all', 'metadata']:
                SyncService.sync_entities(client, session, models['Entity'])
                SyncService.sync_locations(client, session, models['Location'])
                SyncService.sync_groups(client, session, models['Group'])
                SyncService.sync_users(client, session, models['User'])
                SyncService.sync_categories(client, session, models['Category'])
                SyncService.sync_profiles(client, session, models['Profile'])
                
                # Custom Assets (SIS only)
                if context == 'sis' and 'Carregador' in models:
                    SyncService.sync_carregadores(client, session, models['Carregador'])
                
                # Relations need checking valid IDs
                logger.info("   [LOAD] Loading IDs for FK validation...")
                valid_ids = {
                    'users': set(r.id for r in session.query(models['User'].id).all()),
                    'groups': set(r.id for r in session.query(models['Group'].id).all()),
                    'profiles': set(r.id for r in session.query(models['Profile'].id).all()),
                    'entities': set(r.id for r in session.query(models['Entity'].id).all())
                }
                
                SyncService.sync_groups_users(client, session, models['GroupUser'], valid_ids)
                SyncService.sync_profiles_users(client, session, models['ProfileUser'], valid_ids)
            
            # --- Tickets Sync ---
            if sync_type in ['all', 'tickets']:
                # Reload valid IDs if not loaded (isolated run)
                valid_ids = {
                    'users': set(r.id for r in session.query(models['User'].id).all()),
                    'groups': set(r.id for r in session.query(models['Group'].id).all()),
                    'entities': set(r.id for r in session.query(models['Entity'].id).all()),
                    'locations': set(r.id for r in session.query(models['Location'].id).all()),
                    'categories': set(r.id for r in session.query(models['Category'].id).all()),
                }
                
                SyncService.sync_tickets(client, session, models['Ticket'], valid_ids, context, limit)
                SyncService.sync_ticket_actors(client, session, models, valid_ids, limit)
                SyncService.sync_ticket_changes(client, session, models, valid_ids, limit)
                
                # Sync Ticket Items (Assets)
                if 'TicketItem' in models:
                    SyncService.sync_ticket_items(client, session, models, valid_ids, limit)
                
        session.close()
        print(f"\n[OK] SYNC COMPLETE for {context.upper()}")
        
    except Exception as e:
        logger.error(f"[ERROR] Sync Failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description='GLPI Sync Tool')
    parser.add_argument('--context', choices=['dtic', 'sis', 'all'], default='all')
    parser.add_argument('--type', choices=['metadata', 'tickets', 'all'], default='all')
    parser.add_argument('--limit', type=int, help='Limit number of tickets/changes for testing', default=None)
    
    args = parser.parse_args()
    
    contexts = ['dtic', 'sis'] if args.context == 'all' else [args.context]
    
    start_time = datetime.now()
    
    for ctx in contexts:
        run_sync(ctx, args.type, args.limit)

        
    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print(f"[DONE] ALL TASKS COMPLETED in {duration:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
