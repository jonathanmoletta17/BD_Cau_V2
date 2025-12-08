import sys
from pathlib import Path
import requests
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_count():
    print("Checking SIS Counts...")
    
    url = Config.get_glpi_url('sis')
    app_token = Config.get_glpi_app_token('sis')
    user_token = Config.get_glpi_user_token('sis')
    
    if not url:
        print("SIS URL not found in config")
        return

    # Init Session
    session_url = f"{url}/initSession"
    headers = {
        'App-Token': app_token,
        'Authorization': f'user_token {user_token}'
    }
    
    print(f"Connecting to {url}...")
    try:
        resp = requests.get(session_url, headers=headers)
        resp.raise_for_status()
        session_token = resp.json().get('session_token')
        print("Session started.")
    except Exception as e:
        print(f"Failed to init session: {e}")
        return

    headers['Session-Token'] = session_token
    
    # Check Logs
    print("\n--- Checking Logs ---")
    log_url = f"{url}/Log"
    params = {
        'range': '0-1',
        'criteria[0][field]': 'itemtype',
        'criteria[0][searchtype]': 'equals',
        'criteria[0][value]': 'Ticket'
    }
    
    try:
        resp = requests.get(log_url, headers=headers, params=params)
        print(f"Status: {resp.status_code}")
        print(f"Content-Range Header: {resp.headers.get('Content-Range')}")
        print(f"Accept-Range Header: {resp.headers.get('Accept-Range')}")
        if resp.status_code == 200:
             data = resp.json()
             print(f"Items returned: {len(data)}")
    except Exception as e:
        print(f"Error: {e}")

    # Check Item_Ticket
    print("\n--- Checking Item_Ticket ---")
    it_url = f"{url}/Item_Ticket"
    params = {'range': '0-1'}
    
    try:
        resp = requests.get(it_url, headers=headers, params=params)
        print(f"Status: {resp.status_code}")
        print(f"Content-Range Header: {resp.headers.get('Content-Range')}")
        if resp.status_code == 200:
             data = resp.json()
             print(f"Items returned: {len(data)}")
    except Exception as e:
        print(f"Error: {e}")

    # Kill Session
    requests.get(f"{url}/killSession", headers=headers)
    print("\nSession killed.")

if __name__ == "__main__":
    check_count()
