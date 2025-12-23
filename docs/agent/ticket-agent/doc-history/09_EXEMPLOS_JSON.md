📁 
# 09 — Exemplos JSON (com comentários)

## RESET_PASSWORD

```jsonc
{
  "intent": "RESET_PASSWORD",  // intenção detectada
  "is_complete": true,         // todos campos obrigatórios preenchidos
  "ticket_payload": {
    "usuario_rede": "joao.santos", // login de rede
    "sistema_afetado": "Rede/Windows" // sistema afetado
  },
  "missing_fields": [],      // nenhum campo pendente
  "diagnostics": null
}

CREATE_USER (efetivo)
{
  "intent": "CREATE_USER",
  "is_complete": true,
  "ticket_payload": {
    "nome_completo": "Maria Oliveira",
    "setor": "Contabilidade",
    "tipo_usuario": "EFETIVO",
    "cpf": "123.456.789-00",   // obrigatório para efetivo
    "rg": null
  },
  "missing_fields": [],
  "diagnostics": null
}


(continua com equip, printer, vpn, corporate…)


---
