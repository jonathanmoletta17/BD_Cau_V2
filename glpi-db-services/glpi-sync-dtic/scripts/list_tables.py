
import sys
import os
from sqlalchemy import text

# Add paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
common_dir = os.path.join(os.path.dirname(parent_dir), 'common')

sys.path.append(parent_dir)
sys.path.append(common_dir)

from src.core.database import Database

def list_tables():
    session = None
    try:
        session = Database.get_session(schema="dtic")
        print("Tables in 'dtic' schema:")
        result = session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'dtic' ORDER BY table_name"))
        for row in result:
            print(f"- {row[0]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if session:
            session.close()

if __name__ == "__main__":
    list_tables()
