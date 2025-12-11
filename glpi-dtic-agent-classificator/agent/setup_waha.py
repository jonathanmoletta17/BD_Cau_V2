import requests
import time
import sys

API_URL = "http://localhost:3000"
API_KEY = "mysecretkey"
SESSION_NAME = "default"

def check_session():
    print(f"🔍 Checking session '{SESSION_NAME}'...")
    try:
        # Get all sessions
        headers = {"X-Api-Key": API_KEY}
        response = requests.get(f"{API_URL}/api/sessions?all=true", headers=headers)
        if response.status_code != 200:
            print(f"❌ API Error: {response.text}")
            return False
            
        sessions = response.json()
        # Find our session
        session = next((s for s in sessions if s.get('name') == SESSION_NAME), None)
        
        if session:
            status = session.get('status')
            print(f"✅ Session found! Status: {status}")
            return status
        else:
            print("ℹ️ Session not found.")
            return None
            
    except Exception as e:
        print(f"❌ Connection Error (Is Docker running?): {e}")
        return False

def start_session():
    print(f"✨ Starting session '{SESSION_NAME}'...")
    payload = {
        "name": SESSION_NAME,
        "config": {
            "webhooks": [
                {
                    "url": "http://host.docker.internal:5000/webhook",
                    "events": ["message", "message.any"]
                }
            ]
        }
    }
    try:
        if response.status_code == 201:
            print("✅ Session created/started!")
            ensure_config()
            return True
        if response.status_code == 201: # Duplicate check removal
            print("✅ Session created/started!")
            ensure_config()
            return True
        elif response.status_code == 422: # Already exists but maybe stopped
             print("ℹ️ Session might already exist, trying to start...")
             requests.post(f"{API_URL}/api/sessions/{SESSION_NAME}/start", headers=headers)
             ensure_config()
             return True
        else:
            print(f"❌ Failed to start session: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting session: {e}")
        return False

def ensure_config():
    print("🔄 Updating session configuration...")
    headers = {"X-Api-Key": API_KEY}
    payload = {
        "config": {
            "webhooks": [
                {
                    "url": "http://host.docker.internal:5000/webhook",
                    "events": ["message", "message.any"]
                }
            ]
        }
    }
    config_payload = {"config": payload["config"]}
    
    try:
        # Try PATCH
        update_resp = requests.patch(f"{API_URL}/api/sessions/{SESSION_NAME}", json=config_payload, headers=headers)
        if update_resp.status_code != 200:
            # Try PUT
            update_resp = requests.put(f"{API_URL}/api/sessions/{SESSION_NAME}", json=config_payload, headers=headers)
            
        if update_resp.status_code == 200:
            print("✅ Configuration updated successfully!")
        else:
             print(f"⚠️ Failed to update config: {update_resp.text}")
    except Exception as e:
        print(f"❌ Error updating config: {e}")

def main():
    print("--- 🟢 WAHA Setup & Status ---")
    status = check_session()
    
    if status is False:
        print("❌ Could not connect to WAHA. Wait for Docker to finish starting.")
        return

    if status is None:
        if start_session():
            time.sleep(2)
            status = check_session()
    else:
        # Always ensure config is correct even if running
        ensure_config()
    
    if status == "SCAN_QR_CODE":
        print("\n📷 **ACTION REQUIRED** 📷")
        print("Go to the Dashboard to scan the QR Code:")
        print(f"👉 {API_URL}/dashboard (User: admin / Pass: admin)")
        
        # Download QR Image
        try:
            print("⬇️ Downloading QR Code to 'qr.png'...")
            headers = {"X-Api-Key": API_KEY}
            qr_response = requests.get(f"{API_URL}/api/{SESSION_NAME}/auth/qr", headers=headers)
            if qr_response.status_code == 200:
                # Some versions return image directly, others JSON with base64
                content_type = qr_response.headers.get('content-type', '')
                if 'image' in content_type:
                    with open('qr.png', 'wb') as f:
                        f.write(qr_response.content)
                    print("✅ Saved to qr.png! Open this file to scan.")
                    
                elif 'json' in content_type:
                    data = qr_response.json()
                    # Handle JSON response if needed (WAHA usually returns image on this endpoint or has a dedicated screenshot one)
                    print(f"ℹ️ API returned JSON. Check dashboard.")
            else:
                print(f"❌ Failed to download QR: {qr_response.status_code}")
        except Exception as e:
            print(f"❌ Error downloading QR: {e}")
            
        print(f"👉 Or view directly: {API_URL}/api/{SESSION_NAME}/auth/qr")
    elif status == "WORKING":
        print("\n✅ **SYSTEM READY** ✅")
        print("Bot is connected and ready to receive messages.")
    elif status == "STARTING":
         print("\n⏳ Session is starting... run this script again in 10 seconds.")
    elif status == "STOPPED":
        print("\n⚠️ Session is STOPPED. Attempting to start...")
        headers = {"X-Api-Key": API_KEY}
        try:
            requests.post(f"{API_URL}/api/sessions/{SESSION_NAME}/start", headers=headers)
            ensure_config()
            print("✅ Start command sent! Run this script again in 10 seconds.")
        except Exception as e:
            print(f"❌ Failed to restart: {e}")

if __name__ == "__main__":
    main()
