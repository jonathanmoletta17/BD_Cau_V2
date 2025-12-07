"""
Drop All Tables Script
DANGER: Destroys ALL tables in DTIC schema
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
from sqlalchemy import text


def drop_all_tables():
    """Drop all tables from DTIC schema."""
    print("=" * 70)
    print("⚠️  DROP ALL TABLES - DESTROYING DATABASE STRUCTURE")
    print("=" * 70)
    
    response = input("\nType 'DROP TABLES' to confirm: ")
    if response != "DROP TABLES":
        print("❌ Cancelled")
        return
    
    print("\n🗑️  Dropping all tables...")
    
    # Get raw connection
    engine = Database._get_engine("dtic")
    
    with engine.connect() as conn:
        # Drop tables in reverse dependency order
        tables = [
            'tickets_groups',
            'tickets_users',
            'ticket_changes',
            'tickets',
            'glpi_profiles_users',
            'glpi_groups_users',
            'glpi_profiles',
            'glpi_itilcategories',
            'glpi_users',
            'glpi_groups',
            'glpi_locations',
            'glpi_entities'
        ]
        
        for table in tables:
            try:
                print(f"   Dropping dtic.{table}...")
                conn.execute(text(f"DROP TABLE IF EXISTS dtic.{table} CASCADE"))
                conn.commit()
            except Exception as e:
                print(f"   ⚠️  Error dropping {table}: {e}")
        
        print("\n✅ ALL TABLES DROPPED")
        print("=" * 70)


if __name__ == "__main__":
    drop_all_tables()
