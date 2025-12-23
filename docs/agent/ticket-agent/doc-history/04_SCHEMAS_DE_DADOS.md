
📁 04_SCHEMAS_DE_DADOS.md
# 04 — Schemas de Dados

Cada intenção tem um schema JSON que define os campos obrigatórios
e opcionais, conforme as regras de triagem.

> O JSON final sempre contém:
> - intent (string)
> - is_complete (bool)
> - ticket_payload (objeto)
> - missing_fields (lista)
> - diagnostics (objeto | null)

---

## Estrutura Comum

```jsonc
{
  "intent": "STRING",          // Nome da intenção detectada
  "is_complete": true|false,   // Indica se os campos obrigatórios estão preenchidos
  "ticket_payload": { ... },   // Campos específicos da intenção
  "missing_fields": [],        // Campos pendentes
  "diagnostics": null          // Informações extras para debug ou logs
}

Exemplos de Campos por Intenção

Veja nos arquivos de exemplos JSON (arquivo 09_JSON_EXEMPLOS.md)
os modelos detalhados com explicações de cada campo.


---
