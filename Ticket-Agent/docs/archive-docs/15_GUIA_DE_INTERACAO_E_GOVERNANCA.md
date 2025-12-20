# 15 — Guia de Interação e Governança

## Restrições de Atuação
> **Você NÃO pode implementar, corrigir ou sugerir código.**

Seu papel agora é apenas:
- Levantar decisões pendentes
- Apresentar opções claras
- Explicar consequências
- Aguardar minha decisão explícita.

Sem isso, o agente tende a "resolver tudo de uma vez", o que não é desejado.

---

## 4. Estrutura correta para seguir

Você não precisa mais pedir análises soltas.
Você precisa conduzir **micro-decisões documentadas**.

### 📐 Framework de Decisão (Use Sempre)

Para cada tema, siga exatamente este ciclo:

#### Fase 1 — Delimitação
Você pergunta:
> “Quais decisões de comportamento ainda NÃO estão explicitamente definidas no agente?”

O agente responde apenas listando (sem propor solução).

*Exemplo de saída aceitável:*
- Inferência de urgência
- Inferência de impacto
- Tratamento de múltiplos problemas no mesmo ticket
- Linguagem técnica vs leiga
- Quando encerrar conversa sem ticket

#### Fase 2 — Uma decisão por vez
Você escolhe uma única regra:
> “Vamos decidir agora apenas: Inferência de Urgência.”

O agente responde obrigatoriamente neste formato:
| Opção | Descrição | Benefício | Risco |
| :--- | :--- | :--- | :--- |
| ... | ... | ... | ... |

**Sem recomendação final.**

#### Fase 3 — Decisão humana
Você responde algo como:
> “Adotar opção híbrida, com confirmação no resumo final.”

👉 **Somente aqui a regra nasce.**

#### Fase 4 — Registro
O agente:
1. Atualiza `politicas_operacionais.md`
2. Marca como **Regra Invariante**
3. Define critério de teste
4. Nada mais.

#### Fase 5 — Só depois: implementação
Somente após várias regras fechadas, vocês voltam para:
- schemas
- prompts
- código

**Nunca antes.**

---

## 5. Próximo Pedido Recomendado

> “Liste todas as regras comportamentais e de inferência que ainda NÃO estão explicitamente decididas ou documentadas no agente.
> Não proponha soluções.
> Apenas enumere os pontos de decisão pendentes.”
