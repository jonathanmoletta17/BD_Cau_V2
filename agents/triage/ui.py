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

# Conditional Auth Definition: Only define auth_callback if MOCK_AUTH is FALSE.
# If MOCK_AUTH is TRUE, Chainlit skips the login screen (Seamless Access).
if os.getenv("MOCK_AUTH_ENABLED", "false").lower() != "true":
    @cl.password_auth_callback
    async def auth_callback(username: str, password: str):
        # Hybrid Auth: Check credentials on PROD, operations on TEST
        client = container.glpi_client
        target_env = os.getenv("OPENER_TARGET_ENV", "test").lower()
        
        # 1. Validate on Prod
        # If Target is Prod, we want to KEEP the session to perform actions as the user
        keep = (target_env == "prod")
        
        print(f"[AUTH] Validating {username} on PROD (Target: {target_env}, Keep Session: {keep})...")
        res = await client.login_on_prod(username, password, keep_session=keep)
        
        if not res.get("ok"):
            print(f"[AUTH] Login Failed: {res.get('class')} - {res.get('detail')}")
            return None
        
        user_data = res.get("user_data", {})
        session = user_data.get("session", {})
        session_token = user_data.get("session_token")
        display = session.get("glpifriendlyname") or username
        
        # Extract Entity ID from Prod Session
        # keys are usually glpiactive_entity or glpidefault_entity
        user_entity_id = session.get("glpiactive_entity")
        if not user_entity_id:
            user_entity_id = session.get("glpidefault_entity")
            
        print(f"[AUTH] Detected User Entity: {user_entity_id}")

        # 3. Resolve User ID for Ticket Attribution
        # logic depends on Target Env:
        # - PROD: Auth ID is usually the same as Target ID. We can use session['glpiID'].
        # - TEST: Prod Auth ID != Test DB ID. We must search.
        user_id = None
        
        if target_env == "prod":
            user_id = session.get("glpiID")
            print(f"[AUTH] PROD: Using Session User ID {user_id}")
        else:
            # Hybrid/Test Mode
            print(f"[AUTH] Searching User ID for {username} on TARGET ({target_env})...")
            if await client.init_session():
                 user_id = await client.search_user_id(username)

        if user_id:
            print(f"[AUTH] Resolved User ID: {user_id}")
            
            # --- ORIGIN DETERMINATION LOGIC ---
            # Use PROD data for reliability, as validated in diagnostics.
            # We use the authenticated user's session from login_on_prod
            
            prod_user_id = session.get("glpiID")
            # session_token variable holds the prod session from login_on_prod response
            
            print(f"[AUTH] checking Origin on PROD for User ID {prod_user_id}...")
            
            # 1. Fetch Groups (Prod)
            user_groups = await client.get_user_groups(
                prod_user_id, 
                session_token=session_token,
                base_url=client.prod_url,
                app_token=client.prod_app_token
            )
            print(f"[AUTH] User Groups (Prod): {user_groups}")
            
            # 2. Fetch Profiles for Chefia Check (Check for Profile ID 7)
            user_profiles = await client.get_user_profiles(
                prod_user_id,
                session_token=session_token,
                base_url=client.prod_url,
                app_token=client.prod_app_token
            )
            print(f"[AUTH] User Profiles (Prod): {user_profiles}")
            
            origin_type = "Outro" # Default
            
            # RH Logic
            rh_keywords = ["rh", "recursos humanos", "dgp"]
            is_rh = any(any(k in g.lower() for k in rh_keywords) for g in user_groups)
            
            # Chefia Logic: Check if Profile ID 7 is present
            is_chefia = (7 in user_profiles)
            
            if is_rh:
                origin_type = "RH"
            elif is_chefia:
                origin_type = "Chefia"
                
            print(f"[AUTH] Determined Origin: {origin_type} (Is RH: {is_rh}, Is Chefia: {is_chefia})")
            


        else:
            print(f"[AUTH] BLOCKING: User {username} verified but ID could not be resolved in Target ENV.")
            return None

        # Store user_id and entity_id in session metadata
        meta = {
            "glpi_user_id": user_id,
            "origin_type": origin_type
        }
        if user_entity_id:
            meta["glpi_entity_id"] = user_entity_id
        
        # Store session token if we kept it
        if keep and session_token:
            meta["glpi_session_token"] = session_token

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
    # Helper for Mock Mode Seamless Auth
    # When MOCK is true, auth_callback is skipped, so we must manually set the user in the session
    if os.getenv("MOCK_AUTH_ENABLED", "false").lower() == "true":
         user = cl.User(identifier="Mock User", metadata={"glpi_user_id": 999, "role": "mock"})
         cl.user_session.set("user", user)
         print(f"[UI] Mock Mode Enabled: Auto-logged in as {user.identifier}")

    # Initialize history
    cl.user_session.set("history", [])
    
    await cl.Message(content="Olá! Sou o Assistente de Triagem. Qual o seu problema hoje?").send()

