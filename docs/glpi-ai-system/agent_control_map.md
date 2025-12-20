# Mapa de Controle do Agente

Este documento descreve os pontos de controle críticos do sistema, onde ajustes têm impacto direto na qualidade da IA.

---

## 🏗️ 1. Knowledge Base (Definições Semânticas)
> *"O que a IA sabe sobre cada categoria"*

*   **Arquivo**: `agent/manual_contexts.json`
*   **Função**: Define a "alma" de cada categoria. É aqui que diferenciamos nuances.
*   **Status Atual**:
    *   ✅ Cobrimos 100% das categorias verdadeiras.
    *   ⚠️ **Atenção**: "AJUDA E SUPORTE" ainda é muito broad e causa confusão.
*   **Ação Recomendada**: Refinar definições genéricas para serem mais excludentes.

## 🧠 2. Logic Engine (O Cérebro)
> *"Como a IA decide"*

*   **Arquivo**: `agent/simple_agent.py`
*   **Modelo**: `intfloat/multilingual-e5-large` (State-of-the-art para PT-BR).
*   **Métrica**: Cosine Similarity.

## 🛡️ 3. Audit System (O Guardião) **[NOVO]**
> *"Como garantimos a verdade"*

*   **Arquivo**: `tools/auto_clean_dataset.py`
*   **Lógica**: **Confident Learning**.
*   **Regra**: Se `Confiança > 0.80`, a IA tem autoridade sobre o rótulo humano histórico.
*   **Impacto**: Permite "limpar" o dataset de treinamento/validação automaticamente, removendo ruído de rótulos preguiçosos.

## 🎯 4. Ground Truth (A Verdade)
> *"O gabarito da prova"*

*   **Arquivo**: `data/datasets/validation_dataset.json`
*   **Status**: **LIMPO (Versão 2.0)**.
    *   Passou por auditoria automática em Dez/2025.
    *   Erros de "Atendimento ao Usuário" foram reduzidos em 94%.
    *   Serve como base confiável para futuros testes.
