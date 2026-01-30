"""
Lookup ID for Peripherals
"""
import sys
import os
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.core import Database

# Override for local
os.environ["POSTGRES_HOST"] = "localhost"

def lookup():
    try:
        session = Database.get_session(context='dtic')
        query = text("SELECT id, completename FROM glpi_itilcategories WHERE completename LIKE '%Periféricos%' AND is_deleted = 0")
        results = session.execute(query).fetchall()
        for r in results:
            print(f"ID: {r.id} | Name: {r.completename}")
        session.close()
    except Exception as e:
        print(e)
    
if __name__ == "__main__":
    lookup()
