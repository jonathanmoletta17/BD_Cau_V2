import sys
from pathlib import Path
from sqlalchemy import text, func

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database
from src.modules.sis.metadata import User, Group, Entity, ITILCategory
from src.modules.sis.tickets import Ticket, TicketChange, TicketItem, TicketUser, TicketGroup

def validate_sis_data():
    print("=" * 60)
    print("🔍 VALIDATION REPORT - SIS CONTEXT")
    print("=" * 60)
    
    Database._initialize()
    session = Database.get_session(context='sis')
    
    # 1. Counts
    print("\n1. Record Counts (Local DB):")
    counts = {
        'Users': session.query(User).count(),
        'Groups': session.query(Group).count(),
        'Entities': session.query(Entity).count(),
        'Categories': session.query(ITILCategory).count(),
        'Tickets': session.query(Ticket).count(),
        'Ticket Changes (Logs)': session.query(TicketChange).count(),
        'Ticket Items': session.query(TicketItem).count(),
        'Ticket Users': session.query(TicketUser).count(),
        'Ticket Groups': session.query(TicketGroup).count()
    }
    
    for k, v in counts.items():
        print(f"   - {k:<25}: {v}")
        
    # 2. Duplication Check (by GLPI ID)
    print("\n2. Duplication Check (GLPI IDs):")
    
    def check_dupes(model, name):
        dupes = session.query(model.glpi_id, func.count(model.glpi_id))\
            .group_by(model.glpi_id)\
            .having(func.count(model.glpi_id) > 1)\
            .all()
        if dupes:
            print(f"   ❌ Found duplicates in {name}: {len(dupes)} IDs duplicated.")
        else:
            print(f"   ✅ No duplicates found in {name}.")

    check_dupes(Ticket, 'Tickets')
    check_dupes(TicketChange, 'Ticket Changes')
    # TicketItem ID is the link ID, not GLPI Item ID.
    # My TicketItem model has 'id' as primary key which maps to GLPI Link ID.
    # So checking PK duplication is handled by DB constraint, but let's check just in case.
    # Actually TicketItem uses `id` as PK, so DB prevents it.
    
    # 3. Integrity Check
    print("\n3. Integrity Check:")
    
    # Check Tickets without valid Users (Requester)
    # This is complex because TicketUser links them.
    
    # Check if all TicketChanges point to valid Tickets
    orphaned_changes = session.query(TicketChange)\
        .outerjoin(Ticket, TicketChange.ticket_id == Ticket.id)\
        .filter(Ticket.id == None)\
        .count()
        
    if orphaned_changes > 0:
        print(f"   ⚠️ Found {orphaned_changes} orphaned ticket changes (no local ticket found).")
    else:
        print(f"   ✅ All ticket changes are linked to valid local tickets.")

    # Check if all TicketItems point to valid Tickets
    orphaned_items = session.query(TicketItem)\
        .outerjoin(Ticket, TicketItem.tickets_id == Ticket.glpi_id)\
        .filter(Ticket.glpi_id == None)\
        .count()
        
    # Note: TicketItem.tickets_id stores GLPI ID. Ticket.glpi_id stores GLPI ID.
    # Join condition: TicketItem.tickets_id == Ticket.glpi_id
    
    if orphaned_items > 0:
        print(f"   ⚠️ Found {orphaned_items} orphaned ticket items (ticket not found in DB).")
    else:
        print(f"   ✅ All ticket items are linked to valid tickets.")

    session.close()
    print("\n" + "=" * 60)
    print("DONE")

if __name__ == "__main__":
    validate_sis_data()
