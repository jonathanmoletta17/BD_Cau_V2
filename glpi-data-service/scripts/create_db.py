"""
Unified Database Creation Script
Creates all tables for all contexts (DTIC, SIS) using SQLAlchemy models.
"""
import sys
from pathlib import Path
from sqlalchemy import text

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database
from src.core.database import Base
from src.core.models import SyncState
from src.core.models import BootstrapState

# --- IMPORT ALL MODELS (To register in Base.metadata) ---

# 1. DTIC Models
from src.modules.dtic.metadata import (
    User as DticUser, Group as DticGroup, Entity as DticEntity, 
    ITILCategory as DticCategory, Location as DticLocation, 
    Profile as DticProfile, GroupUser as DticGroupUser, 
    ProfileUser as DticProfileUser
)
from src.modules.dtic.tickets import (
    Ticket as DticTicket, TicketUser as DticTicketUser, 
    TicketGroup as DticTicketGroup, TicketChange as DticTicketChange
)

# 2. SIS Models
from src.modules.sis.metadata import (
    User as SisUser, Group as SisGroup, Entity as SisEntity, 
    ITILCategory as SisCategory, Location as SisLocation, 
    Profile as SisProfile, GroupUser as SisGroupUser, 
    ProfileUser as SisProfileUser
)
from src.modules.sis.tickets import (
    Ticket as SisTicket, TicketUser as SisTicketUser, 
    TicketGroup as SisTicketGroup, TicketChange as SisTicketChange,
    TicketItem as SisTicketItem
)
from src.modules.sis.carregadores.models import Carregador as SisCarregador


def create_db():
    print("=" * 70)
    print("🛠️  GLPI DATA SERVICE - DATABASE SETUP")
    print("=" * 70)
    
    print("\n1. Initializing Database connection...")
    Database._initialize()
    engine = Database._engine
    
    print("\n2. Ensuring schemas exist...")
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS dtic"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS sis"))
        conn.commit()
    print("   ✅ Schemas 'dtic' and 'sis' verified.")
    
    print("\n3. Registered Tables:")
    keys = sorted(Base.metadata.tables.keys())
    dtic_tables = [k for k in keys if k.startswith('dtic.')]
    sis_tables = [k for k in keys if k.startswith('sis.')]
    
    print(f"   🔹 DTIC Tables ({len(dtic_tables)}):")
    for t in dtic_tables: print(f"      - {t}")
        
    print(f"   🔹 SIS Tables ({len(sis_tables)}):")
    for t in sis_tables: print(f"      - {t}")
    
    print("\n4. Creating/Updating Tables...")
    Base.metadata.create_all(engine)
    print("   ✅ All tables processed successfully.")
    
    print("\n" + "=" * 70)
    print("🏁 DATABASE SETUP COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    create_db()
