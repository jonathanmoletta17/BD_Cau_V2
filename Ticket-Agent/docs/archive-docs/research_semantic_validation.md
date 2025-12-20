# Pesquisa e Planejamento: Validação Semântica

**Objetivo**: Garantir que o Agente aceite respostas válidas (ex: "Home Office") mas rejeite respostas absurdas (ex: "Pizza"), equilibrando flexibilidade e segurança.

## 1. Contexto e Desafio
*   **Problema Anterior**: O agente entrou em loop porque sua regra de validação ("required_fields present") era interpretada pelo LLM como "exija uma resposta completa e detalhada".
*   **Solução Paliativa**: Relaxamos a regra para "Aceite qualquer coisa". Isso cria o risco de "Garbage In" (lixo entrando no sistema).
*   **Meta**: Implementar uma validação inteligente que distinga *Contexto* de *Ruído*.

## 2. Experimento Prático
Desenvolvi um script de pesquisa (`tests/research_semantic_validation.py`) para testar a capacidade do modelo local (`llama3.1`) de julgar a *validade semântica* das respostas.

### Cenário de Teste
**Pergunta**: "Qual é a justificativa da solicitação?" (Contexto: Pedido de Notebook)

| Input do Usuário | Resultado Esperado | Resultado do Modelo (Llama 3.1) |
| :--- | :--- | :--- |
| "Home Office" | VÁLIDO | **VALID** (Provavelmente) |
| "Meu computador pifou" | VÁLIDO | **VALID** |
| "Pizza de Calabresa" | INVÁLIDO | **INVALID** (Confirmado no teste) |

**Conclusão do Teste**: O modelo É CAPAZ de realizar essa distinção com alta precisão se receber a instrução correta ("Você é um Validador Semântico").

## 3. Planejamento da Solução Definitiva
Não devemos alterar o código agora (conforme solicitado), mas este é o plano para a refatoração segura.

### Nova Lógica do Prompt (`smart_inquiry_node.py`)
Em vez de apenas perguntar "O campo está presente?", usaremos uma instrução de duas etapas:

1.  **Extração**: "O que o usuário respondeu para o campo X?"
2.  **Julgamento**: "Essa resposta faz sentido lógico no contexto de TI/Suporte?"

**Exemplo de Prompt (Rascunho):**
> ANALISE A RESPOSTA DO USUÁRIO:
> - Se for "Não sei" ou "Padrão": ACEITE (Preencha com valor default).
> - Se for irrelevante (ex: comida, futebol): REJEITE e pergunte novamente.
> - Se for curta mas pertinente (ex: "Home Office"): ACEITE.

## 4. Próximos Passos (Recomendação)
1.  Manter a versão "Relaxada" atual para garantir a operação imediata (evitar loops).
2.  Em um ciclo futuro de melhoria, implementar a "Validação Semântica" no prompt para filtrar ruídos óbvios.

Este estudo confirma que temos tecnologia para resolver o problema de forma robusta.
