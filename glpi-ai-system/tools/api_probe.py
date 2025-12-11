import os
import requests
import json
from dotenv import load_dotenv

# Carrega .env
load_dotenv('glpi-ai-system/.env')

GLPI_URL = os.getenv("GLPI_TEST_URL")
USER_TOKEN = os.getenv("GLPI_TEST_USER_TOKEN")
APP_TOKEN = os.getenv("GLPI_TEST_APP_TOKEN")

headers = {
    "App-Token": APP_TOKEN,
    "Authorization": f"user_token {USER_TOKEN}",
    "Content-Type": "application/json"
}

def probe_api():
    print(f"📡 Probando API: {GLPI_URL}")
    
    # 1. Init Session
    session_url = f"{GLPI_URL}/initSession"
    resp = requests.get(session_url, headers=headers)
    if resp.status_code != 200:
        print(f"❌ Falha ao iniciar sessão: {resp.text}")
        return
    
    session_token = resp.json().get("session_token")
    print(f"✅ Sessão iniciada: {session_token[:10]}...")
    
    sess_headers = headers.copy()
    sess_headers["Session-Token"] = session_token
    
    # 2. List Tickets (Get recent ones)
    # Range 0-5
    list_url = f"{GLPI_URL}/Ticket?range=0-5&sort=id&order=DESC"
    resp = requests.get(list_url, headers=sess_headers)
    
    if resp.status_code in [200, 206]:
        tickets = resp.json()
        print(f"✅ Listagem de Tickets OK. Encontrados: {len(tickets)}")
        if len(tickets) > 0:
            t = tickets[0]
            print(f"   Último Ticket ID: {t['id']} - {t['name']}")
    else:
        print(f"❌ Falha ao listar tickets: {resp.status_code} - {resp.text}")

    # 3. Simulate Update (Probe Options for Categories)
    # We won't actually update yet, just check if we can list Categories to map IDs?
    # Actually, RAG uses its own IDs, but we need GLPI Category IDs for the API update.
    # The taxonomy.yaml has 'id' strings like '1_hardware...', GLPI needs INT IDs.
    # We might need a 'Category Mapper' step or assume names match.
    # Let's check listing categories.
    cat_url = f"{GLPI_URL}/ITILCategory?range=0-5"
    resp = requests.get(cat_url, headers=sess_headers)
    if resp.status_code in [200, 206]:
        cats = resp.json()
        print(f"✅ Listagem de Categorias GLPI OK.")
        for c in cats:
            print(f"   [ID {c['id']}] {c['completename']}")
    else:
        print(f"❌ Falha ao listar categorias: {resp.text}")

    # 4. Kill Session
    requests.get(f"{GLPI_URL}/killSession", headers=sess_headers)
    print("👋 Sessão encerrada.")

if __name__ == "__main__":
    probe_api()
