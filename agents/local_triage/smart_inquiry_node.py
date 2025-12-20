import json
from pathlib import Path
from typing import Dict, Any
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from agents.local_triage.state import AgentState
from agents.local_triage.services_factory import get_llm_service

def load_intents_config():
    """Loads the specific field definitions from JSON."""
    try:
        current_dir = Path(__file__).parent
        with open(current_dir / "intents_config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load intents_config.json: {e}")
        return {"intents": []}

async def smart_inquiry_node(state: AgentState) -> Dict[str, Any]:
    """
    Intelligent Node (Hybrid Brain).
    Uses the Shared LLM Service + Structured Intents config to ask
    precise follow-up questions (Slot Filling) or generic context questions.
    """
    llm_service = get_llm_service()
    
    # 1. Get History
    messages = state.get("messages", [])
    if not messages:
        return {"step": "wait_input", "ready_to_classify": False}

    # 1b. SYSTEM INFO PARSER (Scenario B: Auto-Parse pasted JSON)
    try:
        last_msg = messages[-1].content
        if "{" in last_msg and "}" in last_msg and ("system" in last_msg or "hardware" in last_msg):
            # Attempt to find JSON block
            import re
            json_match = re.search(r'\{.*\}', last_msg, re.DOTALL)
            if json_match:
                potential_json = json_match.group(0)
                sys_info = json.loads(potential_json)
                
                # Check signature keys
                if "system" in sys_info and "hardware" in sys_info:
                    print("DEBUG: System Info JSON Detected!")
                    extracted_data = {}
                    
                    # Extract fields
                    if "system" in sys_info:
                        extracted_data["hostname"] = sys_info["system"].get("hostname")
                        extracted_data["os"] = sys_info["system"].get("os")
                        
                    if "hardware" in sys_info:
                        extracted_data["serial_number"] = sys_info["hardware"].get("serial_number")
                        
                    if "network" in sys_info:
                        extracted_data["ip"] = sys_info["network"].get("ip")
                        
                    if "monitors" in sys_info and isinstance(sys_info["monitors"], list):
                         monit_str = ", ".join([f"{m.get('Model')} (SN:{m.get('SerialNumber')})" for m in sys_info["monitors"]])
                         extracted_data["monitors"] = monit_str
                         
                    # Merge with existing data
                    current_data = state.get("data", {})
                    current_data.update(extracted_data)
                    
                    return {
                        "data": current_data,
                        "messages": [AIMessage(content="Obrigado! Recebi as informações do sistema (Serial, IP e Hostname). Vou usá-las para agilizar o atendimento.")],
                        "ready_to_classify": False, # Continue flow (might need more info or be ready)
                        "step": "wait_input" # Loop back to check completeness
                    }
    except Exception as e:
        print(f"JSON Parse Warning: {e}")

    # 2. Load Intents Logic (INTENT LOCKING APPLIED)
    config = load_intents_config()
    all_intents = config.get("intents", [])
    
    # Check if we already have a LOCKED intent
    current_intent_name = state.get("intent")
    
    active_intents = []
    if current_intent_name and current_intent_name != "Unknown":
        # FILTER: Only show the Locked Intent to the LLM
        # This prevents "Intent Drift" (Hallucination of other requirements)
        active_intents = [i for i in all_intents if i["name"] == current_intent_name]
        if not active_intents:
            # Fallback if valid intent name but not found in config (rare)
            active_intents = all_intents
            current_intent_name = None 
    else:
        active_intents = all_intents

    intents_context = json.dumps(active_intents, indent=2, ensure_ascii=False)

    # 3. Construct Prompt (Hybrid: Structured + Conversational)
    history_text = "\n".join([f"{m.type.upper()}: {m.content}" for m in messages[-10:]])
    
    system_prompt = (
        "Você é um Assistente de Suporte TI Sênior e Gatekeeper.\n"
        "Seu objetivo é classificar a solicitação e garantir que temos os dados necessários.\n\n"
        f"INTENÇÃO ATUAL: {current_intent_name if current_intent_name else 'Ainda não identificada (Analise)'}\n"
        "CONFIGURAÇÃO DE INTENÇÕES DISPONÍVEIS:\n"
        f"{intents_context}\n\n"
        "REGRAS DE OPERAÇÃO:\n"
        "1. Analise o histórico e tente identificar a INTENÇÃO do usuário.\n"
        "2. Se identificar uma intenção, VERIFIQUE se os 'required_fields' estão presentes no histórico.\n"
        "3. Se TODOS os campos obrigatórios estiverem presentes. IMPORTANTE: Se o usuário deu QUALQUER resposta para a pergunta (mesmo curta), considere o campo PREECHIDO. Não seja perfeccionista.\n"
        "4. Se faltar algum campo obrigatório, FAÇA UMA PERGUNTA ESPECÍFICA para obter esse dado.\n"
        "5. EVITE LOOPS: Se o usuário já respondeu a pergunta no histórico, NÃO PERGUNTE DE NOVO. Aceite a resposta e digite 'READY'.\n"
        "6. Em caso de dúvida, se já tiver respostas suficientes, Responda: 'READY'.\n"
        "7. IMPORTANTE: Separe sua validação da resposta final.\n"
        "   No início, escreva 'INTENT: [NOME_DA_INTENCAO]' (Se identificada).\n"
        "   Escreva seu raciocínio, e depois coloque a tag '### RESPONSE'.\n"
        "   Tudo após a tag será enviado ao usuário.\n"
        "   Exemplo:\n"
        "   INTENT: PERIPHERALS_REQUEST\n"
        "   O usuário quer mouse. Falta modelo.\n"
        "   ### RESPONSE\n"
        "   Qual modelo de mouse você precisa?\n"
    )
    
    user_prompt = f"""Histórico da Conversa:
    {history_text}
    
    Analise. Responda 'READY' (se pronto) OU use o formato 'INTENT: ... \n ... ### RESPONSE [Sua Pergunta]'."""
    
    try:
        # 4. Call LLM
        # We increase max_tokens slightly to allow for reasoning
        response_text = await llm_service.chat_completion(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            options={"temperature": 0.1, "num_ctx": 2048} 
        )
        
        # 5. Logic Branch & Parser
        final_answer = response_text
        detected_intent = current_intent_name # Default to keeping what we have
        
        # PARSER LOGIC: Extract content after ### RESPONSE
        if "### RESPONSE" in response_text:
            parts = response_text.split("### RESPONSE")
            # The part BEFORE response usually contains INTENT:
            analysis_part = parts[0]
            if len(parts) > 1:
               final_answer = parts[-1].strip()
            
            # Extract INTENT: from analysis
            for line in analysis_part.split('\n'):
                if "INTENT:" in line:
                    val = line.split("INTENT:")[1].strip()
                    if val and val != "None" and val != "Unknown":
                        detected_intent = val
        
        # Check for READY signal
        if "READY" in final_answer.upper() or "READY" in response_text.upper().split("### RESPONSE")[-1]:
             return {
                "intent": detected_intent, # Persist Intent
                "ready_to_classify": True,
                "step": "smart_inquiry_complete"
            }
            
        return {
            "intent": detected_intent, # Persist Intent (LOCK IT)
            "messages": [AIMessage(content=final_answer)],
            "ready_to_classify": False,
            "step": "wait_input"
        }
        
    except Exception as e:
        # Fallback in case of LLM failure
        print(f"Smart Inquiry Failed: {e}")
        return {
            "messages": [AIMessage(content="Poderia me dar mais detalhes sobre o pedido?")],
            "ready_to_classify": False,
            "step": "wait_input"
        }
