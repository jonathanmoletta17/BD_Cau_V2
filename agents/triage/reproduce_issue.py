import sys
import os
import asyncio
from pathlib import Path

# Setup path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

# Mock environment if needed (or rely on existing .env if loaded by config)
# We want to see if it fails with CURRENT environment.

from src.services.glpi_client import GLPIClient

async def test_client():
    print("Initializing Client...")
    try:
        client = GLPIClient()
        print(f"Read URL: {client.read_url}")
        print(f"Read Token: {client.read_app_token}")
        print(f"Write URL: {client.write_url}")
        print(f"Write Token: {client.write_app_token}")
        
        if client.write_app_token is None:
            print("ERROR: Write App Token is None!")
        
        print("Attempting init_session...")
        await client.init_session()
        print("Session Initialized.")
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_client())
