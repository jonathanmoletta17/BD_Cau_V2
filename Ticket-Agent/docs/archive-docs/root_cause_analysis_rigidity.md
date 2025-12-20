# Análise de Causa Raiz: A Origem das Travas 🔒

**Objetivo**: Entender por que o Agente oscila entre "Imprevisível" e "Travado", analisando os últimos 5 incidentes.

## Os 5 Últimos Incidentes (O Histórico)

### 1. O Loop do Patrimônio (Mouse/Teclado)
*   **Sintoma**: Usuário pedia mouse, agente bloqueava exigindo Patrimônio.
*   **Causa**: Classificação errada (`HARDWARE_ISSUE` exige patrimônio).
*   **A Trava**: Rigidez na definição de "Campos Obrigatórios". O código obedecia cegamente o JSON.

### 2. A Crise de Identidade (Intent Drift)
*   **Sintoma**: Agente começava falando de Hardware e terminava perguntando de Acesso na mesma frase.
*   **Causa**: Falta de foco. O agente via todas as possibilidades ao mesmo tempo.
*   **A "Correção"**: Implementamos o **Intent Locking** (Trava de Intenção). Isso resolveu a bagunça, mas criou os problemas 3 e 4.

### 3. O Limbo do Notebook (Recusa de Pedido)
*   **Sintoma**: "Quero Notebook" -> Agente rejeita e pede "Periférico".
*   **Causa**: O **Intent Locking** funcionou bem demais. O agente travou em `PERIPHERALS_REQUEST`, e a definição dessa categoria (no JSON) era restrita demais (não incluía notebook).
*   **A Trava**: O agente foi proibido de "sair da caixa" que escolheu.

### 4. O Loop da Justificativa (Home Office)
*   **Sintoma**: Agente rejeitava "Home Office" como resposta válida.
*   **Causa**: Instrução de validação excessivamente zelosa no Prompt do Sistema (`smart_inquiry_node.py`).
*   **A Trava**: O LLM julgou que a resposta era curta demais e bloqueou o avanço.

### 5. O Chamado Prematuro (Oposto da Trava)
*   **Sintoma**: Agente abria chamado sem perguntar nada.
*   **Causa**: Otimização excessiva (`Viability Node`) pulava a etapa de perguntas.
*   **Correção**: Forçamos a passagem pelo nó de perguntas.

---

## O Diagnóstico: Por que isso acontece?

A raiz de todos os problemas é o conflito entre **Estrutura Estática** e **Inteligência Dinâmica**.

1.  **A Armadilha do JSON**:
    Nossa arquitetura depende do arquivo `intents_config.json`.
    *   Vantagem: Controle. Sabemos o que o agente vai perguntar.
    *   Desvantagem: **Cegueira Situacional**. Se o caso do usuário fugir 1 milímetro do que está escrito no JSON (ex: pedir Notebook na categoria errada), o agente trava.

2.  **A Trava de Segurança (Locking)**:
    Para evitar alucinações, mandamos o agente "olhar só para uma intenção".
    *   Isso transformou o agente em um **Robô de Formulário**. Ele deixa de raciocinar sobre o todo e foca obsessivamente em preencher os campos daquela caixa específica.

3.  **O Perfeccionismo do LLM**:
    Sem instruções explícitas de "seja flexível", o LLM tende a ser pedante. Ele quer a resposta perfeita. Como ele não tem bom senso humano ("Home Office é válido"), ele cai no loop.

## Conclusão
As "travas" que você sente são, ironicamente, os **mecanismos de controle** que criamos para ele não alucinar.
Construímos um sistema muito "Rígido" para tentar torná-lo preciso.

**O Caminho para a Cura Total**:
Precisamos "afrouxar" as rédeas sem perder o controle.
*   **JSON**: Deve ser guia, não lei absoluta.
*   **Prompt**: Deve instruir a "Usar bom senso" acima da "Regra de Preenchimento".
*   **Validadores**: Devem ser semânticos (entender o significado), não sintáticos (checar se tem texto).
