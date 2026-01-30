"""
Backfill Ticket Actors Script
Usage: python scripts/backfill_actors.py --context <dtic|sis>
"""
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Config, Database
from src.services.sync_service import SyncService
from src.core.glpi_client import GLPIClient

# Import Models dynamically
import src.modules.dtic.metadata as dtic_meta
import src.modules.dtic.tickets as dtic_tickets
import src.modules.sis.metadata as sis_meta
import src.modules.sis.tickets as sis_tickets

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - BACKFILL - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_models(context):
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
            'TicketChange': sis_tickets.TicketChange
        }
    return None

def run_backfill(context):
    logger.info(f"🚀 Starting Actor Backfill for {context.upper()}")
    
    models = get_models(context)
    if not models:
        logger.error("❌ Unknown context")
        return

    url = Config.get_glpi_url(context)
    app_token = Config.get_glpi_app_token(context)
    user_token = Config.get_glpi_user_token(context)

    if not url:
        logger.error("❌ Config missing")
        return

    session = Database.get_session(context=context)
    
    try:
        with GLPIClient(url, app_token, user_token) as client:
            # Load Valid IDs
            logger.info("   [LOAD] Loading Valid IDs...")
            valid_ids = {
                'users': set(r.id for r in session.query(models['User'].id).all()),
                'groups': set(r.id for r in session.query(models['Group'].id).all()),
            }
            logger.info(f"   ✅ Loaded {len(valid_ids['users'])} users and {len(valid_ids['groups'])} groups.")

            # Run Sync
            SyncService.sync_ticket_actors(client, session, models, valid_ids)
            
        logger.info("🎉 Backfill Completed")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--context', required=True, choices=['dtic', 'sis'])
    args = parser.parse_args()
    
    run_backfill(args.context)
