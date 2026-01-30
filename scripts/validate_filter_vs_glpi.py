
import os
import sys
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load Env
load_dotenv()

GLPI_URL = os.getenv("GLPI_DTIC_URL")
APP_TOKEN = os.getenv("GLPI_DTIC_APP_TOKEN")
USER_TOKEN = os.getenv("GLPI_DTIC_USER_TOKEN")
LOCAL_API_URL = "http://localhost:8000/api/v1/dtic"

HEADERS = {
    "App-Token": APP_TOKEN,
    "Authorization": f"user_token {USER_TOKEN}",
    "Content-Type": "application/json"
}

def get_session():
    try:
        resp = requests.get(f"{GLPI_URL}/initSession", headers=HEADERS, verify=False)
        if resp.status_code != 200:
            print(f"❌ Error initSession: {resp.text}")
            sys.exit(1)
        return resp.json()['session_token']
    except Exception as e:
        print(f"❌ Connection Error (GLPI): {e}")
        sys.exit(1)

def query_glpi_count(session_token, start_date, end_date):
    """Query GLPI for total tickets created in range."""
    headers = {**HEADERS, "Session-Token": session_token}
    
    # GLPI Range Search Criteria
    # 15 = Date (creation)
    # 80 = Entities (Root) - Optional if defaulting to user context
    
    # We use search/Ticket
    # criteria[0][field]=15 & criteria[0][searchtype]=morethan & criteria[0][value]=START
    # criteria[1][field]=15 & criteria[1][searchtype]=lessthan & criteria[1][value]=END
    # criteria[2][link]=AND
    # is_deleted=0
    
    params = {
        "criteria[0][field]": 15,
        "criteria[0][searchtype]": "morethan",
        "criteria[0][value]": start_date,
        "criteria[1][link]": "AND",
        "criteria[1][field]": 15,
        "criteria[1][searchtype]": "lessthan",
        "criteria[1][value]": end_date,
        "is_deleted": 0,
        "range": "0-1" # We only need total_count
    }
    
    resp = requests.get(f"{GLPI_URL}/search/Ticket", headers=headers, params=params, verify=False)
    if resp.status_code in [200, 206]:
        return resp.json().get('totalcount', 0)
    else:
        print(f"❌ GLPI Search Error: {resp.text}")
        return -1

def query_local_count(start_date, end_date):
    """Query Local API for total resolved + pending + progress + new (if applicable, but new ignores filter).
       Better: Use metrics-gerais and sum relevant fields, OR add a 'total' endpoint.
       For now, let's sum 'resolvidos' + 'em_progresso' + 'pendentes' for apples-to-apples.
       Note: 'Novos' ignores filter, so we exclude it from date-sensitive comparison?
       Wait, the user wants date filter validation. Autos/Novos is constant. 
       So we should compare 'Created in Range' vs 'Local Created in Range'.
       
       Actually, `metrics-gerais` filters by `criado_em`.
       So Sum(em_progresso + pendentes + resolvidos) + (Novos if they were created in that range?)
       'Novos' endpoint returns all. 
       
       Issue: Local 'Novos' logic ignores date.
       GLPI Search logic respects date.
       So GLPI 'Status=New AND Date=Range' might return 0, but Local 'Novos' returns 17.
       
       Comparison Strategy:
       Compare 'Resolvidos' (Solved/Closed) specifically.
       Or compare 'All Tickets Created in Range' (Local DB Query might be needed if API doesn't expose total).
       
       Let's stick to 'metrics-gerais' 'resolvidos' vs GLPI 'Status=Solved/Closed' in Range.
       Status IDs: 5 (Solved), 6 (Closed).
    """
    
    params = {
        "inicio": start_date,
        "fim": end_date
    }
    
    resp = requests.get(f"{LOCAL_API_URL}/metrics-gerais", params=params)
    if resp.status_code == 200:
        data = resp.json()
        return data.get('resolvidos', 0)
    return -1

def query_glpi_resolved_count(session_token, start_date, end_date):
    headers = {**HEADERS, "Session-Token": session_token}
    
    # Criteria: Date Range AND (Status = Solved OR Status = Closed)
    # This complex OR in GLPI search API is tricky via params.
    # Simplified: Just match Date Range for now to see TOTAL volume?
    # No, let's do Status=5 OR Status=6 logic is hard.
    # Let's count Status=Completed (which is 5 and 6 usually).
    
    # Let's filter by Date Range only first to validate volume.
    # But wait, local API returns breakdown.
    # Let's try to match 'Active' tickets?
    
    # Correct Approach defined in Plan:
    # "Compare Local DB metrics vs GLPI API metrics"
    # Local 'resolvidos' = 5,6.
    
    # GLPI Params for Status 5 or 6:
    # It's easier to verify 5 and 6 separately and sum them.
    
    total = 0
    for status in [5, 6]:
        params = {
            "criteria[0][field]": 15,
            "criteria[0][searchtype]": "morethan",
            "criteria[0][value]": start_date,
            "criteria[1][link]": "AND",
            "criteria[1][field]": 15,
            "criteria[1][searchtype]": "lessthan",
            "criteria[1][value]": end_date,
            "criteria[2][link]": "AND",
            "criteria[2][field]": 12, # Status
            "criteria[2][searchtype]": "equals",
            "criteria[2][value]": status,
            "is_deleted": 0,
            "range": "0-1"
        }
        resp = requests.get(f"{GLPI_URL}/search/Ticket", headers=headers, params=params, verify=False)
        if resp.status_code in [200, 206]:
            total += resp.json().get('totalcount', 0)
            
    return total

def main():
    print("⚖️  Starting Truth Comparator (Local vs GLPI)...")
    
    session_token = get_session()
    
    # Range: Last 30 Days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    start_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"📅 Range: {start_str} to {end_str}")
    
    # 1. Get GLPI Count (Resolved)
    print("🔎 Querying GLPI (Source)...")
    glpi_resolved = query_glpi_resolved_count(session_token, start_str, end_str)
    print(f"   => GLPI Resolved: {glpi_resolved}")
    
    # 2. Get Local Count (Resolved)
    print("🔎 Querying Local API (Target)...")
    local_resolved = query_local_count(start_date.isoformat(), end_date.isoformat())
    print(f"   => Local Resolved: {local_resolved}")
    
    # 3. Assert
    if glpi_resolved == local_resolved:
        print("\n✅ MATCH: Data is synchronized and filters are accurate.")
        sys.exit(0)
    else:
        diff = abs(glpi_resolved - local_resolved)
        print(f"\n❌ MISMATCH: Difference of {diff} tickets.")
        print("   Possible causes: Sync lag (check daemon), Timezone offset, or API filter logic difference.")
        sys.exit(1)

if __name__ == "__main__":
    main()
