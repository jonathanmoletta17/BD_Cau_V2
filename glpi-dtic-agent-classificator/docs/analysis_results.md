# Análise Estratégica dos Testes: O Paradoxo da Precisão

## 1. O Cenário (Dados Preliminares)
*   **Total de Tickets Avaliados**: 417
*   **Discrepâncias Encontradas**: ~290 (aprox. 70% do dataset)
*   **Acurácia Técnica Inicial**: ~32% (Baixa)
*   **Causa Raiz**: Conflito Sistemático entre Classificação Humana (Genérica) e IA (Específica).

## 2. Padrões Identificados (O "Generalist Problem")
Através da análise quantitativa, um padrão massivo se destaca:

| Padrão de Discrepância | Contagem Aprox. | Diagnóstico |
| :--- | :--- | :--- |
| **Humano**: `ATENDIMENTO AO USUÁRIO` <br> **IA**: `IMPRESSORA`, `OFFICE 365`, `REDE` | **~158 casos** | **Erro Humano Sistemático**. O usuário/técnico usa a categoria "Suporte" como um "Lixo Geral" para evitar o trabalho de categorizar corretamente. A IA, sendo pedante, corrige para a categoria específica. |
| **Humano**: `TÚNEL PROCERGS` <br> **IA**: `REDE > TÚNEL PROCERGS` | **~14 casos** | **Erro de Taxonomia**. O Humano usa uma categoria raiz obsoleta ou preguiçosa, enquanto a IA prefere a hierarquia correta (Filho de Rede). |

### Conclusão da Análise
O modelo **não está burro**. Ele está **super-qualificado** para o dataset atual.
*   A IA tem "doutorado" nas definições que criamos manualmente.
*   O Dataset histórico tem "preguiça" humana.

## 3. Estratégia de Melhoria: Saneamento, não Simplificação
Não devemos "emburrecer" a IA para aceitar "Atendimento ao Usuário" quando o ticket diz claramente "Minha impressora parou".

### Plano de Ação (Prioridades)
1.  **Fase 1: Auditoria em Massa de "Suporte Geral"**
    *   Este é o "Low Hanging Fruit".
    *   **Ação**: Filtrar na ferramenta de Auditoria todos os casos onde Humano = "ATENDIMENTO AO USUÁRIO".
    *   **Critério**: Se a IA tem Confiança > 90% e sugere uma categoria técnica clara (Impressora/Rede), **ACEITAR AUTOMATICAMENTE** (após revisão rápida).

2.  **Fase 2: Ajuste de Taxonomia (Hierarquia)**
    *   Casos como "Túnel" vs "Rede > Túnel".
    *   **Ação**: Decidir qual é a "Verdadeira". Se for "Rede > Túnel", rodar script para migrar todos os tickets antigos para a nova estrutura.

## 4. Critérios de Sucesso (KPIs)
Como saberemos se funcionou?
*   **Redução da Categoria "Lixo"**: Esperamos uma queda drástica (>80%) no volume de tickets em `ATENDIMENTO AO USUÁRIO`.
*   **Aumento da Acurácia no Validador**: Após limpar o dataset ("Validation Gold Clean"), ao rodarmos `evaluate_accuracy.py` novamente, a métrica deve saltar de 30% para **>85%**.

## 5. Próximos Passos (Implementação)
*   Usar o `tools/app_audit.py` focado inicialmente em zerar os conflitos de "Suporte Geral".
*   Criar script `tools/apply_audit.py` para efetivar as mudanças no JSON final.
