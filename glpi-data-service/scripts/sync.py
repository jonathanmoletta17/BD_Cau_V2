"""
Unified Sync CLI Script
Orchestrates synchronization for specified contexts.

Usage:
  python scripts/sync.py [--context <dtic|sis|all>] [--type <metadata|tickets|all>]
"""
import sys
import argparse
import logging
import concurrent.futures
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Config, Database
from src.core.glpi_client import GLPIClient
from src.core.models import SyncState, OrphanChange  # ✅ Import SyncState & OrphanChange
from src.services.sync import SyncService

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
            'OrphanChange': src.core.models.OrphanChange,
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


def run_sync(context, sync_type, limit=None, incremental=False):
    print("\n" + "=" * 60)
    print(f"[START] SYNC: Context={context.upper()}, Type={sync_type.upper()}{f', Limit={limit}' if limit else ''}{', INCREMENTAL' if incremental else ''}")
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
                
                # Incremental Logic
                since_ticket = None
                since_changes = None
                
                start_ticket_sync = datetime.utcnow()
                
                if incremental:
                    # Fetch State
                    st_ticket = session.query(SyncState).filter_by(context=context, entity_type='Ticket').first()
                    st_changes = session.query(SyncState).filter_by(context=context, entity_type='TicketChange').first()
                    
                    if st_ticket and st_ticket.last_sync:
                        # Safety Margin (Lookback Window): Subtract 1 hour to catch late commits/clock skew
                        since_ticket = st_ticket.last_sync - timedelta(hours=1)
                        logger.info(f"   🕒 Incremental Ticket: Since {st_ticket.last_sync} (Lookback: {since_ticket})")
                    if st_changes and st_changes.last_sync:
                        since_changes = st_changes.last_sync - timedelta(hours=1)
                        logger.info(f"   🕒 Incremental Changes: Since {st_changes.last_sync} (Lookback: {since_changes})")
                
                # Sync Tickets
                max_ticket_date = SyncService.sync_tickets(client, session, models, valid_ids, context, limit, since_date=since_ticket)
                
                # Update State if Incremental AND no limit (Full Sync)
                if incremental and not limit and max_ticket_date:
                    if not st_ticket:
                        st_ticket = SyncState(context=context, entity_type='Ticket')
                        session.add(st_ticket)
                    
                    # Update ONLY if newer
                    if not st_ticket.last_sync or max_ticket_date > st_ticket.last_sync:
                        st_ticket.last_sync = max_ticket_date
                        logger.info(f"   💾 Cursor Updated (Ticket): {max_ticket_date}")
                    session.commit()
                elif incremental and limit:
                    logger.warning("   ⚠️ Incremental Sync with LIMIT: State NOT updated.")
                
                # Actors (Always full for now? Or depends on ticket? Usually tied to tickets)
                # Actors don't have date_mod easily accessible via API root usually, 
                # but if we sync tickets, we might want to refresh actors for those tickets?
                # For Phase 1, we leave actors as is (might be bottleneck later, but let's stick to plan)
                # Actually sync_ticket_actors is full scan?
                if not incremental:
                    SyncService.sync_ticket_actors(client, session, models, valid_ids, limit)
                else:
                    logger.info("   ℹ️ Skipping Actor Sync in Incremental Mode (Optimization)")
                
                # Sync Changes
                max_changes_date = SyncService.sync_ticket_changes(client, session, models, valid_ids, limit, since_date=since_changes)
                
                if incremental and not limit and max_changes_date:
                    if not st_changes:
                        st_changes = SyncState(context=context, entity_type='TicketChange')
                        session.add(st_changes)
                        
                    if not st_changes.last_sync or max_changes_date > st_changes.last_sync:
                        st_changes.last_sync = max_changes_date
                        logger.info(f"   💾 Cursor Updated (Changes): {max_changes_date}")
                    session.commit()
                elif incremental and limit:
                    logger.warning("   ⚠️ Incremental Sync with LIMIT: State NOT updated.")
                
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
    parser.add_argument('--incremental', action='store_true', help='Perform incremental sync based on last run')
    
    args = parser.parse_args()
    
    contexts = ['dtic', 'sis'] if args.context == 'all' else [args.context]
    
    start_time = datetime.now()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(contexts)) as executor:
        future_to_ctx = {
            executor.submit(run_sync, ctx, args.type, args.limit, args.incremental): ctx 
            for ctx in contexts
        }
        
        for future in concurrent.futures.as_completed(future_to_ctx):
            ctx = future_to_ctx[future]
            try:
                future.result()
            except Exception as exc:
                logger.error(f"❌ Context {ctx.upper()} generated an exception: {exc}")

        
    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print(f"[DONE] ALL TASKS COMPLETED (Parallel) in {duration:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
