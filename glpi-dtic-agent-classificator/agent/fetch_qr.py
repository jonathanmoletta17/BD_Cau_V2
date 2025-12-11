import requests
import time
import base64
from io import BytesIO
from PIL import Image

API_URL = "http://host.docker.internal:8080"
API_KEY = "mysecretkey"
INSTANCE_NAME = "SistemChamados"
HEADERS = {"apikey": API_KEY}

def fetch_qr():
    print(f"🔄 Polling QR Code for '{INSTANCE_NAME}' (Max 10 tries)...")
    url = f"{API_URL}/instance/connect/{INSTANCE_NAME}"
    
    for i in range(1, 11):
        try:
            print(f"   Attempt {i}...", end=" ")
            response = requests.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                b64 = data.get("base64")
                if b64:
                    print("✅ QR CODE RECEIVED!")
                    # Try to show it?
                    # For now just print instructions
                    print("Detailed Response Keys:", data.keys())
                    print("\n⭐⭐⭐ COPY THE BASE64 BELOW AND PASTE IN A BROWSER TO SEE QR (data:image/png;base64,...) ⭐⭐⭐")
                    print(b64[:50] + "..." + b64[-50:])
                    print("\nOr check docker logs again.")
                    return
                else:
                    print(f"⏳ No QR yet. Response: {data}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    fetch_qr()