@cl.on_message
async def main(message: cl.Message):
    history = cl.user_session.get("history")
    
    # Add User Message
    if message.elements:
        # User uploaded files
        for element in message.elements:
            # Store in session for later upload
            current_files = cl.user_session.get("pending_attachments", [])
            current_files.append({
                "path": element.path,
                "name": element.name,
                "mime": element.mime or "application/octet-stream"
            })
            cl.user_session.set("pending_attachments", current_files)
            
            # Notify User
            await cl.Message(content=f"📎 **{element.name}** recebido e anexado à sessão.").send()
            
            # Add to history as text context (optional, but good for LLM to know)
            user_msg = ChatMessage(role="user", content=f"[Anexo enviado: {element.name}] {message.content}")
    else:
        user_msg = ChatMessage(role="user", content=message.content)
        
    history.append(user_msg)
    
    # Show loading
    msg = cl.Message(content="")
    await msg.send()
    
    # Process
    try:
        session_id = cl.user_session.get("id")
        response_dict = await container.chat_service.handle_message(history, session_id)
        
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
        sess_token = user.metadata.get("glpi_session_token") if user else None
        
        # LOGIC: 
        # - PROD: We MUST send the Entity ID to correct assign the ticket.
        # - TEST: We usually SKIP Entity ID because Test Env IDs differ from Prod Auth IDs.
        
        target_env = os.getenv("OPENER_TARGET_ENV", "test").lower()
        
        full_desc = last_desc
        
        # Append "Origem Solicitação" if detected
        origin = user.metadata.get("origin_type")
        if origin and origin != "Outro":
            full_desc += f"\n\n**Origem Solicitação:** {origin}"
        
        create_kwargs = {
            "title": t_title,
            "description": full_desc,
            "category_id": cat_id,
            "ticket_type": t_type,
            "urgency": t_urgency,
            "impact": t_impact,
            "requester_id": req_id,
            "ai_analysis": details.get("reasoning", "Classificado automaticamente.")
        }

        if target_env == "prod":
            if ent_id:
                print(f"[UI] PROD DETECTED: Enforcing Entity ID {ent_id}")
                create_kwargs["entities_id"] = ent_id
            if sess_token:
                print(f"[UI] USER SESSION DETECTED: Opening ticket AS USER")
                create_kwargs["session_token"] = sess_token
        else:
             print(f"[UI] TEST/DEV ENV: Skipping Entity ID (Auto-assign)")

        res = await container.glpi_client.create_ticket(**create_kwargs)
        
        ticket_id = res.get("id")
        ticket_id = res.get("id")
        
        # --- ATTACHMENT UPLOAD ---
        pending_files = cl.user_session.get("pending_attachments", [])
        uploaded_count = 0
        
        if pending_files and ticket_id:
            await cl.Message(content=f"📎 Enviando {len(pending_files)} anexos...").send()
            for pf in pending_files:
                try:
                    await container.glpi_client.upload_document(
                        ticket_id=ticket_id,
                        file_path=pf["path"],
                        filename=pf["name"],
                        mime_type=pf["mime"]
                    )
                    uploaded_count += 1
                except Exception as e:
                    print(f"[UI] Error uploading {pf['name']}: {e}")
                    await cl.Message(content=f"⚠️ Falha ao enviar anexo {pf['name']}.").send()
            
            # Clear session
            cl.user_session.set("pending_attachments", [])

        success_msg = f"✅ Chamado aberto com sucesso! **ID: {ticket_id}**"
        if uploaded_count > 0:
            success_msg += f"\n📎 {uploaded_count} anexo(s) enviado(s)."
            
        await cl.Message(content=success_msg).send()
        
    except Exception as e:
        await cl.Message(content=f"❌ Erro ao criar ticket: {e}").send()
