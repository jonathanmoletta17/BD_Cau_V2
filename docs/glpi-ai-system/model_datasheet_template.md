# Ficha Técnica do Modelo de IA

**Nome do Projeto:** Agente Classificador GLPI
**Data de Atualização:** [Data Atual]
**Responsável Técnico:** [Nome]

---

## 1. Identificação do Modelo

| Campo | Valor Atual (Exemplo) |
| :--- | :--- |
| **Nome do Modelo Base** | `intfloat/multilingual-e5-large` |
| **Origem/Provedor** | Hugging Face (Open Source) |
| **Arquitetura** | Transformer (Encoder-only, baseada em BERT/RoBERTa) |
| **Tamanho (Parâmetros)** | ~560 Milhões de parâmetros |
| **Dimensão do Embedding** | 1024 dimensões |
| **Licença** | MIT / Apache 2.0 (Verificar específica do modelo) |

---

## 2. Capacidades e Especialidades

*   **Multilíngue:** Sim (Suporta 90+ idiomas, incluindo Português).
*   **Foco:** Otimizado para *semantic search* e *clustering*. Excelente para entender que "impressora quebrada" é similar a "falha de impressão".
*   **Contexto Máximo:** 512 tokens (aprox. 300-400 palavras).
    *   *Impacto:* Se o ticket for um log gigante de erro, o modelo vai ler apenas o começo. O script deve truncar ou resumir antes.

---

## 3. Limitações Conhecidas

1.  **Janela de Contexto:** Descrições muito longas são cortadas. Informação crucial no final do texto pode ser ignorada.
2.  **Viés de Treino:** O modelo sabe português geral, não o "dialeto de TI" específico da sua empresa. Pode confundir siglas internas se não houver contexto.
3.  **Sensibilidade:** Pode ser sensível a erros de digitação graves, embora embeddings sejam mais robustos que palavras-chave.

---

## 4. Parâmetros Operacionais

| Métrica | Valor Estimado |
| :--- | :--- |
| **Latência (GPU T4/A10)** | ~20ms a 50ms por ticket (batch=1) |
| **Consumo VRAM** | ~2GB a 4GB (dependendo do batch size) |
| **Throughput Máximo** | ~100 tickets/segundo (em batch otimizado) |

---

## 5. Histórico de Alterações (Log de Versão)

| Versão | Data | Alteração | Motivo |
| :--- | :--- | :--- | :--- |
| v1.0 | 01/01/2024 | Modelo inicial (e5-large) | PoC Inicial |
| v1.1 | --/--/---- | Adição de regras léxicas | Correção de erros em "Impressora" |
| ... | ... | ... | ... |
