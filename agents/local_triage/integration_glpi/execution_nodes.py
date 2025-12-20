from typing import Dict, Any, List
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from agents.local_triage.state import AgentState
import json
from agents.local_triage.glpi_mapper import map_category, format_ticket_title, format_ticket_description
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from agents.triage.src.config import settings

# Load Env
load_dotenv()

# Initialize Model (Used by Finalizer)
ollama_base_url = settings.INFERENCE_SERVER_URL
llm_model = settings.LLM_MODEL
llm = ChatOllama(model=llm_model, temperature=0, num_ctx=8192, base_url=ollama_base_url)

# NOTE: We Assume Sys.Path is already set by UI bootstrap or Main.
try:
    from src.services.glpi_client import GLPIClient
except ImportError:
    GLPIClient = None


def finalize_response_node(state: AgentState) -> Dict[str, Any]:
    """Generates the final confirmation."""
    intent = state.get("intent")
    data = state.get("data", {})
    ticket_id = state.get("ticket_id")

    if intent in ["UNKNOWN", "other", "Other"]:
        msg = "Desculpe, não consegui entender sua solicitação. Por favor, tente descrever de outra forma ou contate o suporte via telefone."
    elif intent == "HANDOVER_TO_HUMAN":
        msg = "Entendido. Estou encaminhando sua solicitação para um atendente humano. Aguarde um momento..."
    else:
        status_msg = f" Chamado aberto com sucesso! ID: #{ticket_id}" if ticket_id else " (Simulação: Pronto para abrir chamado)."
        
        system_prompt = f"""Você é um assistente de suporte de TI prestativo.
        Status do Chamado: {status_msg}
        Dados: {data}
        Gere uma resposta final ao usuário confirmando a ação."""

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content="Gere a mensagem de confirmação.")
        ])
        msg = response.content

    return {"messages": [HumanMessage(content=msg)], "step": "done"}


async def create_ticket_node(state: AgentState) -> Dict[str, Any]:
    """
    Final node (Async): Transforms extracted data into a valid GLPI Ticket Payload AND calls API.
    """
    intent = state.get('intent')
    data = state.get("data", {})
    messages = state['messages']
    original_input = messages[0].content if messages else ""

    # Check if Payload was already built by Engine
    existing_payload = state.get("ticket_payload")
    if existing_payload:
        print("DEBUG: Using existing Smart Payload from Engine")
        payload = existing_payload
    else:
        # Legacy Flow (Fallback)
        category_id = map_category(intent, data)
        title = format_ticket_title(intent, data)
        description = format_ticket_description(intent, data, original_input)
        
        payload = {
            "input": {
                "name": title,
                "content": description,
                "itilcategories_id": category_id,
                "urgency": 3,
                "impact": 3
            }
        }
    
    # Inject Requester ID if present
    req_id = state.get('requester_id')
    if req_id:
        payload["input"]["_users_id_requester"] = req_id
    
    ticket_id = None
    # 2. Call GLPI API
    if GLPIClient:
        try:
            # Init Client (Settings loaded from env)
            client = GLPIClient()
            print(f"DEBUG: Opening ticket via Agent A Client...")
            
            # ADAPTER LOGIC: Map payload back to args
            inp = payload.get("input", {})
            
            # Extract basic fields
            name_arg = inp.get("name", "Sem Título")
            content_arg = inp.get("content", "Sem Descrição")
            cat_id = inp.get("itilcategories_id", 0)
            urgency_arg = inp.get("urgency", 3)
            impact_arg = inp.get("impact", 3)
            req_id_arg = inp.get("_users_id_requester")
            
            # Call it
            res = await client.create_ticket(
                title=name_arg,
                description=content_arg,
                category_id=cat_id,
                urgency=urgency_arg,
                impact=impact_arg,
                requester_id=req_id_arg
            )
            ticket_id = res.get("id")
            print(f"DEBUG: TICKET CREATED: #{ticket_id}")

        except Exception as e:
            print(f"ERROR Creating Ticket: {e}")
    else:
        print("DEBUG: GLPIClient Class not loaded.")

    return {"ticket_payload": payload, "ticket_id": ticket_id, "step": "finalize"}
