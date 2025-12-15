import asyncio
import sys
import os

# Add project root and agents/triage to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
triage_agent_root = os.path.join(project_root, 'agents', 'triage')

sys.path.append(project_root)
sys.path.append(triage_agent_root)

from src.services.glpi_client import GLPIClient
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

async def main():
    client = GLPIClient()
    print(f"--- Extracting Comments for User ID 141 (Jorge Vicente Junior) ---")
    user_id = 141
    
    if not client.session_token:
        await client.init_session()

    print(f"--- Debugging Ticket Fetch for User ID {user_id} ---")
    
    # 1. Simple fetch (no criteria) to verify auth/permissions
    print("Test 1: Fetching any 5 tickets...")
    url = f"{client.write_url}/Ticket"
    params_simple = {"range": "0-5"}
    headers = {
        "App-Token": client.write_app_token,
        "Session-Token": client.session_token
    }
    
    resp = await client.client.get(url, headers=headers, params=params_simple)
    print(f"Test 1 Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Test 1 Response: {resp.text}")
    else:
        print("Test 1 OK")

    # 2. Fetch with criteria
    print("\nTest 2: Fetching tickets for technician...")
    params = {
        "criteria[0][field]": 5, 
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": user_id,
        "range": "0-50",
        "sort": 19, # Sort by Date Mod
        "order": "DESC"
    }
    
    resp = await client.client.get(url, headers=headers, params=params)
    print(f"Test 2 Status: {resp.status_code}")
    
    if resp.status_code not in [200, 206]:
        print(f"Test 2 Response: {resp.text}")
        return

    tickets = resp.json()
    if isinstance(tickets, list) and len(tickets) > 0 and tickets[0] == "ERROR":
         print("Received ['ERROR'] from GLPI. This usually means invalid search criteria.")
         # Possible fix: some GLPI versions require values to be strings or ints specifically, or field 5 issues.
         return

    print(f"Found {len(tickets)} tickets.")
    
    detailed_comments = []
    import html

    for i, ticket in enumerate(tickets):
        ticket_id = ticket['id']
        ticket_name = ticket.get('name', 'No Title')
        
        print(f"Processing ticket {ticket_id} ({i+1}/{len(tickets)})...")
        
        try:
            f_url = f"{client.write_url}/Ticket/{ticket_id}/ITILFollowup"
            f_resp = await client.client.get(f_url, headers=headers)
            
            if f_resp.status_code == 200:
                followups = f_resp.json()
                for f in followups:
                    if f.get('users_id') == user_id:
                        raw_content = f.get('content', '')
                        content = html.unescape(raw_content).replace('&nbsp;', ' ').replace('<br>', '\n').replace('<p>', '').replace('</p>', '\n')
                        
                        detailed_comments.append({
                            "ticket_id": ticket_id,
                            "ticket_title": ticket_name,
                            "date": f.get('date'),
                            "content": content
                        })
        except Exception as e:
            print(f"Error processing ticket {ticket_id}: {e}")

    print(f"\n--- Found {len(detailed_comments)} comments by User {user_id} ---")
    
    import json
    detailed_comments.sort(key=lambda x: (x['ticket_id'], x['date']), reverse=True)
    
    output_file = "jorge_comments_report.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(detailed_comments, f, indent=2, ensure_ascii=False)
        
    print(f"Report saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
