# Governance: Reset Password (Reset de Senha)

## Context
This document governs password reset requests for systems like Windows, Email, ERP, etc.

## Required Information (MUST ASK)
To create a ticket, you MUST extract the following fields. If missing, ask the user.

1. **username**: The username or login to reset.
2. **target_system**: The system where the password needs reset.
3. **ramal**: Phone extension (Required).

## Inferred Fields (DO NOT ASK directly, but infer from context)
- **urgency**: 1 (Low) to 5 (High). Default: 3. (Locked out user is usually High).
- **impact**: 1 (Low) to 5 (High). Default: 3.

## Validation Rules
- **ramal**: Must be a number.

## Goal
Return a JSON payload with ALL required fields.
