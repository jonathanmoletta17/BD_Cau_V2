import requests
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# CONFIG
GLPI_PROD_URL = os.getenv("GLPI_PROD_URL")
GLPI_PROD_APP_TOKEN = os.getenv("GLPI_PROD_APP_TOKEN")

GLPI_TEST_URL = os.getenv("GLPI_TEST_URL")
GLPI_TEST_APP_TOKEN = os.getenv("GLPI_TEST_APP_TOKEN")
GLPI_TEST_USER_TOKEN = os.getenv("GLPI_TEST_USER_TOKEN")

def test_prod_connectivity():
    print(f"\n[1] TESTING PROD CONNECTIVITY: {GLPI_PROD_URL}")
    if not GLPI_PROD_URL:
        print("SKIP: GLPI_PROD_URL not set")
        return

    url = f"{GLPI_PROD_URL}/initSession"
    headers = {
        "App-Token": GLPI_PROD_APP_TOKEN,
        "Content-Type": "application/json"
    }
    # attempts a raw connect without user auth to see if API responds (should be 401 or 400 but reachable)
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"STATUS: {r.status_code}")
        print(f"RESPONSE: {r.text[:100]}...")
        if r.status_code in [400, 401]: 
            print("RESULT: PASS (Service Reachable)")
        else:
            print("RESULT: UNEXPECTED STATUS")
    except Exception as e:
        print(f"RESULT: ERROR (Network/DNS): {e}")

def test_test_env_token():
    print(f"\n[2] TESTING TEST ENV AUTH (User Token): {GLPI_TEST_URL}")
    if not GLPI_TEST_URL:
        print("SKIP: GLPI_TEST_URL not set")
        return

    url = f"{GLPI_TEST_URL}/initSession"
    headers = {
        "App-Token": GLPI_TEST_APP_TOKEN,
        "Authorization": f"user_token {GLPI_TEST_USER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.get(f"{url}?get_full_session=true", headers=headers, timeout=5)
        if r.status_code in [200, 206]:
            print(f"RESULT: SUCCESS (Session Token: {r.json().get('session_token')})")
            # Kill session to be polite
            sess = r.json().get('session_token')
            requests.get(f"{GLPI_TEST_URL}/killSession", headers={"App-Token": GLPI_TEST_APP_TOKEN, "Session-Token": sess})
        else:
            print(f"RESULT: FAIL ({r.status_code})")
            print(f"BODY: {r.text}")
    except Exception as e:
        print(f"RESULT: ERROR: {e}")

if __name__ == "__main__":
    test_prod_connectivity()
    test_test_env_token()
