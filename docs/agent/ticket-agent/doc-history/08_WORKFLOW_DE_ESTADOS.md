
📁 08_WORKFLOW_DE_ESTADOS.md
# 08 — Workflow Determinístico



Start
↓
Router → Classifica intenção
↓
Extractor → Extrai campos
↓
Validator → Completo?
↙ ↘
Sim Não
↓ Inquiry (Campo X)
JSON Final ↓
Extrator lê resposta
Validator revalida
Repetir até completar ou Handover
