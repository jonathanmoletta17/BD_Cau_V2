# Roadmap e Recomendações de Evolução

Este documento sintetiza o diagnóstico atual e propõe um plano de ação estruturado para transformar o piloto em um sistema de produção confiável.

---

## 1. Diagnóstico Imediato (O que corrigir HOJE)

Os problemas relatados apontam para **falhas críticas** na qualidade dos dados de referência:

1.  **Dados de Referência Sujos:** Os embeddings das categorias foram gerados com base em histórico sem curadoria. O modelo "aprendeu errado".
2.  **Ausência de Lista Fechada:** O agente precisa ter uma lista estrita de categorias ativas para não sugerir opções obsoletas.

---

## 2. Roteiro de Evolução

### Fase 1: Higienização e Controle (Curto Prazo - 1 a 2 semanas)
*Objetivo: Parar de errar o óbvio.*

*   [ ] **Auditoria de Categorias:** Listar as categorias ativas no GLPI e congelar essa lista no agente (`category_context.json`).
*   [ ] **Curadoria Manual (Golden Set):** Escrever descrições claras para cada categoria crítica.
*   [ ] **Embeddings "Puros":** Regenerar os vetores de referência das categorias usando *apenas* a descrição oficial (ignorar o resto do histórico).

### Fase 2: Maturação e Validação (Médio Prazo - 1 mês)
*Objetivo: Ganhar confiança para automação.*

*   [ ] **Pipeline de Validação:** Criar script que roda o modelo contra um conjunto de teste (tickets passados rotulados) e calcula métricas (F1-Score).
*   [ ] **Calibração de Thresholds:** Definir matematicamente qual score (0.80? 0.92?) garante precisão suficiente para automação.
*   [ ] **Feedback Loop (V1):** Implementar lógica simples: se técnico altera a categoria que o bot sugeriu, salvar esse ticket para análise.

### Fase 3: Escala e Sofisticação (Longo Prazo - 3+ meses)
*Objetivo: Alta performance e integração.*

*   [ ] **NVIDIA Triton:** Migrar a inferência para um servidor dedicado, permitindo que múltiplos sistemas usem a IA.
*   [ ] **Integração com Chatbot:** Usar o mesmo motor de classificação para sugerir soluções ao usuário antes de abrir o ticket.

---

## 3. Recomendações Finais de Governança

1.  **Não automatize sem medir:** Nunca coloque o agente para alterar tickets em massa sem antes rodar no conjunto de validação e ver a acurácia.
2.  **Comece como "Copiloto":** Configure o agente para apenas *sugerir* (comentário privado) ou preencher campos apenas se estiverem vazios.
3.  **Documente a Regra de Negócio:** A IA não adivinha regra. Se "Mouse" vai em "Periféricos" e não em "Hardware", isso precisa estar escrito na descrição da categoria.
