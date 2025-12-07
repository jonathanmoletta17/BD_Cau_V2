"""
SIS Ticket Actors Synchronization
Syncs ticket-user and ticket-group relationships for all tickets
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import config, Database
from src.core.glpi_client import GLPIClient
from src.modules.sis.tickets import Ticket, TicketUser, TicketGroup
from src.modules.sis.metadata import User, Group

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sync_ticket_actors_batch(client, session, ticket_ids, batch_start=0, batch_size=100):
    """Sync ticket actors for a batch of tickets."""
    batch_end = min(batch_start + batch_size, len(ticket_ids))
    batch_tickets = ticket_ids[batch_start:batch_end]
    
    logger.info(f"Processing tickets {batch_start+1}-{batch_end} of {len(ticket_ids)}...")
    
    # Get valid IDs for FK validation
    valid_users = set([u.id for u in session.query(User.id).all()])
    valid_groups = set([g.id for g in session.query(Group.id).all()])
    
    ticket_users_added = 0
    ticket_groups_added = 0
    skipped_users = 0
    skipped_groups = 0
    
    for ticket_id in batch_tickets:
        try:
            # Get ticket-user relationships from API
            try:
                ticket_users_data = client.make_request(f'Ticket/{ticket_id}/Ticket_User')
                
                for rel in ticket_users_data:
                    user_id = rel.get('users_id')
                    rel_type = rel.get('type', 1)  # 1=Requester, 2=Assigned, 3=Observer
                    
                    # Validate FK
                    if user_id not in valid_users:
                        # Create partial user record
                        partial_user = User(
                            id=user_id,
                            name=f"User_{user_id}",
                            is_active=True,
                            is_deleted=False
                        )
                        session.merge(partial_user)
                        valid_users.add(user_id)
                    
                    # Check if already exists (prevent duplicates)
                    existing = session.query(TicketUser).filter_by(
                        ticket_id=ticket_id,
                        user_id=user_id,
                        type=rel_type
                    ).first()
                    
                    if not existing:
                        ticket_user = TicketUser(
                            ticket_id=ticket_id,
                            user_id=user_id,
                            type=rel_type
                        )
                        session.add(ticket_user)
                        ticket_users_added += 1
            except Exception as e:
                if '404' not in str(e):  # Ignore 404 (no relationships)
                    logger.debug(f"Could not fetch users for ticket {ticket_id}: {e}")
            
            # Get ticket-group relationships from API
            try:
                ticket_groups_data = client.make_request(f'Ticket/{ticket_id}/Group_Ticket')
                
                for rel in ticket_groups_data:
                    group_id = rel.get('groups_id')
                    rel_type = rel.get('type', 2)  # 1=Requester, 2=Assigned
                    
                    # Validate FK
                    if group_id not in valid_groups:
                        skipped_groups += 1
                        continue
                    
                    # Check if already exists
                    existing = session.query(TicketGroup).filter_by(
                        ticket_id=ticket_id,
                        group_id=group_id,
                        type=rel_type
                    ).first()
                    
                    if not existing:
                        ticket_group = TicketGroup(
                            ticket_id=ticket_id,
                            group_id=group_id,
                            type=rel_type
                        )
                        session.add(ticket_group)
                        ticket_groups_added += 1
            except Exception as e:
                if '404' not in str(e):
                    logger.debug(f"Could not fetch groups for ticket {ticket_id}: {e}")
        
        except Exception as e:
            logger.warning(f"Error processing ticket {ticket_id}: {e}")
    
    session.commit()
    logger.info(f"  ✓ Added {ticket_users_added} ticket-user, {ticket_groups_added} ticket-group relations")
    
    return ticket_users_added, ticket_groups_added


def main(test_mode=False, test_limit=100):
    """Main synchronization function."""
    print("=" * 70)
    print("GLPI_SIS TICKET ACTORS SYNCHRONIZATION")
    if test_mode:
        print(f"Mode: TEST (limit={test_limit} tickets)")
    else:
        print("Mode: FULL")
    print("=" * 70)
    print()
    
    start_time = datetime.now()
    
    try:
        # Create session
        session = Database.get_session(context="sis")
        
        # Get all ticket IDs
        ticket_ids = [t.glpi_id for t in session.query(Ticket.glpi_id).all()]
        logger.info(f"Found {len(ticket_ids)} tickets in database")
        
        if test_mode:
            ticket_ids = ticket_ids[:test_limit]
            logger.info(f"Test mode: processing first {len(ticket_ids)} tickets")
        
        # Create GLPI client
        with GLPIClient(
            config.GLPI_SIS_URL,
            config.GLPI_SIS_APP_TOKEN,
            config.GLPI_SIS_USER_TOKEN
        ) as client:
            
            # Process in batches
            batch_size = 100
            total_users = 0
            total_groups = 0
            
            for start in range(0, len(ticket_ids), batch_size):
                users_count, groups_count = sync_ticket_actors_batch(
                    client, session, ticket_ids, start, batch_size
                )
                total_users += users_count
                total_groups += groups_count
        
        session.close()
        
        # Summary
        duration = (datetime.now() - start_time).total_seconds()
        final_users = Database.get_session(context="sis").query(TicketUser).count()
        final_groups = Database.get_session(context="sis").query(TicketGroup).count()
        
        print("\n" + "=" * 70)
        print(f"[OK] TICKET ACTORS SYNC COMPLETED in {duration:.1f}s")
        print(f"Total Ticket-User relations: {final_users}")
        print(f"Total Ticket-Group relations: {final_groups}")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Full sync mode
    main(test_mode=False)

