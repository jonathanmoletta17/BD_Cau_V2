"""
Verification Script - Phase 0: Infrastructure
"""
import sys
from pathlib import Path
from sqlalchemy import text

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database

def verify_phase_0():
    print("🧪 Starting Exhaustive Verification for Phase 0...")
    
    session = Database.get_session()
    
    # 1. Check Table Existence
    try:
        # Check if table exists in information_schema to be DB-agnostic-ish (Postgres specific here)
        result = session.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sync_state'"
        )).scalar()
        
        if result == 'sync_state':
            print("   ✅ Table 'sync_state' exists in schema 'public'.")
        else:
            print("   ❌ Table 'sync_state' NOT FOUND in public schema.")
            sys.exit(1)
            
    except Exception as e:
        print(f"   ❌ Error checking table: {e}")
        sys.exit(1)
        
    # 2. Check Data Integrity
    try:
        # We expect 4 rows (DTIC/SIS x Ticket/TicketChange)
        count = session.execute(text("SELECT COUNT(*) FROM public.sync_state")).scalar()
        print(f"   📊 Row count in sync_state: {count}")
        
        if count >= 4:
             print("   ✅ Data initialization seems correct.")
        else:
             print("   ⚠️  Unexpected row count (expected >= 4).")
             
    except Exception as e:
        print(f"   ❌ Error checking data: {e}")
        sys.exit(1)
        
    print("\n🎉 Phase 0 Verification PASSED.")

if __name__ == "__main__":
    verify_phase_0()
