from langchain_core.messages import SystemMessage, HumanMessage
from agents.local_triage.state import AgentState
from agents.local_triage.services_factory import get_llm_service
from typing import Dict, Any

async def viability_node(state: AgentState) -> Dict[str, Any]:
    """
    Analyzes the regular conversation to determine if there is enough information
    to proceed to classification.
    Equivalent to Agent A's _check_viability, but as a Graph Node.
    """
    llm_service = get_llm_service()
    
    # 1. Get recent history
    messages = state["messages"]
    if not messages:
        return {"step": "wait_input", "viability_score": 0.0}
        
    # OPTIMIZATION: Logic Bypass
    # If we already have a Locked Intent OR High Viability from previous steps,
    # we DO NOT need to ask the LLM again.
    # This prevents redundant calls and saves latency/cost.
    if state.get("intent") or state.get("viability_score", 0.0) >= 0.5:
        print(f"DEBUG: Viability Bypass Active (Intent: {state.get('intent')})")
        return {"viability_score": 1.0, "step": "check_viability_bypassed"}

    # 2. Construct Prompt for Viability Analysis
    # We want to be less strict than Agent A (which failed "Teams Error").
    # If the user mentions a specific software/error, that IS sustainable.
    history_text = "\n".join([f"{m.type}: {m.content}" for m in messages[-5:]])
    
    system_prompt = """You are a Triage Gatekeeper.
    Decide if the user has provided enough info to Start Classification.

    Criteria for YES (Viable):
    - Mentions a specific item/software (mouse, monitor, excel, sap).
    - AND/OR mentions an error or symptoms (broke, frozen, blue screen).
    - OR asks a clear question ("how to install VS Code").
    
    Criteria for NO (Not Viable):
    - Just greetings ("Hi", "Hello").
    - Extremely vague ("I have a problem", "Help me") without context.
    - Pure chit-chat.

    Respond ONLY with JSON: {"viable": true/false, "reason": "brief reason"}"""

    user_prompt = f"""Conversation History:
    {history_text}
    
    Is this viable for classification? (Be permissive: if in doubt, say YES)"""
    
    try:
        response = await llm_service.chat_completion(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            options={"temperature": 0.0, "format": "json"}
        )
        
        # Parse JSON (assuming Ollama returns valid JSON with format='json')
        import json
        try:
            data = json.loads(response)
            is_viable = data.get("viable", False)
            score = 1.0 if is_viable else 0.0
        except:
            # Fallback if raw text
            is_viable = "true" in response.lower()
            score = 1.0 if is_viable else 0.0
            
        return {"viability_score": score, "step": "check_viability"}

    except Exception as e:
        print(f"Viability Check Failed: {e}")
        return {"viability_score": 0.0, "step": "check_viability"}
