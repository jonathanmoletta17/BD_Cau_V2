# Design de Sistema: Auditoria e Saneamento de Dados Assistida por IA

## 1. O Conceito
**"Não emburreça a IA. Use a IA para educar os dados."**

Atualmente, temos um **Conflito de Verdade**:
*   **Verdade Histórica (Dataset):** Classificações feitas por humanos, muitas vezes apressadas ou genéricas (Ex: Tudo é "Suporte").
*   **Verdade Semântica (Agente):** Classificações baseadas em definições estritas e leitura de texto (Ex: "Isso é Impressora").

A proposta é transformar o Agente em um **Auditor**. Ele não apenas classifica; ele aponta onde o humano provavelmente errou.

## 2. A Solução Técnica: "Audit Dashboard" (Tela de Auditoria)
Precisamos de uma interface visual simples para que você (o humano especialista) possa julgar os casos onde a IA discorda do Histórico.

### Stack Tecnológica Sugerida
*   **Backend**: Python (já temos toda a lógica pronta).
*   **Frontend Rápido**: **Streamlit**.
    *   *Por que?* É uma biblioteca Python opensource projetada para Data Science. Permite criar painéis interativos em minutos sem escrever HTML/CSS. Perfeito para "ferramentas internas".
    *   *Alternativa*: Gradio (mais focado em ML demos, Streamlit é melhor para Dashboards).

## 3. Fluxo de Trabalho (Workflow)

```mermaid
graph TD
    A[Dataset Sujo] -->|Entrada| B(Agente Classificador)
    B -->|Classifica| C{IA concorda com Humano?}
    C -->|Sim| D[Aprovado Automaticamente]
    C -->|Não| E[Fila de Discrença]
    E -->|Visualização| F[Streamlit Dashboard]
    F -->|Humano Julga| G{Quem está certo?}
    G -->|Humano| H[Manter Original]
    G -->|IA| I[Atualizar Label]
    H --> J[Dataset Limpo (Gold Standard)]
    I --> J
```

## 4. Visualização e Explicabilidade
O Dashboard deve mostrar, para cada ticket conflituoso:

1.  **O Problema (Ticket)**: Título e Descrição originais.
2.  **O Combate**:
    *   🥊 **Canto Azul (Humano)**: Categoria Original (ex: "Atendimento ao Usuário").
    *   🥊 **Canto Vermelho (IA)**: Categoria Sugerida (ex: "Impressora") + **Confiança** (ex: 98%).
3.  **A Prova (O "Porquê")**:
    *   Como nosso modelo usa *Embeddings* (matemática vetorial), ele não "fala" naturalmente.
    *   **Solução de Explicabilidade**: Exibir a **Definição do Contexto** que a IA escolheu.
    *   *Exemplo*: "A IA escolheu 'IMPRESSORA' porque este contexto aborda: 'toner', 'atolamento', 'papel'. O texto do ticket contém 'toner'."

## 5. Estratégia de Implementação
Não alteraremos o código do agente. Criaremos uma **camada de ferramentas** acima dele.

1.  **Script de Auditoria (`audit.py`)**: Roda o agente em todo o dataset e salva um arquivo `discrepancies.json` contendo apenas os conflitos.
2.  **App de Visualização (`app_audit.py`)**: Lê esse JSON e mostra a interface "Tinder de Tickets" (Esquerda/Direita para aprovar/rejeitar a sugestão da IA).
3.  **Ação de Correção**: O App salva as decisões em um novo arquivo `validation_dataset_CLEAN.json`.

## 6. Benefícios Imediatos
*   **Confiança**: Você verá com seus próprios olhos que a IA está acertando.
*   **Limpeza**: Em poucas horas, você transforma um dataset "viciado" em um Dataset de Ouro.
*   **Futuro**: Esse Dataset de Ouro será usado para treinar versões futuras ainda mais poderosas (Fine-tuning).
