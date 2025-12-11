import requests
import time
import json
import os

# Configuration
API_URL = "http://localhost:8080"
API_KEY = "mysecretkey"
INSTANCE_NAME = "SistemChamados"
WEBHOOK_URL = "http://host.docker.internal:5000/webhook" 

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def delete_instance():
    print(f"🗑️ Deleting existing instance '{INSTANCE_NAME}' (if any)...")
    url = f"{API_URL}/instance/delete/{INSTANCE_NAME}"
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print("✅ Instance deleted.")
        else:
            print(f"ℹ️ Delete result: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error during delete: {e}")

def create_instance():
    print(f"✨ Creating Instance '{INSTANCE_NAME}'...")
    url = f"{API_URL}/instance/create"
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
        else:
            print(f"❌ Failed to create instance: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def set_webhook():
    print(f"\n🔗 Configuring Webhook to {WEBHOOK_URL}...")
    url = f"{API_URL}/webhook/set/{INSTANCE_NAME}"
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
    print(f"\n🔍 Fetching QR Code for '{INSTANCE_NAME}'...")
    url = f"{API_URL}/instance/connect/{INSTANCE_NAME}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            base64_qr = data.get("base64")
            if base64_qr:
                print("✅ QR Code received!")
                print("👉 CHECK TERMINAL LOGS NOW: docker logs -f evolution_api")
            else:
                print("ℹ️ No QR Code returned. Response:", data)
        else:
            print(f"❌ Error fetching QR: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    print("--- 🔄 Evolution API Reset & Setup ---")
    delete_instance()
    time.sleep(2)
    if create_instance():
        time.sleep(2)
        set_webhook()
        time.sleep(1)
        connect_instance()
