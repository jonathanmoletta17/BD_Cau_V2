import chainlit as cl
import os
import sys
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Load Environment
load_dotenv()

# Add project root to sys.path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

# CRITICAL: Bootstrap Agent A environment (The ONE TRUE SRC)
agent_a_root = project_root / "agents" / "triage"
sys.path.insert(0, str(agent_a_root))

# NOTE: We DO NOT add glpi-data-service to path anymore to avoid 'src' conflict.
# We use Agent A's internal GLPI Client which is fully capable.

# Import Agent Graph
from agents.local_triage.graph import app
print("DEBUG: LOADING NEW GRAPH (HYBRID ENGINE) - VERSION PROTECTED")
# Import Agent A's GLPI Client
from src.services.glpi_client import GLPIClient
from langchain_core.messages import HumanMessage, AIMessage

# Configuration
if not os.getenv("CHAINLIT_AUTH_SECRET"):
    os.environ["CHAINLIT_AUTH_SECRET"] = secrets.token_urlsafe(32)

@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    """
    Hybrid Authentication (Async):
    - Validates credentials against GLPI PROD via Agent A Client.
    """
    client = GLPIClient()
    target_env = os.getenv("OPENER_TARGET_ENV", "test").lower()
    
    print(f"[UI] Authenticating {username} (Target: {target_env})...")
    
    # 1. Validate Credentials on PROD
    keep = (target_env == "prod")
    # Agent A login_on_prod is async
    res = await client.login_on_prod(username, password, keep_session=keep)
    
    if not res.get("ok"):
        print(f"[UI] Login Failed: {res.get('class')} - {res.get('detail')}")
        return None
        
    user_data = res.get("user_data", {})
    # Friendly name logic might differ slightly in Agent A's response structure
    # Agent A returns: { "session": { "glpifriendlyname": ... } }
    session_data = user_data.get("session", {})
    display_name = session_data.get("glpifriendlyname") or username
    
    # 2. Resolve User ID on TARGET
    user_id = None
    if target_env == "prod":
        user_id = session_data.get("glpiID")
    else:
        # Search on Test Env
        print(f"[UI] Searching ID for {username} on {target_env}...")
        # Agent A search_user_id is async
        user_id = await client.search_user_id(username)
        
    if not user_id:
        print(f"[UI] WARN: User {username} valid, but ID not found on target {target_env}.")
        pass
        
    return cl.User(identifier=display_name, metadata={"glpi_user_id": user_id, "username": username})

@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    user = cl.user_session.get("user")
    
    welcome = f"Olá {user.identifier}! Sou o Assistente de Triagem V2. Como posso ajudar?"
    await cl.Message(content=welcome).send()

@cl.on_message
async def main(message: cl.Message):
    # Retrieve history
    history = cl.user_session.get("history", [])
    
    # Setup User Context
    user_input = message.content
    user_id = cl.user_session.get("user").metadata.get("glpi_user_id") if cl.user_session.get("user") else None
    
    # Loading Indicator
    msg = cl.Message(content="")
    
    try:
        # Retrieve previous state from session
        prev_state = cl.user_session.get("graph_state", {})
        
        # Build inputs
        inputs = {
            "messages": history + [HumanMessage(content=user_input)],
            "requester_id": user_id,
            "data": prev_state.get("data", {}),
            "intent": prev_state.get("intent"),
            "ticket_payload": prev_state.get("ticket_payload"),
            "viability_score": prev_state.get("viability_score", 0.0),
            "classification_result": prev_state.get("classification_result", {})
        }
    
        # Execute Graph with Visual Feedback
        final_state = {}
        async with cl.Step("Processando Solicitação (Agente B)") as step:
            step.input = user_input
            
            # Using ainvoke (Stable) instead of astream (Unstable)
            final_state = await app.ainvoke(inputs)
            
            # Extract basic feedback for the Step
            intent = final_state.get("intent") or "Desconhecido"
            tid = final_state.get("ticket_id")
            step.output = f"Intenção: {intent} | Ticket Criado: {tid if tid else 'N/A'}"

        # Save the new state for next turn
        cl.user_session.set("graph_state", {
            "data": final_state.get("data"),
            "intent": final_state.get("intent"),
            "ticket_payload": final_state.get("ticket_payload"),
            "requester_id": final_state.get("requester_id"),
            "viability_score": final_state.get("viability_score"),
            "classification_result": final_state.get("classification_result")
        })

        # Extract response
        messages = final_state.get("messages", [])
        response_text = "Desculpe, não consegui processar sua solicitação." 
        if messages:
             last_msg = messages[-1]
             if isinstance(last_msg, AIMessage):
                 response_text = last_msg.content
             else:
                 response_text = str(last_msg.content)
        
        # Update History
        cl.user_session.set("history", messages)
        
        # Send response
        msg.content = response_text
        await msg.send()
        
    except Exception as e:
        await cl.Message(content=f"❌ Erro sistêmico: {e}").send()
        import traceback
        traceback.print_exc()
