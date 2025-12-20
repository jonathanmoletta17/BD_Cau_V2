import sys
import json
import asyncio
from pathlib import Path
import httpx

# Setup path to import src if needed (not strictly needed for this standalone)
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

async def dump_options():
    # PROD CREDENTIALS (provided by user)
    url_base = "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php"
    app_token = "2UVQ8P4gL2Z1xyo31liYpeSH2xaHjUQHJNABfuWO"
    user_token = "QLtRd1m1egZwiRHgxLK2gJNt3FRSa7mW4Qa2hf3e"
    
    print(f"Connecting to: {url_base}")

    async with httpx.AsyncClient(verify=False) as client:
        # 1. Init Session
        headers_init = {
            "App-Token": app_token,
            "Authorization": f"user_token {user_token}",
            "Content-Type": "application/json"
        }
        
        try:
            resp = await client.get(f"{url_base}/initSession", headers=headers_init)
            resp.raise_for_status()
            session_token = resp.json().get('session_token')
            print(f"Session initialized: {session_token[:5]}...")
        except Exception as e:
            print(f"Session Init Failed: {e}")
            return

        # 2. Get Search Options for User
        headers = {
            "App-Token": app_token,
            "Session-Token": session_token
        }
        
        print("Fetching listSearchOptions/User...")
        try:
            resp = await client.get(f"{url_base}/listSearchOptions/User", headers=headers)
            resp.raise_for_status()
            
            data = resp.json()
            
            # Save to file for clear inspection
            output_path = Path("glpi_user_options.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            print(f"Options saved to {output_path.absolute()}")
            
        except Exception as e:
            print(f"Fetch Options Failed: {e}")

if __name__ == "__main__":
    asyncio.run(dump_options())
