"""
Database Cleanup Script
DANGER: Deletes ALL data from DTIC schema tables
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database
from src.modules.dtic.metadata import (
    User, Group, Entity, ITILCategory, Location, Profile,
    GroupUser, ProfileUser
)
from src.modules.dtic.tickets import Ticket, TicketUser, TicketGroup, TicketChange


def clean_database():
    """Delete all data from DTIC tables."""
    print("=" * 70)
    print("⚠️  DATABASE CLEANUP - DELETING ALL DATA")
    print("=" * 70)
    
    response = input("\nType 'DELETE ALL' to confirm: ")
    if response != "DELETE ALL":
        print("❌ Cancelled")
        return
    
    print("\n🗑️  Starting cleanup...")
    
    session = Database.get_session(context="dtic")
    
    try:
        # Delete in reverse dependency order
        print("   Deleting Ticket-Groups...")
        session.query(TicketGroup).delete()
        session.commit()
        
        print("   Deleting Ticket-Users...")
        session.query(TicketUser).delete()
        session.commit()
        
        print("   Deleting Ticket Changes...")
        session.query(TicketChange).delete()
        session.commit()
        
        print("   Deleting Tickets...")
        session.query(Ticket).delete()
        session.commit()
        
        print("   Deleting Profiles-Users...")
        session.query(ProfileUser).delete()
        session.commit()
        
        print("   Deleting Groups-Users...")
        session.query(GroupUser).delete()
        session.commit()
        
        print("   Deleting Profiles...")
        session.query(Profile).delete()
        session.commit()
        
        print("   Deleting Categories...")
        session.query(ITILCategory).delete()
        session.commit()
        
        print("   Deleting Users...")
        session.query(User).delete()
        session.commit()
        
        print("   Deleting Groups...")
        session.query(Group).delete()
        session.commit()
        
        print("   Deleting Locations...")
        session.query(Location).delete()
        session.commit()
        
        print("   Deleting Entities...")
        session.query(Entity).delete()
        session.commit()
        
        session.close()
        
        print("\n✅ ALL DATA DELETED")
        print("=" * 70)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    clean_database()
