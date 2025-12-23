# Análise: Por que o Agente Esquece? 🧠

**Resumo do Problema**: O usuário relatou que o agente "esquece" o contexto dependendo do número de interações.

## 1. Pesquisa Teórica (Internalização)
Antes de olhar o código, estudei como Chatbots LLM gerenciam memória.
*   **O Problema do Contexto**: LLMs têm limite de tokens. Não dá para passar o histórico infinito.
*   **A Falha Comum (Sliding Window)**: Muitos sistemas cortam as mensagens antigas (`últimas N mensagens`) para economizar tokens.
*   **O Efeito Colateral**: Se a mensagem que define o problema (ex: "Meu mouse quebrou") ficar velha demais, ela sai da janela. O agente "esquece" do que se tratava.
*   **A Arquitetura Correta**:
    1.  **Contexto Pinado**: Manter sempre a mensagem #1 (Origem).
    2.  **Memória de Estado**: Extrair fatos para variáveis (ex: `intent=MOUSE`) para não depender de reler o texto original.

## 2. A Inconsistência no Código
Analisei `smart_inquiry_node.py` e encontrei a "arma do crime" na linha 97:

```python
history_text = "\n".join([f"{m.type.upper()}: {m.content}" for m in messages[-10:]])
```

**O Que Isso Significa?**
O sistema está programado para olhar **apenas as últimas 10 mensagens**.
*   Cada interação (Você + Agente) = 2 mensagens.
*   Após **5 rodadas** de conversa, a primeira mensagem (onde você disse o que queria) DESAPARECE da visão do agente.

## 3. Cenário do Erro
1.  Você: "Preciso de um computador." (Msg 1)
2.  Agente: "Qual?" (Msg 2)
3.  Você: "Notebook." (Msg 3)
... (Conversa se alonga solicitando IP, Serial, Justificativa, Erro no Loop) ...
11. Agente vai classificar.
12. O Código pega `messages[-10:]`. A Msg 1 ("Preciso de um computador") foi cortada.
13. O Agente olha o histórico recente, não vê pedido nenhum, e "esquece" ou alucina.

## 4. O Plano de Correção (Futuro)
*Não alterarei o código agora, conforme sua ordem.*
Mas a correção estrutural é simples e definitiva:
**Alterar a construção do prompt para:**
```python
# Pseudo-código da Arquitetura Correta
recent_history = messages[-8:] # Mantém o recente
original_request = messages[0] # PINA o início
final_history = [original_request] + recent_history
```
Isso garante que ele JAMAIS esqueça como tudo começou.
