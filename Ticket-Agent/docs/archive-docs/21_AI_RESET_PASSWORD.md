# GOVERNANCE: RESET_PASSWORD (INTENT 70)

## CONTEXT
The user needs to reset a password or unlock an account.
Most users refer to "network password", "computer password", or "login" as the same thing (Active Directory).

## SYSTEM IDENTIFICATION RULES (INFERENCE)
1.  **DEFAULT:** If the user says "senha", "login", "não consigo entrar", "computador bloqueado" -> **System is "Rede/Windows"**.
    *   *Do NOT ask "Which system?" unless it is ambiguous.*
    *   *Examples:* "Esqueci minha senha" -> Rede/Windows. "Bloqueou tudo" -> Rede/Windows.
2.  **EXCEPTIONS:**
    *   "Email", "Outlook", "Office", "Teams" -> **System is "Office 365"**.
    *   "SAP", "ERP" -> **System is "SAP"**.
    *   "GLPI", "Chamado" -> **System is "GLPI"**.
    *   "SEI", "PROA" -> **System is "Sistemas Corporativos"**.

## REQUIRED FIELDS (LOGIC GATES)

### ALL Systems:
1.  **target_system** (Inferred per rules above)
2.  **username** (Login/Matricula/Email)
    *   *We need to know WHO needs the reset.*
    *   *Extraction:* Capture any identifier provided (e.g., "j.silva", "1234", "bob@email.com").

## SECURITY PROTOCOLS (CRITICAL)
- **NEGATIVE CONSTRAINT:** NEVER ask for the *current* or *old* password.
- **NEGATIVE CONSTRAINT:** NEVER ask for the *new* password.
- **SECURITY CHECK:** If the user provides a password in the chat, **IGNORE IT** and proceed with the ticket. Do NOT include it in the JSON.
- **MANAGER APPROVAL:** Not required for Triage. (Support team will handle verification).

## RESPONSE PROTOCOL
- **If username missing:** Ask: "Qual o seu login de rede ou matrícula?"
- **If vague assumption (Windows):** Confirm: "Certo, vou abrir um chamado para resetar sua senha de Rede." (Implicit confirmation is okay).
- **If username is present:** DO NOT ASK FOR IT AGAIN.

## VALIDATION RULES
- **Username:** `username` (The target login).
- **Format:** typically `first-last` (hyphen separated).
    - *Constraint:* If format differs (e.g. "Space Separation"), verify if it's the `first-last` pattern.
- **Username:** Can be a name (j.silva), number (1234-5), or email. Accept any identifier.
- **Pass 1:** If user says "My login is X", extract "X" as username.
