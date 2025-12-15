import chainlit as cl
import os
import secrets
import sys
from pathlib import Path

# Adiciona o diretório atual ao PYTHONPATH para importar src
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from main import container
from src.models import ChatMessage

# Configuration
if not os.getenv("CHAINLIT_AUTH_SECRET"):
    os.environ["CHAINLIT_AUTH_SECRET"] = secrets.token_urlsafe(32)

@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    # Hybrid Auth: Check credentials on PROD, operations on TEST
    client = container.glpi_client
    
    # 1. Validate on Prod
    print(f"[AUTH] Validating {username} on PROD...")
    res = await client.login_on_prod(username, password)
    
    if not res.get("ok"):
        print(f"[AUTH] Login Failed: {res.get('class')} - {res.get('detail')}")
        return None
    
    user_data = res.get("user_data", {})
    session = user_data.get("session", {})
    display = session.get("glpifriendlyname") or username
    
    # Extract Entity ID from Prod Session
    # keys are usually glpiactive_entity or glpidefault_entity
    user_entity_id = session.get("glpiactive_entity")
    if not user_entity_id:
        user_entity_id = session.get("glpidefault_entity")
        
    print(f"[AUTH] Detected User Entity: {user_entity_id}")

    # 2. Init Session on Target (Test) - Service Account Session
    # Using the shared service session for user lookup and ticket opening
    print(f"[AUTH] Ensuring Service Session on TARGET...")
    if not await client.init_session():
        print("[AUTH] Failed to initialize Service Session on Target.")
        return None 
        
    # 3. Search User on Target to get their ID for ticket attribution
    print(f"[AUTH] Searching User ID for {username} on TARGET...")
    user_id = await client.search_user_id(username)
    
    if user_id:
        print(f"[AUTH] Found User ID {user_id} for {username}.")
    else:
        print(f"[AUTH] BLOCKING: User {username} verified in Prod but NOT found in Target ENV.")
        return None

    # Store user_id and entity_id in session metadata
    meta = {"glpi_user_id": user_id}
    if user_entity_id:
        meta["glpi_entity_id"] = user_entity_id

    return cl.User(identifier=display, metadata=meta)

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Triagem Inteligente",
            markdown_description="Descreva seu problema para abertura automática de chamado.",
            icon="🛠️",
        )
    ]

@cl.on_chat_start
async def start():
    # Initialize history
    cl.user_session.set("history", [])
    
    await cl.Message(content="Olá! Sou o Assistente de Triagem. Qual o seu problema hoje?").send()

@cl.on_message
async def main(message: cl.Message):
    history = cl.user_session.get("history")
    
    # Add User Message
    user_msg = ChatMessage(role="user", content=message.content)
    history.append(user_msg)
    
    # Show loading
    msg = cl.Message(content="")
    await msg.send()
    
    # Process
    try:
        response_dict = await container.chat_service.handle_message(history)
        
        # Add AI Message to history
        ai_content = response_dict.get("content", "")
        history.append(ChatMessage(role="assistant", content=ai_content))
        cl.user_session.set("history", history)
        
        msg.content = ai_content
        
        # If action detected (e.g. classified), allow confirmation
        if response_dict.get("action") == "classified":
            details = response_dict.get("details", {})
            
            # Store proposed ticket in session
            cl.user_session.set("proposed_ticket", details)
            
            # Use reasoning or content as summary for user
            actions = [
                cl.Action(name="confirm_ticket", value="confirm", label="✅ Criar Ticket", payload={})
            ]
            msg.actions = actions
            
        await msg.update()
        
    except Exception as e:
        msg.content = f"Erro ao processar: {e}"
        await msg.update()

@cl.action_callback("confirm_ticket")
async def on_action(action: cl.Action):
    details = cl.user_session.get("proposed_ticket")
    user = cl.user_session.get("user") # Chainlit stores current user here
    
    if not details:
        await cl.Message(content="❌ Erro: Detalhes do ticket perdidos.").send()
        return

    req_id = user.metadata.get("glpi_user_id") if user else None

    await cl.Message(content="⏳ Abrindo chamado no GLPI...").send()
    
    try:
        # Simplificacao: Usando mensagem do usuario como descrição
        history = cl.user_session.get("history")
        # Find last user message
        last_desc = "Chamado via IA"
        for m in reversed(history):
            if m.role == "user":
                last_desc = m.content
                break
        
        cat_id = details.get("selected_category_id")
        
        # Extract Metadata from AI Analysis
        t_type = details.get("ticket_type", 1) # Default to Incident
        t_urgency = details.get("urgency", 3)
        t_impact = details.get("impact", 3)
        t_title = details.get("suggested_title") or last_desc[:50]
        
        print(f"[UI] Creating Ticket: Title='{t_title}', Type={t_type}, Urgency={t_urgency}, Impact={t_impact}")

        # Pass requester_id explicitamente para evitar condições de corrida
        req_id = user.metadata.get("glpi_user_id") if user else None
        ent_id = user.metadata.get("glpi_entity_id") if user else None
        
        if ent_id:
             print(f"[UI] Assigning Ticket to Entity ID: {ent_id}")

        res = await container.glpi_client.create_ticket(
            title=t_title,
            description=last_desc,
            category_id=cat_id,
            ticket_type=t_type,
            urgency=t_urgency,
            impact=t_impact,
            requester_id=req_id,
            entities_id=ent_id,
            ai_analysis=details.get("reasoning", "Classificado automaticamente.")
        )
        
        ticket_id = res.get("id")
        await cl.Message(content=f"✅ Chamado aberto com sucesso! **ID: {ticket_id}**").send()
        
    except Exception as e:
        await cl.Message(content=f"❌ Erro ao criar ticket: {e}").send()
