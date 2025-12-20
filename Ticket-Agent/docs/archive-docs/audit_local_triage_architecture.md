# Auditoria de Arquitetura: Agente de Triagem Local (`local_triage`)

**Data**: 17/12/2025
**Objetivo**: Mapear a estrutura atual, identificar duplicidade e propor limpeza.

## 1. Mapa da Estrutura Atual (O "Estado da Arte")

O fluxo do agente é definido em `new_graph.py`. Ele orquestra os seguintes arquivos:

| Nó no Grafo (`new_graph.py`) | Arquivo Python (Implementação) | Função | Status |
| :--- | :--- | :--- | :--- |
| `viability` | `viability_node.py` | Decide se conversa tem "substância" para avançar. | ✅ ATIVO (Moderno) |
| `ask_more` | `smart_inquiry_node.py` | Cérebro Híbrido. Faz perguntas de slot-filling e validação. | ✅ ATIVO (Moderno) |
| `classifier` | `new_nodes_migration.py` | Wrapper para o Motor de Classificação do Agente A (Service Factory). | ✅ ATIVO (Nome Confuso) |
| `ticket_creator` | `nodes.py` | Monta payload e chama API do GLPI. | ✅ ATIVO (Misturado com Legado) |
| `finalizer` | `nodes.py` | Gera mensagem final de sucesso/falha. | ✅ ATIVO (Misturado com Legado) |

## 2. Análise de Inconsistências Detectadas

### A. O Cemitério em `nodes.py`
O arquivo `agents/local_triage/nodes.py` tem 325 linhas, mas metade é código morto.
*   `classify_node` (Legado): Comentado. Substituído por `new_nodes_migration.py`.
*   `extract_node` (Legado): Comentado. Substituído por `smart_inquiry_node.py`.
*   `generate_question_node` (Legado): Comentado. Substituído por `smart_inquiry_node.py`.
*   **Problema**: Dificulta a leitura. Parece que tem duplicação, mas é apenas "história não apagada".

### B. Nomenclatura Confusa
*   `new_nodes_migration.py`: O nome sugere um script temporário de migração, mas ele contém a lógica crítica de conectar com o Agente A. Deveria se chamar `classifier_node.py`.
*   `new_graph.py`: O "new" é redundante. Deveria ser o `graph.py` oficial.

### C. Dispersão Lógica
*   A lógica de "Check Completeness" (verificar campos) está duplicada:
    *   Em `nodes.py` (função `check_completeness` - usada pelo legado).
    *   Em `smart_inquiry_node.py` (lógica embutida no prompt do sistema - usada pelo moderno).

## 3. Plano de Correção (Roadmap de Limpeza)

Para resolver a sensação de "inconsistência", recomendo a seguinte refatoração (NÃO EXECUTEI AINDA):

1.  **Limpar `nodes.py`**:
    *   Remover todo o código comentado (`classify_node`, `extract_node`, etc).
    *   Manter apenas `create_ticket_node` e `finalize_response_node`.
    *   Renomear o arquivo para `execution_nodes.py` (já que ele só executa, não pensa).

2.  **Renomear e Consolidar**:
    *   `new_nodes_migration.py` -> `classifier_wrapper_node.py`.
    *   `new_graph.py` -> `graph.py` (Assumir como oficial).

3.  **Centralizar Configuração**:
    *   Garantir que `intents_config.json` seja a ÚNICA fonte de verdade. Remover o fallback hardcoded em `nodes.py` (linhas 48-52).

## 4. Conclusão da Auditoria
Não há **duplicação funcional ativa** (o código antigo está comentado), mas há **poluição visual**.
A estrutura parece fragmentada porque estamos no meio de uma transição de arquitetura (de "Node-based Regex" para "Graph-based Hybrid LLM").

A limpeza é segura e recomendada para reduzir a carga cognitiva do desenvolvedor.
