# AI RULESET: CREATE_USER

## INTENT DEFINITION
**Intent:** CREATE_USER
**Description:** Request to create a new digital identity for an employee.

## CLASSIFICATION RULES (USER TYPE)
| Input Keywords | User Type |
| :--- | :--- |
| "estagiário", "bolsista", "estágio" | **Estagiário** |
| "efetivo", "funcionário", "contratado" | **Efetivo** |

## REQUIRED FIELDS (LOGIC GATES)

### IF User Type is "Efetivo":
1.  **user_type** (Value: "Efetivo")
2.  **full_name** (Nome Completo)
3.  **department** (Setor)
4.  **cpf** (Format: `000.000.000-00` or `123.456.789-00`)
5.  **matricula** (Format: `XXXX-X` or similar ID)

### IF User Type is "Estagiário":
1.  **user_type** (Value: "Estagiário")
2.  **full_name** (Nome Completo)
3.  **department** (Setor)
4.  **rg** (Value: Any valid RG number)
    *   **CRITICAL:** DO NOT ASK FOR CPF OR MATRICULA FOR INTERNS.
    *   **CRITICAL:** ONLY RG IS REQUIRED.

## VALIDATION RULES (QUALITY CONTROL)
- **CPF:** Accept standard Brazilian format (`XXX.XXX.XXX-XX`). Do NOT be pedantic about separators if numbers are correct.
- **Matricula:** Must be numeric logic.

## RESPONSE PROTOCOL
- If User Type is "Estagiário" and "rg" is missing -> Ask: "Por favor, forneça o RG do estagiário."
- If User Type is "Efetivo" and "matricula"/ "cpf" is missing -> Ask: "Por favor, informe a matrícula e o CPF do colaborador efetivo."
- If data is complete and valid -> Output JSON.
