import os
import time
import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configuration
# Match your docker-compose or .env settings
DB_USER = os.getenv("POSTGRES_USER", "glpi_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "glpi_secure_2024")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "glpi_data")

API_BASE_URL = "http://localhost:8000/api/v1/knowledge"

# GLPI Status IDs for Solved/Closed (Standard GLPI: 5=Solved, 6=Closed)
# Adjust if your instance uses different IDs
TARGET_STATUS_IDS = (5, 6)

def get_db_connection():
    # Helper to test connection
    def test_engine(host):
        url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{host}:{DB_PORT}/{DB_NAME}"
        try:
            engine = create_engine(url)
            with engine.connect() as conn:
                pass
            return engine
        except Exception as e:
            return None

    # Try configured host first
    print(f"🔌 Connecting to DB at {DB_HOST}...")
    engine = test_engine(DB_HOST)
    
    # Fallback to localhost if failed and host wasn't already localhost
    if not engine and DB_HOST != "localhost":
        print(f"⚠️  Connection to '{DB_HOST}' failed. Retrying with 'localhost'...")
        engine = test_engine("localhost")
        
    if not engine:
        raise Exception(f"Could not connect to database on '{DB_HOST}' or 'localhost'")
        
    print("✅ Database connection established.")
    return sessionmaker(bind=engine)()

def main():
    print("🚀 Starting Knowledge Base Population Script")
    print("-------------------------------------------")
    
    session = get_db_connection()
    
    try:
        # 1. Fetch Candidate Tickets
        # We want tickets that are Solved/Closed AND have a Solution (content not shown here but implied by status)
        # We verify existence in 'knowledge_entries' via LEFT JOIN or just let the API handle updates?
        # API is idempotent (checking internal ID), so we can just blindly feed Solved tickets.
        
        print("🔍 Fetching soluble tickets from database...")
        query = text("""
            SELECT glpi_id, titulo 
            FROM dtic.tickets 
            WHERE status_id IN :status_ids
            ORDER BY id DESC
            LIMIT 1000 -- Safety limit for first run
        """)
        
        result = session.execute(query, {"status_ids": tuple(TARGET_STATUS_IDS)}).fetchall()
        total_tickets = len(result)
        
        print(f"📄 Found {total_tickets} candidate tickets (Solved/Closed).")
        
        if total_tickets == 0:
            print("⚠️ No tickets found with status 5 or 6. Check your status IDs.")
            return

        print("\n⚡ Beginning Ingestion...")
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        with httpx.Client(timeout=60.0) as client:
            for i, row in enumerate(result):
                glpi_id = row.glpi_id
                title = row.titulo
                
                print(f"[{i+1}/{total_tickets}] Processing Ticket {glpi_id}...", end=" ", flush=True)
                
                try:
                    # Call the Learn Endpoint
                    resp = client.post(f"{API_BASE_URL}/learn/{glpi_id}")
                    
                    if resp.status_code == 200:
                        print("✅ Learned")
                        success_count += 1
                    elif resp.status_code == 404:
                         # Could happen if ticket exists in DB but API filters it out for some reason
                         print(f"⚠️ Skipped (API 404): {resp.text}")
                         skip_count += 1
                    else:
                        print(f"❌ Failed ({resp.status_code}): {resp.text}")
                        error_count += 1
                        
                    
                    # Throttle requests to avoid overwhelming Ollama (500 Error)
                    time.sleep(1.0)
                    
                except Exception as e:
                    print(f"❌ Network/Client Error: {e}")
                    error_count += 1
                    
        print("\n-------------------------------------------")
        print("🏁 Ingestion Complete")
        print(f"✅ Successfully Learned: {success_count}")
        print(f"⚠️ Skipped: {skip_count}")
        print(f"❌ Errors: {error_count}")
        
    except Exception as e:
        print(f"\n💥 Critical Database Error: {e}")
        print("Check your database connection settings in the script.")
    finally:
        session.close()

if __name__ == "__main__":
    main()
