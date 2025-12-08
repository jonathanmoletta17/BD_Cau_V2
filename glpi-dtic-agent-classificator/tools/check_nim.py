import requests
import json
import os
from dotenv import load_dotenv

# Load Env to get config
load_dotenv()

BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:9000/v1") 
# Force localhost for this host-side check if the env var uses host.docker.internal
if "host.docker.internal" in BASE_URL:
    BASE_URL = BASE_URL.replace("host.docker.internal", "localhost")

print(f"Checking NIM at: {BASE_URL}")

try:
    # Check Models
    resp = requests.get(f"{BASE_URL}/models")
    if resp.status_code == 200:
        print("✅ Connection Successful!")
        models = resp.json()
        print(f"Available Models: {json.dumps(models, indent=2)}")
    else:
        print(f"❌ Connected but Error: {resp.status_code}")
        print(resp.text)
except Exception as e:
    print(f"❌ Connection Failed: {e}")
