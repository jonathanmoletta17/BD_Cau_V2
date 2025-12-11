import requests
import time
import json
import os

# Configuration
API_URL = "http://localhost:8080"
API_KEY = "mysecretkey"
INSTANCE_NAME = "SistemChamados"
# NOTE: "host.docker.internal" is used so the Container can talk to your Windows host
WEBHOOK_URL = "http://host.docker.internal:5000/webhook" 

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def create_instance():
    print(f"Creating Instance '{INSTANCE_NAME}'...")
    url = f"{API_URL}/instance/create"
    # UPDATED PAYLOAD FOR V2
    payload = {
        "instanceName": INSTANCE_NAME,
        "token": "secret_token_123",
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS" 
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            print("✅ Instance created successfully!")
            return True
        elif "already exists" in response.text or "already in use" in response.text:
            print("⚠️ Instance already exists (proceeding).")
            return True
        else:
            print(f"❌ Failed to create instance: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def set_webhook():
    print(f"\nConfiguring Webhook to {WEBHOOK_URL}...")
    url = f"{API_URL}/webhook/set/{INSTANCE_NAME}"
    # FIX: Wrap in "webhook" property for V2
    payload = {
        "webhook": {
            "url": WEBHOOK_URL,
            "enabled": True,
            "webhookByEvents": True,
            "events": ["MESSAGES_UPSERT"]
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 201 or '"id":' in response.text:
            print("✅ Webhook configured successfully!")
        else:
            print(f"❌ Failed to set webhook: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def connect_instance():
    print(f"\nFetching QR Code for '{INSTANCE_NAME}'...")
    url = f"{API_URL}/instance/connect/{INSTANCE_NAME}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Check for base64 or other status indicators
            base64_qr = data.get("base64")
            
            if base64_qr:
                print("✅ QR Code received!")
                print("👉 Open the Docker logs to inspect it visually:")
                print(f"   docker logs -f evolution_api")
            else:
                # If no base64, check if it says "CONNECTED"
                instance_data = data.get("instance", {})
                state = instance_data.get("state")
                if state == "open":
                    print("✅ Instance ALREADY CONNECTED! You can start the chat server.")
                else:
                    print(f"ℹ️ Status: {state}. Check logs for QR Code.")
        else:
            print(f"❌ Error fetching QR: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    print("--- Evolution API Setup ---")
    if create_instance():
        time.sleep(2) # Wait a bit for initialization
        set_webhook()
        connect_instance()
    
    print("\n--- Next Steps ---")
    print("1. If you haven't scanned the QR Code yet, run: docker logs -f evolution_api")
    print("2. Scan the code with your WhatsApp")
    print("3. Start the Python Chat Server: python chat_server.py")
