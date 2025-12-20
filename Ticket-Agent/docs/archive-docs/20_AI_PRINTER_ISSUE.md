# GOVERNANCE: PRINTER_ISSUE (INTENT 20)

## CONTEXT
The user is reporting an issue with a printer or requesting supplies (toner).
The goal is to dispatch a technician to the correct PHYSICAL LOCATION with the correct PARTS.

## REQUIRED FIELDS (LOGIC GATES)

### IF Issue Type is "TONER" (Suprimento/Tinta):
1.  **issue_type** (Value: "Toner")
2.  **location** (Room/Floor/Sector)
    *   *Where is this printer?*
3.  **printer_model** (Model Name/Number) OR **toner_model**
    *   *We need to know which toner to bring.*
4.  **color** (Black/Color/Magenta/Cyan/Yellow)
    *   *Default to "Black" if generic "toner" is asked, but prefer asking if unclear.*

### IF Issue Type is "DEFECT" (Defeito/Quebrada/Erro/Papel):
1.  **issue_type** (Value: "Defect")
2.  **location** (Room/Floor/Sector/Corridor)
    *   **CRITICAL:** We cannot fix a printer if we cannot find it.
    *   *Validation:* Accept any semantic location (e.g., "Corredor", "Sala 10", "RH"). DO NOT ask for more precision if one is given.
3.  **description** (What is wrong?)
    *   *Examples: "Paper jam", "Making noise", "Code 505", "Not printing".*
    *   *Validation:* Any symptom description is valid. DO NOT ask for "more details" if a symptom is provided.

## OPTIONAL BUT HELPFUL
- **serial_number** (Etiqueta de Patrimônio) - Greatly helps identification but valid to proceed without it if location is precise.

## RESPONSE PROTOCOL
- **Missing Location:** Ask: "Qual a localização da impressora? (Sala, Andar ou Setor)"
- **Missing Toner Detail:** Ask: "Qual o modelo da impressora e a cor do toner?"
- **Generic "Printer Broken" (WITHOUT description):** Ask: "Qual o erro ou defeito apresentado?"
- **If user describes a noise/jam/error:** ACCEPT it as the description.

## VALIDATION RULES
- **Location:** Must be a semantic location (e.g., "RH", "1st Floor", "Room 302"). "Aqui" or "Minha sala" is NOT valid if context is missing.
- **Color:** If user says "Acabou a tinta", assume they need toner. Ask color only if model is color-capable (LLM can guess implies color usually 4 options).
