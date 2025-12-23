📁 07_POLITICA_DE_CONFIRMACAO_E_ERRO.md
# 07 — Política de Confirmação e Erro

## Limite de Tentativas
- O agente pergunta até 3 vezes sobre o mesmo campo.
- Após 3 tentativas sem progresso → **Handover N2**
- Divergência implícita de informação exige confirmação explícita.

## Loops
- O agente **não deve** repetir uma pergunta sem primeiro ler a resposta.
- Histórico de mensagens deve ser considerado.
