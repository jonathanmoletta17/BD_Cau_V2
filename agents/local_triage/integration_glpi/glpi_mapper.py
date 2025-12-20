"""
GLPI Mapper
Translates Agent Intents and Extracted Data into GLPI Ticket Categories and Fields.
"""

# Map Semantic Intents to GLPI Category IDs based on `categories_list.json`
# We aim for the deepest specific category ID available.

# SYSTEM MAP (For CORPORATE_SYSTEMS intent)
SYSTEM_TO_CATEGORY = {
    "PROA": 5730,  # Sistemas Corporativos > PROA
    "FPE": 5727,   # Sistemas Corporativos > FPE
    "GPE": 5728,   # Sistemas Corporativos > GPE
    "SOE Web": 5731, # Sistemas Corporativos > SOE
    "SOE": 5731,     # Alias
    "IPE": 5729,     # Outros Sistemas
    "RHE": 5729,     # Outros Sistemas
    "LAI": 5729,     # Outros Sistemas (Fallback)
    "GCE": 5729,     # Outros Sistemas (Fallback)
    "GDG": 5729,     # Outros Sistemas (Fallback)
    "SGM": 5729,     # Outros Sistemas (Fallback)
    "SPI": 5729,     # Outros Sistemas (Fallback)
    "Agenda": 5729,  # Outros Sistemas (Fallback)
    "Túnel PROCERGS": 5729, # Outros Sistemas (Fallback)
    "Geral": 5729    # Outros Sistemas (Fallback)
}

# INTENT MAP (General fallback or specific logic)
INTENT_TO_CATEGORY = {
    "CREATE_USER": 5740,        # Acesso > Conta de Rede > Criação de Novo Usuário
    "ACCESS_PROBLEM": 5743,     # Acesso > Conta de Rede > Reset de Senha (Default safe choice)
    "HARDWARE_PROBLEM": 5749,   # Hardware > Desktops > Falha de Hardware (Default)
    "REQUEST_PERIPHERALS": 5765,# Hardware > Periféricos > Solicitação
    "REQUEST_EQUIPMENT": 5751,  # Hardware > Desktops > Solicitação de Novo Equipamento
    "SOFTWARE_SUPPORT": 5736,   # Software > Softwares de Terceiros (Generic)
    "NETWORK_PROBLEM": 5773,    # Rede > Internet > Lentidão ou Falha
    "TELEPHONY": 5767           # Telefonia > Falha de Chamada
}

def map_category(intent: str, data: dict) -> int:
    """
    Determines the GLPI Category ID based on the Intent and Data fields.
    """
    # 1. Corporate Systems Specific Logic
    if intent == "CORPORATE_SYSTEMS":
        system_name = data.get("sistema", "")
        # Try exact match or partial match
        for key, cat_id in SYSTEM_TO_CATEGORY.items():
            if key.lower() == system_name.lower():
                return cat_id
            if key in system_name: # Handle 'SOE Web' vs 'SOE'
                return cat_id
        return 5729 # Default to 'Outros Sistemas'

    # 2. Hardware Refinement (Example)
    if intent == "HARDWARE_PROBLEM":
        equip = data.get("equipamento", "").lower()
        if "impressora" in equip or "toner" in equip:
            return 5755 # Impressoras > Falha
        if "notebook" in equip or "laptop" in equip:
            return 5762 # Notebook > Falha
    
    # 3. Access Refinement
    if intent == "ACCESS_PROBLEM":
        action = data.get("acao", "").lower()
        if "pasta" in action or "rede" in action:
            return 5744 # Pastas de Rede

    # Default Intent Mapping
    return INTENT_TO_CATEGORY.get(intent, 0) # 0 means Uncategorized/Root

def format_ticket_title(intent: str, data: dict) -> str:
    """Generates a standardized title."""
    if intent == "CORPORATE_SYSTEMS":
        sys = data.get("sistema", "Sistema")
        type_req = data.get("tipo_solicitacao", "Suporte")
        return f"[{sys}] {type_req} - {data.get('nome_usuario', 'Usuario')}"
    
    if intent == "CREATE_USER":
        return f"[Criação de Usuário] {data.get('nome_completo', '')}"

    subject = data.get("equipamento") or data.get("sistema") or data.get("software") or "Solicitação"
    return f"[{intent}] {subject}"

def format_ticket_description(intent: str, data: dict, original_input: str) -> str:
    """Generates a markdown description body."""
    lines = [f"**Descrição Original:**\n{original_input}\n"]
    lines.append("**Dados Extraídos:**")
    for k, v in data.items():
        if v:
            lines.append(f"- **{k}:** {v}")
            
    lines.append("\n*Classificado Automaticamente pelo Agente de Triagem V2*")
    return "\n".join(lines)
