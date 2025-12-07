# Guia de Validação e Calibração

Este guia descreve como validar a qualidade do modelo determinístico de classificação de tickets usando métricas objetivas.

---

## 1. Visualizando o Invisível

Para entender se suas categorias estão misturadas no espaço vetorial, usamos técnicas de redução de dimensionalidade.

### Ferramentas e Técnicas
*   **t-SNE / UMAP:** Visualização de clusters.
*   **Objetivo:** Ver "ilhas" de categorias separadas. Se houver sobreposição (nuvem misturada), as definições das categorias estão ambíguas.

---

## 2. Métricas de Qualidade

Para validar, você precisa de um **Conjunto de Teste (Gold Set)**: uma lista de tickets rotulados manualmente e revisados.

### Métricas Essenciais
1.  **Precisão (Precision):** Quando o modelo diz "É Impressora", ele acerta? (Evita falsos positivos).
2.  **Recall (Revocação):** De todos os problemas de impressora que existem, quantos o modelo encontrou?
3.  **F1-Score:** Média harmônica. O melhor número único para avaliar performance.

### Como medir
Rode o script de validação no Gold Set e gere uma **Matriz de Confusão** para ver onde o modelo confunde A com B.

---

## 3. Calibração de Thresholds (Limiares)

O modelo retorna um score de similaridade (0 a 1). A definição do limiar de corte deve ser baseada em dados.

### Metodologia
1.  Teste o modelo no Gold Set.
2.  Calcule a precisão para diferentes cortes (0.70, 0.80, 0.90).

### Critérios de Decisão
*   **Modo Assistente (Sugestão):** Threshold mais baixo (ex: 0.75). Errar pouco não é crítico, pois o humano revisa.
*   **Modo Autônomo (Automação):** Threshold alto (ex: 0.90 ou 0.95). Prioridade total para precisão; se tiver dúvida, não atua.

---

## 4. Quando a IA falha?

Se a performance for ruim mesmo com dados limpos:
1.  **Regras Léxicas:** Adicionar filtro de palavras-chave antes do embedding para casos óbvios ("toner" -> "Impressora").
2.  **Ambiguidade:** Revisar se a categoria de destino realmente faz sentido ou se o ticket é vago demais.
