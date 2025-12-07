# Relatório Técnico de Inconsistências Sistêmicas (ISO/IEC 26515)
**ID do Documento:** INC-2025-001
**Versão:** 1.0
**Data:** 2025-12-06
**Status:** Análise Preliminar
**Classificação:** Confidencial / Interno

---

## 1. Controle de Documento e Histórico

| Versão | Data       | Autor            | Descrição das Alterações |
| :---   | :---       | :---             | :---                     |
| 1.0    | 2025-12-06 | AI Assistant     | Criação inicial do relatório detalhado de inconsistências. |

---

## 2. Inconsistência #1: Poluição de Dados por Artefatos HTML (Phantom Form Effect)

### 2.1 Descrição Detalhada
*   **Contexto:** Módulo de Pré-processamento (`glpi_agent/preprocess.py`) e Ingestão de Tickets.
*   **Fluxo:** O Agente recebe o conteúdo bruto do ticket via API do GLPI -> Concatena Título + Conteúdo -> Gera Embedding.
*   **Impacto:**
    *   **Técnico:** O vetor de embedding é contaminado por tokens irrelevantes ("Dados do formulário", "div", "h1").
    *   **Operacional:** Redução da acurácia em tickets abertos via formulário web. O modelo classifica com base na estrutura do formulário, não no problema do usuário.
    *   **Evidência:**
        *   *Ticket ID:* #69168
        *   *Input:* `<h1>Dados do formulário</h1>...` (800 caracteres de HTML) + `...impressora não funciona` (20 caracteres úteis).
        *   *Output:* Classificação incorreta devido à diluição semântica.

### 2.2 Análise Técnica (Causa Raiz - 5 Whys)
1.  **Por que o modelo errou?** O texto de entrada continha mais ruído do que sinal.
2.  **Por que havia ruído?** O sistema ingere o campo `content` do GLPI raw (bruto), que armazena HTML.
3.  **Por que não foi limpo?** A função `join_title_description` faz apenas uma concatenação simples, sem sanitização de HTML.
4.  **Por que não houve sanitização?** O design inicial assumiu que o modelo lidaria bem com ruído ou que os tickets eram texto plano (e-mail).
5.  **Causa Raiz:** Ausência de uma etapa de *HTML Stripping* no pipeline de pré-processamento.

### 2.3 Classificação Estratégica
*   **Impacto:** Alto (Afeta ~40% dos tickets).
*   **Probabilidade:** Certa (Ocorre em 100% dos tickets via formulário).
*   **Criticidade:** **CRÍTICA**.

### 2.4 Proposta de Solução
*   **Ação:** Implementar `BeautifulSoup` ou Regex para extrair apenas texto visível.
*   **Esforço:** Baixo (2 horas).
*   **Risco:** Baixo (Pode remover formatação útil, mas o ganho supera a perda).

---

## 3. Inconsistência #2: Ambiguidade Taxonômica (Doppelgänger Categories)

### 3.1 Descrição Detalhada
*   **Contexto:** Definição de Categorias (`category_context.json`) e Lógica de Validação.
*   **Problema:** Existência de categorias semanticamente idênticas mas sintaticamente distintas.
    *   A: `IMPRESSORA`
    *   B: `DTIC > EQUIPAMENTOS > INSTALAÇÃO > IMPRESSORA`
*   **Impacto:**
    *   **Técnico:** O modelo divide a probabilidade (Softmax) entre A e B (ex: 0.45 vs 0.44).
    *   **Operacional:** Falsos negativos nos relatórios de acurácia. O agente acerta a *intenção* mas erra o *rótulo exato*.
*   **Evidência:** Relatório de Acurácia mostra 8 erros onde `True: IMPRESSORA` e `Pred: DTIC > ... > IMPRESSORA`.

### 3.2 Análise Técnica
*   **Diagrama de Ishikawa (Espinha de Peixe):**
    *   *Processo:* Falta de governança na criação de categorias no GLPI.
    *   *Sistema:* O validador usa comparação estrita de strings (`==`) em vez de equivalência semântica.
    *   *Dados:* Histórico legado misturado com nova estrutura.

### 3.3 Classificação Estratégica
*   **Impacto:** Médio (Distorce métricas, mas a ação final do suporte seria correta).
*   **Probabilidade:** Alta.
*   **Criticidade:** **ALTA** (Invalida a confiança no relatório).

### 3.4 Proposta de Solução
*   **Ação Imediata:** Criar mapa de equivalência (`canonical_map`) no validador.
*   **Ação Definitiva:** Projeto de Reestruturação de Categorias (ver Seção 5).

---

## 4. Inconsistência #3: Definições Circulares e "Keyword Traps"

### 4.1 Descrição Detalhada
*   **Contexto:** `category_context.json`.
*   **Problema:** Descrições que não descrevem.
    *   *Ex:* "Tickets relacionados a EXCLUSÃO".
*   **Impacto:** O modelo aprende a palavra "EXCLUSÃO" como token principal, ignorando o contexto (ex: "Exclusão de VPN" cai em "Exclusão de E-mail").

### 4.2 Análise Técnica
*   **Causa Raiz:** O arquivo de contexto foi gerado assumindo que o nome da categoria era autoexplicativo para a IA. Modelos de embedding precisam de *descrições semânticas ricas*.

### 4.3 Proposta de Solução
*   **Ação:** Reescrever contextos usando a técnica "Positive/Negative Examples".
    *   *De:* "Tickets de exclusão."
    *   *Para:* "Solicitações para remover contas de e-mail. NÃO use para VPN ou acesso à rede."

---

## 5. Plano de Reestruturação de Categorias (Sandbox)

### 5.1 Estrutura Proposta (Simplificada)
O objetivo é reduzir a profundidade da árvore e eliminar redundâncias.

| Atual (Complexo) | Proposto (Canonical) |
| :--- | :--- |
| `DTIC > EQUIPAMENTOS > INSTALAÇÃO > IMPRESSORA` | `HARDWARE > IMPRESSORA` |
| `IMPRESSORA` | `HARDWARE > IMPRESSORA` |
| `IMPRESSORA > ATOLAMENTO` | `HARDWARE > IMPRESSORA` (Tag: Manutenção) |
| `ACESSO A SISTEMAS > OFFICE 365 > EMAIL` | `SOFTWARE > EMAIL` |

### 5.2 Protocolo de Teste A/B (Sandbox)
1.  **Ambiente:** Criar `category_context_V2.json`.
2.  **Execução:** Rodar `evaluate_accuracy.py` duas vezes:
    *   Run A: Usando Contexto V1.
    *   Run B: Usando Contexto V2 (com mapeamento de De-Para nos resultados).
3.  **Métrica de Sucesso:** Acurácia V2 > Acurácia V1 + 10%.

---

## 6. Plano de Ação Imediato (Next Steps)

1.  **Implementar `clean_html`** no `glpi_agent/preprocess.py`.
2.  **Criar `tools/analyze_structure.py`** para mapear todas as duplicatas automaticamente.
3.  **Gerar `category_context_V2_DRAFT.json`** com as descrições melhoradas.

---
**Aprovação Técnica:**
__________________________
Agente AI - Tech Lead
