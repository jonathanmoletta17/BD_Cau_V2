# Governance: Create User (Novo Usuário)

## Context
This document governs the creation of new user accounts in the system.

## Required Information (MUST ASK)
To create a ticket, you MUST extract the following fields. If missing, ask the user.

1. **nome_completo**: Full Name.
2. **departamento**: Department (e.g., RH, Financeiro, TI).
3. **tipo_usuario**: "Efetivo" or "Estagiário".
4. **cpf**: CPF (Brazilian ID).
5. **ramal**: Phone extension (Required).

### Logic Gates
- If `tipo_usuario` is "Efetivo":
    - **matricula**: Required (Employee ID).
- If `tipo_usuario` is "Estagiário":
    - **rg**: Required (ID Card).
    - **matricula**: Optional/Ignored.

## Inferred Fields (DO NOT ASK directly, but infer from context)
- **urgency**: 1 (Low) to 5 (High). Default: 3.
- **impact**: 1 (Low) to 5 (High). Default: 3.

## Validation Rules
- **cpf**: Must be valid format (11 digits).
- **ramal**: Must be a number.

## Goal
Return a JSON payload with ALL required fields.
