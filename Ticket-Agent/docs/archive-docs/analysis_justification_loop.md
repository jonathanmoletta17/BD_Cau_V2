# Análise de Inconsistência: Loop de Justificativa

**Incidente**: O agente pergunta a justificativa, o usuário responde "Home Office", e o agente pergunta de novo, num loop frustrante.

## 1. O Que o Agente Viu (A Prova)
Capturei o prompt exato que o agente recebeu no momento do erro.
O histórico estava assim:
```text
AI: Qual é o motivo exato da solicitação de um notebook? (Ex: Defeito, Novo Funcionário, Home Office)
HUMAN: Home Office
```

## 2. Por que ele falhou? (Diagnóstico)
O Prompt do Sistema (`smart_inquiry_node.py`) diz:
> "VERIFIQUE se os 'required_fields' estão presentes no histórico."

O LLM, ao ler o histórico acima, provavelmente pensou:
1.  *A pergunta deu exemplos: "Defeito, Novo Funcionário, Home Office".*
2.  *O usuário repetiu a palavra "Home Office".*
3.  **Falha de Raciocínio (Hipótese Principal)**: O modelo interpretou que o usuário estava apenas citando o *tipo* de uso, mas não a *justificativa detalhada* que ele (o modelo) esperava excessivamente ser "exata".
4.  **Falha de Contexto (Hipótese Secundária)**: O usuário já tinha dito "atuar em home office" antes. O agente ignorou. Agora, disse de novo. O agente ignorou de novo.

Isso indica que o **critério de aceitação** do campo `justificativa` está muito "rigoroso" ou "confuso" para o modelo `llama3.1` (ou o que está sendo usado). Ele acha que "Home Office" não é resposta suficiente, ou que é ambíguo.

## 3. Ponto Exato do Código
Arquivo: `agents/local_triage/smart_inquiry_node.py`
Trecho: `system_prompt` (Linhas ~40-60).

O prompt confia na "intuição" do LLM para decidir se o campo está preenchido.
Não há código Python validando "Se len(resposta) > 0, aceite". É pura interpretação de texto. E a interpretação está falhando em ser pragmática.

## 4. O Que Fazer (Planejamento)
Para resolver isso sem reescrever o motor inteiro, precisamos ajustar as instruções para o LLM ser **Menos Chato**.

**Alterações Planejadas (Para depois):**
1.  **Ajuste no Prompt**: Adicionar uma regra explícita: *"Se o usuário deu UMA resposta para a pergunta, considere o campo preenchido. Não exija detalhes excessivos."*
2.  **Refinamento do Config**: Mudar a pergunta do JSON.
    *   De: *"Qual é o motivo...?"*
    *   Para: *"Qual o motivo? (Se for Home Office, pode responder apenas 'Home Office')"*.

Isso deve "destravar" o cérebro do modelo.
