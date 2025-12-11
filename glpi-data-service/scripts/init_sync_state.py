"""
Initialize Sync State
Sets the initial timestamp for Incremental Sync.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database
from src.core.models import SyncState

def init_sync_state():
    print("=" * 60)
    print("🚦 INIT SYNC STATE")
    print("=" * 60)
    
    session = Database.get_session(context='dtic') # Context doesn't matter for public table
    
    contexts = ['dtic', 'sis']
    entities = ['Ticket', 'TicketChange'] # Entities we plan to sync incrementally
    
    # Default: Start from NOW (ignore old raw history for delta loop)
    # OR: Start from a specific date if we want to re-scan recent history
    # Let's start from 2024-01-01 to be safe? Or just NOW?
    # User said: "atualize todas as tabelas existentes... sem alterar codigo".
    # Implementation Plan said: "initialize... so we don't re-fetch history immediately".
    # If we want real-time from NOW, we set NOW.
    # If we want to catch up, we set older date. 
    # Let's set to Yesterday to catch any recent activity during dev.
    
    start_date = datetime.utcnow() - timedelta(days=15)
    
    try:
        for ctx in contexts:
            for ent in entities:
                state = session.query(SyncState).filter_by(
                    context=ctx, entity_type=ent
                ).first()
                
                if not state:
                    print(f"   [NEW] Creating state for {ctx.upper()} / {ent} -> {start_date}")
                    new_state = SyncState(
                        context=ctx, 
                        entity_type=ent, 
                        last_sync=start_date
                    )
                    session.add(new_state)
                else:
                    print(f"   [SKIP] State exists for {ctx.upper()} / {ent}: {state.last_sync}")
        
        session.commit()
        print("\n✅ Sync State Initialized.")
        
        # Verify
        all_states = session.query(SyncState).all()
        print("\n📊 Current States:")
        for s in all_states:
            print(f"   - {s.context} | {s.entity_type} : {s.last_sync}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_sync_state()
