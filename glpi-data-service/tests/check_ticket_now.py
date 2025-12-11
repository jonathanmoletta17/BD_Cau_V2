"""
Check Ticket 11909 Status (Concurrent Check)
"""
import sys
from pathlib import Path
from sqlalchemy import text

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database

def main():
    print("🔎 Checking Ticket 11909 Update Status...")
    session = Database.get_session(context='dtic')
    
    try:
        # Check Ticket
        query = text(f"SELECT glpi_id, titulo, status_id, atualizado_em, descricao FROM dtic.tickets WHERE glpi_id = 11909")
        result = session.execute(query).fetchone()
        
        if result:
            print(f"✅ Found Ticket 11909!")
            print(f"   - Title: {result.titulo}")
            print(f"   - Status: {result.status_id}")
            print(f"   - Updated At: {result.atualizado_em}")
            # Snippet of desc
            desc = result.descricao[:100] if result.descricao else "No Description"
            print(f"   - Desc: {desc}...")
        else:
            print("❌ Ticket 11909 NOT FOUND in DB yet.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
