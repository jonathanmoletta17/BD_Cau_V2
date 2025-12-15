import asyncio
import sys
from pathlib import Path
import os

# Adiciona o diretório atual ao PYTHONPATH
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from main import container

async def test_logins():
    client = container.glpi_client
    
    creds = [
        ("glpi", "glpi"),
        ("post-only", "postonly"),
        ("tech", "tech"),
        ("normal", "normal"),
        ("jonathan-moletta", "admin"),            # Username from screenshot?
        ("jonathan.moletta@email.com", "admin")   # Email form?
    ]
    
    print(f"--- Testing Login on TEST: {os.getenv('GLPI_TEST_URL')} ---")
    
    for user, pwd in creds:
        print(f"\nTrying user: '{user}' ...")
        try:
            # Manually call _post_no_auth to test specific URL regardless of client config
            url = f"{os.getenv('GLPI_TEST_URL')}/initSession"
            headers = {
                "App-Token": os.getenv('GLPI_TEST_APP_TOKEN'),
                "Content-Type": "application/json"
            }
            # Need to use internal client method or just httpx? 
            # GLPIClient.login_on_prod is hardcoded to use self.prod_url.
            # I will just create a temporary client pointing to test or use pure httpx.
            import httpx
            async with httpx.AsyncClient() as c:
                resp = await c.get(url, headers=headers, auth=(user, pwd))
                if resp.status_code == 200:
                    print(f"✅ SUCCESS! User '{user}' works on TEST.")
                else:
                     print(f"❌ FAILED on TEST: {resp.status_code} - {resp.text}")

        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            
    return # End here for now

if __name__ == "__main__":
    asyncio.run(test_logins())
