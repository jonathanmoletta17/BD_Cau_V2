import os
import requests
import time
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings()
load_dotenv()

GLPI_URL = os.getenv("GLPI_DTIC_URL")
APP_TOKEN = os.getenv("GLPI_DTIC_APP_TOKEN")
USER_TOKEN = os.getenv("GLPI_DTIC_USER_TOKEN")

headers = {
    "App-Token": APP_TOKEN,
    "User-Token": USER_TOKEN,
    "Content-Type": "application/json"
}

def create_ticket():
    print("🚀 Triggering GLPI Ticket Creation...")
    
    # Debug: Check tokens
    if not APP_TOKEN or not USER_TOKEN:
        print("❌ Missing App-Token or User-Token in env")
        return

    # 1. Init Session
    # Try passing tokens in params if headers fail
    session_url = f"{GLPI_URL}/initSession"
    params = {
        "app_token": APP_TOKEN,
        "user_token": USER_TOKEN
    }
    
    try:
        # Try with headers AND params to be sure
        session_res = requests.get(session_url, headers=headers, params=params, verify=False, timeout=10)
        
        if session_res.status_code != 200:
            print(f"❌ Failed to init session: {session_res.text}")
            return
        session_token = session_res.json().get('session_token')
        print(f"✅ Session Initialized: {session_token[:5]}...")
    except Exception as e:
        print(f"❌ Error initializing session: {e}")
        return

    # 2. Create Ticket with Session Token
    url = f"{GLPI_URL}/Ticket"
    active_headers = headers.copy()
    active_headers['Session-Token'] = session_token
    
    payload = {
        "input": {
            "name": "TESTE LIVE SYNC ⚡",
            "content": "Ticket criado automaticamente para validar sync.",
            "status": 1, # Novo
            "priority": 3,
            "entities_id": 0
        }
    }
    try:
        response = requests.post(url, headers=active_headers, json=payload, verify=False, timeout=10)
        if response.status_code in [200, 201]:
            print(f"✅ Ticket Created Successfully! ID: {response.json().get('id')}")
            
            # 3. Kill Session (Good Practice)
            requests.get(f"{GLPI_URL}/killSession", headers=active_headers, verify=False)
        else:
            print(f"❌ Failed to create ticket: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_ticket()
