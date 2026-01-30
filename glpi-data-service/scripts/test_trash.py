import sys
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.core import Config
from src.core.glpi_client import GLPIClient

logging.basicConfig(level=logging.INFO)

url = Config.get_glpi_url('dtic')
app_token = Config.get_glpi_app_token('dtic')
user_token = Config.get_glpi_user_token('dtic')

with GLPIClient(url, app_token, user_token) as client:
    # Try fetching the specific deleted ID
    # Usually ID 12467
    tid = 12467
    
    # 1. Direct Get (might fail if in trash and default is active)
    try:
        r = client.session.get(f"{client.base_url}/Ticket/{tid}", headers={
             'App-Token': client.app_token, 'Session-Token': client.session_token
        })
        print(f"Direct Get status: {r.status_code}")
        print(f"Direct Get data: {r.json().get('is_deleted')}")
    except Exception as e:
        print(f"Direct Get failed: {e}")

    # 2. Search with is_deleted=1
    print("Searching for is_deleted=1...")
    params = {
        'criteria[0][field]': 'is_deleted',
        'criteria[0][searchtype]': 'equals',
        'criteria[0][value]': '1',
        'criteria[1][link]': 'AND',
        'criteria[1][field]': 'id',
        'criteria[1][searchtype]': 'equals',
        'criteria[1][value]': str(tid)
    }
    r = client.session.get(f"{client.base_url}/Ticket", params=params, headers={
             'App-Token': client.app_token, 'Session-Token': client.session_token
        })
    print(f"Search Trash Result: {r.text}")
