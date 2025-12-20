from agents.local_triage.triage_core.state import AgentState

def validator_node(state: AgentState):
    intent = state.get("intent")
    data = state.get("data", {})
    missing = []
    
    if intent == "EQUIPMENT_REQUEST":
        if not data.get("equipment_type"):
            missing.append("equipment_type")
        
        # Rule: If not specified, default to incident? No, we need strict classification.
        # But schema has default? Let's check logic.
        # Logic: If it's a "broken" mouse -> incident. If "new" -> requisition.
        # If user didn't specify, we might have it empty.
        if not data.get("request_type"):
             # Simple heuristic validation/defaulting could happen here or in extractor.
             # Ideally extractor handles mapping.
             missing.append("request_type")
             
        if data.get("request_type") == "requisition" and not data.get("justification"):
            missing.append("justification")

    elif intent == "VPN_ACCESS":
        if not data.get("justification"):
            missing.append("justification")
            
    elif intent == "CREATE_USER":
        if not data.get("full_name"): missing.append("full_name")
        if not data.get("department"): missing.append("department")
        if not data.get("user_type"): missing.append("user_type")
        
        u_type = data.get("user_type")
        if u_type == "efetivo":
            if not data.get("cpf"): missing.append("cpf")
            if not data.get("matricula"): missing.append("matricula")
        elif u_type == "terceiro":
            if not data.get("empresa"): missing.append("empresa")
            
    is_complete = len(missing) == 0
    return {"missing_fields": missing, "is_complete": is_complete}
