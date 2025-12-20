import sys
import asyncio
import os
from pathlib import Path
from pprint import pprint

# Setup path to import src
current_dir = Path(__file__).resolve().parent
# Add agents/triage to path so 'src' can be imported as top-level
triage_path = current_dir.parent / "agents" / "triage"
sys.path.append(str(triage_path))

from src.services.glpi_client import GLPIClient
from src.config import settings

async def analyze():
    print(f"--- Analysis Started ---")
    print(f"Target Env: {settings.OPENER_TARGET_ENV}")
    
    # Check if tokens are present before crashing
    if not settings.GLPI_TEST_APP_TOKEN and settings.OPENER_TARGET_ENV.lower() != 'prod':
         print("WARNING: GLPI_TEST_APP_TOKEN is missing. Connection will likely fail.")

    try:
        client = GLPIClient()
        
        # --- OVERRIDE WITH PROD CREDENTIALS PROVIDED BY USER ---
        prod_url = "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php"
        prod_app_token = "2UVQ8P4gL2Z1xyo31liYpeSH2xaHjUQHJNABfuWO"
        prod_user_token = "QLtRd1m1egZwiRHgxLK2gJNt3FRSa7mW4Qa2hf3e"

        print(f"--- OVERRIDE: Using PROD credentials ---")
        client.write_url = prod_url
        client.write_app_token = prod_app_token
        client.write_user_token = prod_user_token
        client.read_url = prod_url # Just to be safe
        client.read_app_token = prod_app_token

    except Exception as e:
        print(f"Client Init Failed: {e}")
        return

    try:
        # Override creds... (already done above)
        
        # Init session
        if not await client.init_session():
            return
            
        headers = {
            "App-Token": client.write_app_token,
            "Session-Token": client.session_token
        }
        
        # 1. Fetch a sample of users
        print("\nFetching sample users...")
        resp = await client.client.get(f"{client.write_url}/User", headers=headers, params={"range": "0-5"})
        if resp.status_code not in [200, 206]:
            print(f"Failed to fetch users: {resp.status_code}")
            return
            
        users = resp.json()
        print(f"Found {len(users)} users. Analyzing metadata...")

        for user in users:
            user_id = user.get('id')
            name = user.get('name')
            print(f"\n--- User: {name} (ID: {user_id}) ---")
            
            # 2. Check Groups
            resp_groups = await client.client.get(f"{client.write_url}/User/{user_id}/Group", headers=headers)
            groups = resp_groups.json() if resp_groups.status_code == 200 else []
            group_names = [g.get('name') for g in groups] if isinstance(groups, list) else []
            print(f"Groups: {group_names}")
            
            # 3. Check Profiles (Target: Supervisor = Profile ID 7)
            print("Checking Profiles...")
            resp_profiles = await client.client.get(f"{client.write_url}/User/{user_id}/Profile", headers=headers)
            
            is_supervisor = False
            profiles_found = []
            
            if resp_profiles.status_code == 200:
                profiles_data = resp_profiles.json()
                if isinstance(profiles_data, list):
                    for p in profiles_data:
                        # Profile data structure has 'id' as the Profile ID
                        p_id = p.get('id')
                        p_name = p.get('name')
                        
                        profiles_found.append(f"{p_id} ({p_name})")
                        if str(p_id) == "7" or p_id == 7:
                            is_supervisor = True
                
                print(f"Profiles Found: {profiles_found}")
            else:
                print(f"Failed to fetch profiles: {resp_profiles.status_code}")

            print(f"Is Supervisor (Profile 7): {is_supervisor}")

    except Exception as e:
        print(f"Error: {e}")

    except Exception as e:
        print(f"Analysis Failed with Exception: {e}")

if __name__ == "__main__":
    asyncio.run(analyze())
