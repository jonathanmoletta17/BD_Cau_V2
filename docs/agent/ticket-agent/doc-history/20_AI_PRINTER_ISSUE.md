# Governance: Printer Issue (Problema de Impressora)

## Context
This document governs reporting issues with printer hardware or supplies.

## Required Information (MUST ASK)
To create a ticket, you MUST extract the following fields. If missing, ask the user.

1. **issue_type**: "Hardware Failure" (Broken, Jammed) or "Supply" (Toner, Paper).
2. **printer_model**: Model of the printer (or "Unknown").
3. **location**: Where is the printer located? (e.g., "1st Floor", "RH Room").
4. **ramal**: Phone extension (Required).

## Inferred Fields (DO NOT ASK directly, but infer from context)
- **urgency**: 1 (Low) to 5 (High). Default: 3. Consider business impact (e.g., "Can't print checks" = High).
- **impact**: 1 (Low) to 5 (High). Default: 3.

## Validation Rules
- **ramal**: Must be a number.

## Goal
Return a JSON payload with ALL required fields.
