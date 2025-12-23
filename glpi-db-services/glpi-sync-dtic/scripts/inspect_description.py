
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Config
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "glpi_data")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def inspect_raw_content(ticket_glpi_id):
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Set schema
        conn.execute(text("SET search_path TO dtic"))
        
        # Query
        query = text("SELECT descricao as content FROM tickets WHERE glpi_id = :id")
        result = conn.execute(query, {"id": ticket_glpi_id}).fetchone()
        
        if result:
            print(f"--- RAW CONTENT FOR TICKET {ticket_glpi_id} ---")
            print(result.content)
            print("--- END RAW CONTENT ---")
            
            # Check for HTML tags
            if "<div" in result.content or "<p" in result.content or "<br" in result.content:
                print("\n[ANALYSIS]: Content appears to be HTML.")
            else:
                print("\n[ANALYSIS]: Content appears to be Plain Text.")
        else:
            print("Ticket not found.")

if __name__ == "__main__":
    inspect_raw_content(12092)
