# Conceitos de IA: Embeddings e Classificação Semântica

Este documento explica a base tecnológica do sistema de classificação de tickets, focando no modelo determinístico de embeddings.

---

## 1. Embeddings: A Base do Sistema

### O que são?
Embeddings são a tradução de texto (palavras, frases) para vetores numéricos (listas de números) em um espaço multidimensional.

*   **Conceito Chave:** Textos com significados semelhantes ficam *fisicamente próximos* nesse espaço vetorial.
*   **Exemplo:** O vetor de "impressora" estará matematicamente próximo de "toner" e "papel", mas distante de "login".

### Como funciona no Agente?
Utilizamos um **Modelo de Embedding** pré-treinado (atualmente `intfloat/multilingual-e5-large`) que roda localmente (via biblioteca `sentence-transformers`).

O processo é determinístico:
1.  **Entrada:** O agente recebe o texto do ticket.
2.  **Conversão:** O modelo gera um vetor fixo para esse texto.
3.  **Comparação:** O agente calcula a distância (similaridade de cosseno) entre o vetor do ticket e os vetores das categorias cadastradas.
4.  **Decisão:** A categoria com maior similaridade é escolhida (se superar o limiar de confiança).

### Por que não usamos LLMs Generativos (GPT/Ollama)?
Para esta tarefa específica (classificação em massa), embeddings são superiores porque:
*   **Velocidade:** Processam milissegundos vs. segundos.
*   **Consistência:** O mesmo texto sempre gera o mesmo vetor (sem "alucinações").
*   **Custo:** Exigem muito menos hardware (VRAM/GPU).

---

## 2. O Papel da Qualidade dos Dados ("Garbage In, Garbage Out")

Como o modelo compara o ticket com a definição das categorias, a precisão depende da qualidade dessas definições.

### O Problema
Se a definição da categoria "Impressora" for vaga ou baseada em tickets históricos classificados errados, o vetor de referência ficará "sujo".
*   **Exemplo:** Se tickets de "Rede" foram classificados como "Impressora" no passado e usamos isso como base, o modelo aprenderá que "wifi" também é "Impressora".

### A Solução: Curadoria (Golden Standard)
Nossa estratégia foca em definir um "Padrão Ouro" para cada categoria no arquivo `agent/category_context.json`.
1.  **Descrição Canônica:** Texto claro e ideal do que pertence à categoria.
2.  **Exemplos Curados:** Lista de termos ou frases inequívocas.

Isso garante que a IA siga a regra de negócio, não os vícios do histórico.
