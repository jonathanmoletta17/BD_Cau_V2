# Relatório de Auditoria Técnica: Inconsistências do Modelo de Classificação

## 1. Resumo Executivo
Realizamos uma auditoria profunda no código, nos dados e na lógica do Agente de Classificação (`simple_agent.py`). O modelo atual (E5-Large) apresenta uma **acurácia técnica de ~85%**, o que é alto para um sistema *zero-shot* (sem treinamento específico).

No entanto, a percepção de "erro" e inconsistência vem de três fontes principais:
1.  **Poluição de Dados (Ruído HTML)**: O modelo está "lendo" cabeçalhos de formulários e tags HTML em vez do problema real.
2.  **Esquizofrenia Taxonômica**: Existem categorias duplicadas com nomes diferentes (Ex: `IMPRESSORA` vs `DTIC > ... > IMPRESSORA`). O modelo fica dividido (50/50), e qualquer escolha é considerada "erro" se não bater com o humano.
3.  **Definições Circulares**: Muitas categorias no `category_context.json` são definidas como *"Tickets relacionados a [NOME DA CATEGORIA]"*. Isso não ensina nada ao modelo.

---

## 2. Diagnóstico de Inconsistências

### A. O Problema do "Formulário Fantasma" (Ruído)
Muitos tickets vêm de formulários web e contêm blocos gigantes de HTML e texto padrão.

*   **Exemplo Real (Ticket #69168)**:
    *   *O que o modelo vê*: `<h1>Dados do formulário</h1><h2>Dados Gerais</h2><div><b>1) LOCALIZAÇÃO...`
    *   *O Problema*: 80% do texto é lixo estrutural. O modelo dilui a importância das palavras-chave reais (ex: "Instalar Impressora") porque está processando "Dados Gerais", "Localização", etc.
    *   **Solução**: Implementar uma limpeza de texto (Regex) para remover tags HTML e frases padrão de formulários *antes* de gerar o embedding.

### B. O Conflito de "Exclusão" (Keyword Trap)
O modelo às vezes foca demais em uma palavra de ação ("Exclusão", "Instalação") e ignora o objeto ("Túnel", "Software").

*   **O Caso**: "Exclusão de Túnel VPN"
    *   *Predição do Modelo*: `EMAIL > EXCLUSÃO`
    *   *Por que?*: A categoria `EMAIL > EXCLUSÃO` provavelmente tem a palavra "Exclusão" muito forte em seu contexto. O modelo associa "Exclusão" a "Email" erroneamente.
    *   **Solução**: Alterar o contexto de `EMAIL > EXCLUSÃO` para *"Solicitação para remover, deletar ou desativar CONTAS DE E-MAIL. Não usar para exclusão de VPN ou outros serviços."*

### C. A Guerra das Impressoras (Duplicidade)
Temos duas categorias para a mesma coisa:
1.  `IMPRESSORA`
2.  `DTIC > EQUIPAMENTOS > INSTALAÇÃO > IMPRESSORA`

O modelo atribui 45% de probabilidade para uma e 45% para a outra. Se o humano escolheu a primeira e o modelo a segunda, conta como erro, mas semanticamente está correto.
*   **Solução**: Unificar a taxonomia. Ou usamos a estrutura simples (`IMPRESSORA`) ou a complexa (`DTIC...`). Ter as duas ativas confunde a IA.

---

## 3. Análise Arquitetural e Conceitual

### Modelo de Embedding (Multilingual-E5-Large)
*   **Paradigma**: Semantic Search (Busca Semântica).
*   **Como funciona**: Transforma texto em vetores numéricos. Textos com significados similares ficam próximos no espaço vetorial.
*   **Avaliação**: O modelo é excelente e adequado para a tarefa. O problema não é o "cérebro" (o modelo), mas o "livro didático" (os contextos) e os "óculos sujos" (dados não limpos).

### Lógica de Decisão (Cosine Similarity)
*   **Atual**: `argmax(cosine_similarity(query, categories))`
*   **Falha**: O sistema é "Winner-Takes-All". Se a categoria A tem score 0.81 e a B tem 0.80, ele escolhe A cegamente.
*   **Recomendação**: Implementar uma margem de segurança. Se a diferença entre o 1º e o 2º lugar for pequena (< 0.03), classificar como "Ambíguo" ou pedir revisão humana.

---

## 4. Plano de Ação (Roadmap de Correção)

Para atingir >95% de acurácia e eliminar a sensação de "inconsistência":

1.  **Saneamento de Dados (Imediato)**:
    *   Criar função `clean_html_tags()` no `preprocess.py`.
    *   Remover cabeçalhos de formulários ("Dados do formulário", "Dados Gerais").

2.  **Refatoração de Contextos (Curto Prazo)**:
    *   Reescrever `category_context.json`.
    *   Eliminar definições circulares ("Categoria X é para tickets de X").
    *   Adicionar **Exemplos Negativos** ("Use para X, mas NÃO use para Y").

3.  **Simplificação Taxonômica (Médio Prazo)**:
    *   Criar um mapa de "De-Para" para unificar categorias duplicadas antes da classificação.
    *   Ex: Se o modelo prever `DTIC > ... > IMPRESSORA`, converter internamente para `IMPRESSORA` antes de comparar.

## 5. Conclusão
O modelo não é "burro"; ele está confuso. Ele está tentando ler um texto cheio de lixo HTML e categorizá-lo em uma lista onde várias opções parecem iguais. Limpando a entrada e organizando as opções, a performance subirá drasticamente.
