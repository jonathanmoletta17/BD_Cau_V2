import requests
import json

API_URL = "http://localhost:8080"
API_KEY = "mysecretkey"
HEADERS = {"apikey": API_KEY}

def check_status():
    url = f"{API_URL}/instance/fetchInstances"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            instances = response.json()
            # Debug Raw Response
            print(f"🔍 Raw Response: {json.dumps(instances, indent=2)}")
            
            if isinstance(instances, list):
                if not instances:
                    print("⚠️ No instances found.")
                    return
                
                for inst in instances:
                    # Try to handle V2 structure which might be different
                    name = inst.get("instance", {}).get("instanceName") or inst.get("name")
                    status = inst.get("instance", {}).get("status") or inst.get("status") or inst.get("connectionStatus")
                    print(f"🔹 Instance: {name} | Status: {status}")
            else:
                 # Single instance object or different structure
                 print(f"ℹ️ Response: {instances}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    check_status()
