# ADR-001: Reescrita para Arquitetura Híbrida (Vetorial + LLM)

> **Status:** Aceito / Em Implementação
> **Data:** Dez/2025
> **Origem:** Plano de Reescrita (.trae)

## Contexto
O projeto original utilizava uma abordagem de "IA Generativa Pura" (estilo Chatbot/Llama) para classificar tickets. Essa abordagem mostrou-se propensa a alucinações, lenta e difícil de calibrar para regras de negócio estritas. Além disso, os dados históricos do GLPI ("Dados Sujos") estavam sendo usados para treinamento, perpetuando erros de classificação.

## Decisão
Mudança fundamental de paradigma para um **Sistema Híbrido Determinístico**.

### Nova Arquitetura
1.  **Motor Principal (Rápido & Determinístico):**
    *   Baseado em **Embeddings** (Vetores Matemáticos) e Similaridade de Cosseno.
    *   Modelo: `intfloat/multilingual-e5-large` ou similar.
    *   Função: Classificar 80-90% dos tickets com base em proximidade semântica.

2.  **Motor Secundário (Inteligente):**
    *   Baseado em **LLM** (Llama 3 / NVIDIA NIM).
    *   Função: Atuar como "Juiz" apenas em casos de baixa confiança (`0.70 < score < 0.85`) ou ambiguidade.
    *   Uso de Prompts JSON estruturados para garantir saída parsável.

3.  **Estratégia de Dados (Golden Tickets):**
    *   Abandonar o treinamento cego no histórico completo.
    *   Criar "Golden Tickets" (Exemplos de Ouro): Um conjunto curado de tickets perfeitos para cada categoria.
    *   Gerar **Vetores de Referência (Centroides)** a partir desses exemplos.

## Benefícios Esperados
*   **Velocidade:** Busca vetorial é milissegundos; LLM é segundos.
*   **Custo:** Redução drástica de tokens LLM.
*   **Controle:** Thresholds matemáticos claros para definir "Sei" vs "Não sei".
*   **Manutenibilidade:** Fácil adicionar uma nova categoria (basta adicionar 1 exemplo "Golden" e reindexar).

## Conceitos Chave (Glossário)
*   **Encoder:** Transforma texto em vetor.
*   **Vector Store:** Banco de dados simples para guardar os vetores das categorias.
*   **Cosine Similarity:** Métrica de distância usada (orientação do vetor) em vez de Euclidiana.
*   **Threshold Calibration:** Definição matemática do corte de confiança.
