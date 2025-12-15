"""
Collect Recent Opener Tickets
Fetches the last 5 tickets created in GLPI to analyze their quality.
"""
import sys
import os
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database

# Override for local
os.environ["POSTGRES_HOST"] = "localhost"

def collect_examples():
    print("🔍 Collecting Recent Tickets...")
    try:
        session = Database.get_session(context='dtic')
        
        # Query last 5 tickets
        query = text("""
            SELECT id, glpi_id, titulo, descricao, urgency, impact, criado_em 
            FROM dtic.tickets 
            ORDER BY criado_em DESC 
            LIMIT 5
        """)
        
        tickets = session.execute(query).fetchall()
        
        for t in tickets:
            print("-" * 60)
            print(f"ID: {t.glpi_id} | Created: {t.criado_em}")
            print(f"Title: {t.titulo}")
            print(f"Urgency: {t.urgency} | Impact: {t.impact}")
            print(f"Description:\n{t.descricao}")
            print("-" * 60)

        session.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    collect_examples()
