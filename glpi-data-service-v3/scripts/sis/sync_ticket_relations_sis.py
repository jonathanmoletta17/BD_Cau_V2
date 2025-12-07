"""
SIS Ticket Relations Synchronization
Syncs ticket-user, ticket-group relationships for SIS tickets
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import config, Database
from src.core.glpi_client import GLPIClient
from src.modules.sis.tickets import Ticket, TicketUser, TicketGroup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sync_ticket_users(client, session):
    """Sync ticket-user relationships."""
    logger.info("🚀 Syncing Ticket-User relationships...")
    
    # Get all tickets
    tickets = session.query(Ticket.glpi_id).all()
    ticket_ids = [t.glpi_id for t in tickets]
    
    logger.info(f"   📥 Processing {len(ticket_ids)} tickets...")
    
    total = 0
    for ticket_id in ticket_ids:
        try:
            relations = client.make_request(f'Ticket/{ticket_id}/Ticket_User')
            if relations:
                for rel in relations:
                    ticket_user = TicketUser(
                        ticket_id=ticket_id,
                        user_id=rel.get('users_id'),
                        type=rel.get('type')
                    )
                    session.merge(ticket_user)
                    total += 1
        except:
            pass  # Ticket might not have user relations
        
        # Commit every 100 tickets
        if total % 100 == 0 and total > 0:
            session.commit()
            logger.info(f"   💾 Committed {total} relations...")
    
    session.commit()
    count = session.query(TicketUser).count()
    logger.info(f"   ✅ {count} ticket-user relationships in sis schema\n")


def sync_ticket_groups(client, session):
    """Sync ticket-group relationships."""
    logger.info("🚀 Syncing Ticket-Group relationships...")
    
    # Get all tickets
    tickets = session.query(Ticket.glpi_id).all()
    ticket_ids = [t.glpi_id for t in tickets]
    
    logger.info(f"   📥 Processing {len(ticket_ids)} tickets...")
    
    total = 0
    for ticket_id in ticket_ids:
        try:
            relations = client.make_request(f'Ticket/{ticket_id}/Group_Ticket')
            if relations:
                for rel in relations:
                    ticket_group = TicketGroup(
                        ticket_id=ticket_id,
                        group_id=rel.get('groups_id'),
                        type=rel.get('type')
                    )
                    session.merge(ticket_group)
                    total += 1
        except:
            pass  # Ticket might not have group relations
        
        # Commit every 100 tickets
        if total % 100 == 0 and total > 0:
            session.commit()
            logger.info(f"   💾 Committed {total} relations...")
    
    session.commit()
    count = session.query(TicketGroup).count()
    logger.info(f"   ✅ {count} ticket-group relationships in sis schema\n")


def main():
    """Main synchronization function."""
    print("=" * 70)
    print("SIS TICKET RELATIONS SYNCHRONIZATION")
    print("=" * 70)
    print()
    
    start_time = datetime.now()
    
    try:
        # Create session
        session = Database.get_session(context="sis")
        
        # Create GLPI client
        with GLPIClient(
            config.GLPI_SIS_URL,
            config.GLPI_SIS_APP_TOKEN,
            config.GLPI_SIS_USER_TOKEN
        ) as client:
            
            sync_ticket_users(client, session)
            sync_ticket_groups(client, session)
        
        session.close()
        
        # Summary
        duration = (datetime.now() - start_time).total_seconds()
        print("=" * 70)
        print(f"[OK] TICKET RELATIONS SYNC COMPLETED in {duration:.1f}s")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
