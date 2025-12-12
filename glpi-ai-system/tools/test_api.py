import requests
import json

url = "http://localhost:8002/predict"
payload = {
    "summary": "Minha internet está lenta",
    "description": "Não consigo acessar nenhum site e o wifi cai toda hora"
}

try:
    print(f"📡 Sending request to {url}...")
    response = requests.post(url, json=payload, timeout=5)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Error: {response.text}")

except Exception as e:
    print(f"❌ Connection Failed: {e}")
