import os
import sys
import logging
from flask import Flask, request, jsonify
from typing import Dict

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.simple_agent import SimpleAgent

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [Chat] %(message)s')
logger = logging.getLogger("ChatServer")

app = Flask(__name__)

# --- Proxy Bypass for GLPI ---
# Avoids 407 Proxy Auth Required errors for internal IPs
os.environ["NO_PROXY"] = os.environ.get("NO_PROXY", "") + ",10.72.16.202,localhost,127.0.0.1"

import json
from typing import Dict, List

# --- In-Memory State Management ---
# Structure: { phone_number: [ {"role": "user", "content": "..."} ] }
conversations: Dict[str, List[Dict]] = {}

# Map Urgency/Impact to GLPI Ints (1-5)
# 5=Very Low, 4=Low, 3=Medium, 2=High, 1=Very High
GLPI_PRIORITY_MAP = {
    "High": 2,    # High
    "Medium": 3,  # Medium
    "Low": 4      # Low
}

# Initialize Agent (Heavy Model Loading)
logger.info("Initializing AI Agent...")
ai_agent = SimpleAgent()
logger.info("AI Agent initialized.")

# WAHA Configuration
WAHA_BASE_URL = os.getenv("WAHA_BASE_URL", "http://localhost:3000")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "mysecretkey")
WAHA_SESSION = "default"

def send_message(phone: str, text: str):
    """
    Sends a text message via WAHA API (WhatsApp HTTP API)
    """
    import requests
    
    url = f"{WAHA_BASE_URL}/api/sendText"
    
    payload = {
        "session": WAHA_SESSION,
        "chatId": f"{phone}@c.us" if "@" not in phone else phone,
        "text": text
    }
    
    headers = {
        "X-Api-Key": WAHA_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"Sending msg to {phone}: {text[:30]}...")
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code != 201:
            logger.error(f"WAHA Error {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "online", "service": "GLPI Chatbot Agent"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # Filter only message events
    event_type = data.get("event")
    if event_type != "message":
        return jsonify({"status": "ignored_event_type"}), 200
        
    session = data.get("session")
    if session != WAHA_SESSION:
        return jsonify({"status": "wrong_session"}), 200

    payload_data = data.get("payload", {})
    
    # Check for self-messages (fromMe)
    if payload_data.get("fromMe"):
        return jsonify({"status": "ignored_self"}), 200
    
    # Extract Sender
    sender = payload_data.get("from") # e.g. 555199999999@c.us
    if not sender:
        return jsonify({"status": "no_sender"}), 200
        
    # Extract Text
    text = payload_data.get("body")
    
    if not text:
         return jsonify({"status": "no_text"}), 200

    # Ensure format is just number
    phone = sender.split("@")[0]

    logger.info(f"📩 Processing message from {phone}: {text}")
    process_incoming_message(phone, text.strip(), sender)
    
    return jsonify({"status": "ok"}), 200

def process_incoming_message(phone: str, text: str, full_jid: str):
    logger.info(f"Processing Msg from {phone}: {text}")
    
    # 1. Init History if needed
    if phone not in conversations:
        conversations[phone] = []
        
    # 2. Append User Message
    conversations[phone].append({"role": "user", "content": text})
    
    # 3. Get AI Response
    # Limit History to last 10 turns to save tokens
    history_window = conversations[phone][-10:]
    response = ai_agent.handle_conversation(history_window)
    
    # 4. Check if it's a JSON Action or Text
    import re
    
    # Try to find JSON block { ... }
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    
    action_data = None
    if json_match:
        try:
            potential_json = json_match.group(0)
            action_data = json.loads(potential_json)
        except json.JSONDecodeError:
            action_data = None

    if action_data and action_data.get("action") == "create_ticket":
        # --- TICKET CREATION FLOW ---
        logger.info("🤖 AI decided to Create Ticket!")
        
        cat_name = action_data.get("category")
        cat_id = ai_agent.cat_map.get(cat_name)
        
        if not cat_id:
            # Fallback if AI halluncinated a category name slightly off
            # Re-run vector search to find closest ID
            logger.warning(f"Category '{cat_name}' not exact match. Using Vector Search fallback.")
            _, cat_id, _ = ai_agent.predict_category(action_data.get("title"))
        
        # Map Urgency/Impact
        urgency_val = GLPI_PRIORITY_MAP.get(action_data.get("urgency"), 3)
        impact_val = GLPI_PRIORITY_MAP.get(action_data.get("impact"), 3)
        
        title = f"[Whats] {action_data.get('title')}"
        description = f"""Chamado aberto via WhatsApp Chatbot.
        
Solicitante: {phone}
Descrição: {action_data.get('description')}

[AI Analysis]
Categoria: {cat_name}
Urgência: {action_data.get('urgency')}
Impacto: {action_data.get('impact')}
"""
        
        # Try to resolve User ID
        user_email = action_data.get("email")
        requester_id = None
        
        if user_email:
            requester_id = ai_agent.client.get_user_by_email(user_email)
            if requester_id:
                 logger.info(f"✅ User found via Email ({user_email}): ID {requester_id}")
        
        if not requester_id:
            logger.warning(f"⚠️ User not found for {user_email}. Ticket will be created as API User.")
            description += f"\n[WARNING] Usuário não encontrado. Email: {user_email} | Fone: {phone}"

        # Create Ticket
        new_id = ai_agent.client.create_ticket(
            name=title,
            content=description,
            category_id=cat_id,
            urgency=urgency_val,
            impact=impact_val,
            requester_id=requester_id
        )
        
        if new_id:
            send_message(full_jid, f"✅ Chamado criado com sucesso! Número: *#{new_id}*.\n\nCategoria: {cat_name}\nUrgência: {action_data.get('urgency')}")
            # Reset conversation
            conversations[phone] = []
        else:
            send_message(full_jid, "❌ Erro ao criar chamado no GLPI. Tente novamente.")
        
    else:
        # Should not happen given the prompt, but treat as text
        send_message(full_jid, str(response))
        conversations[phone].append({"role": "assistant", "content": str(response)})



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Chat Server on port {port}")
    app.run(host='0.0.0.0', port=port)
