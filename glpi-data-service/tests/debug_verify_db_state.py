"""
Deep DB Inspection Script
Verifies:
1. Postgres Version
2. Installed Extensions (specifically 'vector')
3. Table Schema for knowledge_entries
4. Actual Data Count and Sample
"""
import sys
import os
from pathlib import Path
from sqlalchemy import text

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database

# Override for local execution
os.environ["POSTGRES_HOST"] = "localhost"

def inspect_db():
    print("🔍 INSPECTING DATABASE STATE...")
    try:
        session = Database.get_session(context='dtic')
        
        # 1. Version
        ver = session.execute(text("SELECT version();")).scalar()
        print(f"\n[1] Postgres Version:\n    {ver}")
        
        # 2. Extensions
        print("\n[2] Checking Extensions:")
        exts = session.execute(text("SELECT extname, extversion FROM pg_extension;")).fetchall()
        vector_found = False
        for e in exts:
            print(f"    - {e.extname} (v{e.extversion})")
            if e.extname == 'vector': vector_found = True
            
        if vector_found:
            print("    ✅ 'vector' extension is INSTALLED and ACTIVE.")
        else:
            print("    ❌ 'vector' extension is MISSING. RAG will not work.")
            
        # 3. Data Count
        print("\n[3] Checking RAG Data (dtic.knowledge_entries):")
        try:
            count = session.execute(text("SELECT count(*) FROM dtic.knowledge_entries")).scalar()
            print(f"    📊 Total Embeddings: {count}")
            
            if count > 0:
                # Sample
                sample = session.execute(text("SELECT id, ticket_id, substring(content, 1, 60) FROM dtic.knowledge_entries LIMIT 1")).fetchone()
                print(f"    📝 Sample Entry: ID={sample[0]}, TicketID={sample[1]}")
                print(f"       Content Preview: '{sample[2]}...'")
        except Exception as e:
            print(f"    ⚠️ Error checking table: {e}")

        session.close()
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    inspect_db()
