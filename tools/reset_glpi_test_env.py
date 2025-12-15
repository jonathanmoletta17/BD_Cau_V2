
import requests
import sys
import time

# ==============================================================================
# 🔒 SAFETY CONFIGURATION (HARDCODED)
# ==============================================================================
# DO NOT CHANGE THESE VALUES TO POINT TO PRODUCTION
TARGET_IP = "10.72.16.202"
TARGET_PATH = "/atual/"
FORBIDDEN_DOMAIN = "ppiratini"

GLPI_BASE_URL = "http://10.72.16.202/atual/apirest.php"
APP_TOKEN = "DCrrU5udtPELzURvQ8wI561U4yLInulor1RE3JRj"
USER_TOKEN = "skpUVqfIFO0FvcUuPrcVA3sZO37o9ADARpaar71f"
# ==============================================================================

def safety_check():
    print("\n🔒 EXECUTION SAFETY CHECK...")
    
    # 1. IP Check
    if TARGET_IP not in GLPI_BASE_URL:
        print(f"❌ SAFETY FAILURE: URL does not contain required IP {TARGET_IP}")
        sys.exit(1)
        
    # 2. Path Check
    if TARGET_PATH not in GLPI_BASE_URL:
        print(f"❌ SAFETY FAILURE: URL does not contain required path {TARGET_PATH}")
        sys.exit(1)
        
    # 3. Forbidden Domain Check
    if FORBIDDEN_DOMAIN in GLPI_BASE_URL:
        print(f"❌ SAFETY FAILURE: URL contains forbidden domain {FORBIDDEN_DOMAIN}")
        sys.exit(1)

    print("✅ Safety Checks Passed: Target is CONFIRMED as TEST Environment.")

def init_session():
    headers = {
        "App-Token": APP_TOKEN,
        "Authorization": f"user_token {USER_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.get(f"{GLPI_BASE_URL}/initSession", headers=headers)
        if r.status_code != 200:
            print(f"❌ Failed to init session: {r.text}")
            sys.exit(1)
        return r.json()['session_token']
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        sys.exit(1)

def kill_session(session_token):
    headers = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_token
    }
    requests.get(f"{GLPI_BASE_URL}/killSession", headers=headers)

def delete_items(session_token, item_type):
    """
    Deletes all items of a specific type (Ticket, ITILCategory).
    GLPI API Range Limit is usually 100 max via API unless configured otherwise.
    We will loop until empty.
    """
    headers = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }
    
    deleted_count = 0
    
    while True:
        # Get batch of items
        # range=0-100
        get_url = f"{GLPI_BASE_URL}/{item_type}?range=0-100" 
        r = requests.get(get_url, headers=headers)
        
        if r.status_code == 206 or r.status_code == 200:
            items = r.json()
            if not items:
                print(f"   ↳ No more {item_type}s found.")
                break
                
            print(f"   ↳ Found batch of {len(items)} {item_type}s. Deleting...")
            
            for item in items:
                item_id = item['id']
                del_url = f"{GLPI_BASE_URL}/{item_type}/{item_id}"
                
                # Force purge for Tickets (purge=true deletes permanently)
                # For Categories, usually standard delete is enough, but we can try purge too
                params = {"force_purge": "true"} 
                
                del_r = requests.delete(del_url, headers=headers, params=params)
                
                if del_r.status_code in [200, 204]:
                    print(f"     [✓] Deleted {item_type} ID {item_id}")
                    deleted_count += 1
                else:
                    print(f"     [X] Failed to delete {item_type} ID {item_id}: {del_r.status_code}")
            
            # Safety sleep to not hammer the server too hard
            # time.sleep(1) 
        else:
            print(f"   ↳ Failed to list {item_type}s or list is empty. Status: {r.status_code}")
            break
            
    print(f"✅ Finished deleting {item_type}s. Total removed: {deleted_count}")

def main():
    print("==============================================")
    print("   GLPI TEST ENV CLEANUP UTILITY")
    print("==============================================")
    
    safety_check()
    
    print("\n⚠️  WARNING: THIS WILL PERMANENTLY DELETE ALL DATA IN THE TARGET.")
    print(f"TARGET: {GLPI_BASE_URL}")

    # Initialize Session
    token = init_session()
    print(f"\n🔑 Session Initialized: {token}")
    
    try:
        # 1. Delete Tickets (Dependencies first)
        print("\n🗑️  STEP 1: Deleting ALL Tickets...")
        delete_items(token, "Ticket")
        
        # 2. Delete Categories
        print("\n🗑️  STEP 2: Deleting ALL Categories...")
        delete_items(token, "ITILCategory")
        
    finally:
        kill_session(token)
        print("\n🔒 Session Killed. Cleanup Complete.")

if __name__ == "__main__":
    main()
