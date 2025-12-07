"""
Create All Tables Script
Creates all tables in DTIC schema using SQLAlchemy models
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


def create_all_tables():
    """Create all tables in DTIC schema."""
    print("=" * 70)
    print("📊 CREATE ALL TABLES")
    print("=" * 70)
    print()
    
    print("Creating tables in DTIC schema...")
    
    # Get engine
    engine = Database._get_engine("dtic")
    
    # Import Base to get metadata
    from src.core.database import Base
    
    # Create all tables
    print("\n🔨 Creating tables from SQLAlchemy models...")
    Base.metadata.create_all(engine)
    
    print("\n✅ ALL TABLES CREATED")
    print("=" * 70)
    
    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names(schema='dtic')
    
    print("\n📋 Tables in DTIC schema:")
    for table in sorted(tables):
        print(f"   ✓ {table}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    create_all_tables()
