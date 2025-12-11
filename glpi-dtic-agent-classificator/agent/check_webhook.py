import requests
import json

API_URL = "http://localhost:3000"
API_KEY = "mysecretkey"
SESSION_NAME = "default"

def inspect_session():
    print(f"🔍 Inspecting session '{SESSION_NAME}' config...")
    headers = {"X-Api-Key": API_KEY}
    
    try:
        # Get specific session details
        response = requests.get(f"{API_URL}/api/sessions/{SESSION_NAME}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Current Configuration:")
            print(json.dumps(data, indent=2))
            
            config = data.get("config") or {}
            webhooks = config.get("webhooks") or []
            
            if not webhooks:
                print("\n❌ NO WEBHOOKS CONFIGURED!")
            else:
                for hook in webhooks:
                    print(f"\n🔗 Webhook URL: {hook.get('url')}")
                    print(f"   Events: {hook.get('events')}")
                    
        else:
            print(f"❌ Error fetching session: {response.text}")

    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    inspect_session()
