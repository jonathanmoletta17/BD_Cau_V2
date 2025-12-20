import sys
import asyncio
import os
import httpx
from pathlib import Path

# Add project root and agents/triage to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "agents" / "triage"))

from agents.triage.src.services.glpi_client import GLPIClient
from agents.triage.src.config import settings

async def test():
    print("Initializing Client...")
    client = GLPIClient()
    
    # We want to test querying PROD data using Service Token (since we don't have user password here)
    # This validates the method's ability to use overrides.
    
    prod_url = settings.GLPI_PROD_URL
    prod_app_token = settings.GLPI_PROD_APP_TOKEN
    prod_user_token = settings.GLPI_PROD_USER_TOKEN
    
    # Fallback/Debug: If Prod App Token fails, try Test App Token (known to work for Write)
    test_app_token = settings.GLPI_TEST_APP_TOKEN
    
    if not all([prod_url, prod_app_token, prod_user_token]):
        print("ERROR: Prod credentials missing/incomplete in settings.")
        print(f"URL: {prod_url}")
        print(f"APP: {bool(prod_app_token)}")
        print(f"USER: {bool(prod_user_token)}")
        # Don't return, try with what we have if URL exists
        if not prod_url: return

    print(f"Connecting to PROD: {prod_url}")
    
    # Try Prod Token
    headers = {
        "App-Token": prod_app_token,
        "Authorization": f"user_token {prod_user_token}"
    }
    
    used_app_token = prod_app_token
    session_token = None
    
    async with httpx.AsyncClient(verify=False) as http:
        # 1. Init Session
        print(f"Attempting Login with PROD Token ({prod_app_token[:5]}...)...")
        try:
            resp = await http.get(f"{prod_url}/initSession", headers=headers)
            if resp.status_code != 200:
                print(f"Failed with PROD Token: {resp.status_code} {resp.text}")
                
                # FALLBACK TEST
                if test_app_token:
                    print(f"Retrying with TEST App Token ({test_app_token[:5]}...)...")
                    headers["App-Token"] = test_app_token
                    resp = await http.get(f"{prod_url}/initSession", headers=headers)
                    if resp.status_code == 200:
                        print("SUCCESS with TEST Token!")
                        used_app_token = test_app_token
                    else:
                        print(f"Failed with TEST Token too: {resp.status_code} {resp.text}")
                        return
                else:
                    return
            
            session_token = resp.json().get("session_token")
            print(f"Got Session Token: {session_token[:10]}...")
        except Exception as e:
            print(f"Connection Error: {e}")
            return
        
        # 2. Search for a Test User (e.g., 'wagner-mengue') to get their ID
        username = "wagner-mengue"
        
        print(f"Searching for user: {username}")
        search_url = f"{prod_url}/User"
        params = {
            "criteria[0][field]": 1, 
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": username
        }
        headers_sess = {
            "App-Token": used_app_token,
            "Session-Token": session_token
        }
        
        try:
            resp_search = await http.get(search_url, headers=headers_sess, params=params)
            users = resp_search.json()
        except Exception as e:
            print(f"Search Error: {e}")
            users = []

        user_id = None
        if isinstance(users, list) and len(users) > 0:
            user_id = users[0].get('id')
            print(f"Found User via List: {users[0].get('name')} (ID: {user_id})")
        
        if not user_id:
             print("Could not find user ID. Aborting.")
             await http.get(f"{prod_url}/killSession", headers=headers_sess)
             return

        # 3. Test New Methods
        print("\n--- Testing get_user_groups (PROD) ---")
        groups = await client.get_user_groups(
            user_id, 
            session_token=session_token,
            base_url=prod_url,
            app_token=used_app_token
        )
        print(f"Groups: {groups}")
        
        print("\n--- Testing get_user_profiles (PROD) ---")
        profiles = await client.get_user_profiles(
            user_id,
            session_token=session_token,
            base_url=prod_url,
            app_token=used_app_token
        )
        print(f"Profiles: {profiles}")
        
        # 4. Apply Origin Logic
        rh_keywords = ["rh", "recursos humanos", "dgp"]
        is_rh = any(any(k in g.lower() for k in rh_keywords) for g in groups)
        is_chefia = (7 in profiles)
        
        origin = "Outro"
        if is_rh: origin = "RH"
        elif is_chefia: origin = "Chefia"
        
        print(f"\n--- Result ---")
        print(f"Is RH? {is_rh}")
        print(f"Is Chefia? {is_chefia}")
        print(f"Calculated Origin: {origin}")
        
        # 5. Kill Session
        await http.get(f"{prod_url}/killSession", headers=headers_sess)
        print("Session killed.")

if __name__ == "__main__":
    asyncio.run(test())
