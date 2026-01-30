"""
Monitor Database Population
"""
import time
import sys
from pathlib import Path
from sqlalchemy import text

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database

def get_counts(session):
    try:
        t_count = session.execute(text("SELECT COUNT(*) FROM dtic.tickets")).scalar()
        u_count = session.execute(text("SELECT COUNT(*) FROM dtic.users")).scalar()
        return t_count, u_count
    except Exception:
        return 0, 0

def main():
    print("📊 Monitoring Database Population (Ctrl+C to stop)...")
    print("Waits for DB connection...")
    
    # Wait loop for connection
    while True:
        try:
            session = Database.get_session(context='dtic')
            break
        except Exception:
            time.sleep(2)
            print(".", end="", flush=True)
    
    print("\n✅ Connected! Watching counts...")
    print(f"{'Time':<10} | {'Tickets':<10} | {'Users':<10}")
    print("-" * 35)
    
    no_change_count = 0
    last_t = -1
    
    for _ in range(20): # Monitor for ~100 seconds
        t, u = get_counts(session)
        print(f"{time.strftime('%H:%M:%S'):<10} | {t:<10} | {u:<10}")
        
        if t == last_t and t > 0:
            no_change_count += 1
        else:
            no_change_count = 0
            
        last_t = t
        
        if no_change_count >= 5:
            print("\n⏹️ Population seems stabilized.")
            break
            
        time.sleep(5)
    
    session.close()
    print("\n✅ Monitor Window Closed.")

if __name__ == "__main__":
    main()
