# Referência de Modelos de Dados (Data Models)

Esta seção descreve detalhadamente as estruturas de dados (schemas) utilizadas nas requisições e respostas da API do Agente de Triagem.

---

## 1. ClassificationRequest
Utilizado como corpo da requisição no endpoint `/classify`. Representa o pedido de classificação de um chamado.

| Campo | Tipo | Obrigatório | Descrição | Restrições/Notas |
| :--- | :--- | :---: | :--- | :--- |
| `description` | `string` | **Sim** | Descrição completa do problema relatado pelo usuário. | Deve conter texto suficiente para análise semântica. |
| `title` | `string` | Não | Título ou resumo curto do chamado. | Opcional. Se não fornecido, a IA tentará inferir ou usar um padrão. |
| `max_candidates` | `integer` | Não | Número máximo de categorias candidatas a retornar. | Default: `5`. Mínimo recomendado: 1. |

### Exemplo JSON
```json
{
  "description": "Meu monitor Dell parou de ligar e está cheirando a queimado.",
  "title": "Problema no Monitor",
  "max_candidates": 3
}
```

---

## 2. ClassificationResponse
Utilizado como corpo da resposta no endpoint `/classify`. Contém o resultado da análise da IA.

| Campo | Tipo | Obrigatório | Descrição | Restrições/Notas |
| :--- | :--- | :---: | :--- | :--- |
| `selected_category_id` | `integer` | **Sim** | ID numérico da categoria GLPI selecionada. | Retorna ID válido do GLPI ou fallback. |
| `selected_category_name` | `string` | **Sim** | Nome completo da categoria (breadcrumb). | Ex: `Hardware > Periféricos > Monitor` |
| `confidence` | `float` | **Sim** | Pontuação de confiança da classificação. | Intervalo: `0.0` a `1.0`. |
| `reasoning` | `string` | **Sim** | Explicação textual do motivo da escolha. | Gerado pela IA. |
| `ticket_type` | `integer` | **Sim** | Tipo de chamado sugerido. | `1` = Incidente, `2` = Requisição. |
| `urgency` | `integer` | **Sim** | Nível de urgência sugerido. | `1` (Muito Baixa) a `5` (Muito Alta). |
| `impact` | `integer` | **Sim** | Nível de impacto sugerido. | `1` (Muito Baixo) a `5` (Muito Alto). |
| `suggested_title` | `string` | Não | Título padronizado sugerido para o chamado. | Pode ser nulo se a IA não gerar. |
| `candidates` | `List[CategoryScore]` | **Sim** | Lista de outras categorias consideradas. | Ver modelo `CategoryScore`. |

### Exemplo JSON
```json
{
  "selected_category_id": 5755,
  "selected_category_name": "Hardware > Periféricos > Monitor",
  "confidence": 0.95,
  "reasoning": "O usuário relatou falha física (não liga, cheiro de queimado) em um monitor.",
  "ticket_type": 1,
  "urgency": 4,
  "impact": 3,
  "suggested_title": "[Hardware] Monitor Queimado - Dell",
  "candidates": [ ... ]
}
```

---

## 3. CategoryScore
Representa uma categoria candidata e sua pontuação de relevância.

| Campo | Tipo | Obrigatório | Descrição | Restrições/Notas |
| :--- | :--- | :---: | :--- | :--- |
| `category_id` | `integer` | **Sim** | ID da categoria no GLPI. | - |
| `name` | `string` | **Sim** | Nome da categoria. | - |
| `score` | `float` | **Sim** | Pontuação de relevância. | `0.0` a `1.0`. |
| `description` | `string` | Não | Descrição da categoria (se disponível). | - |

---

## 4. ChatMessage
Estrutura básica de uma mensagem em um histórico de chat. Utilizado no endpoint `/chat`.

| Campo | Tipo | Obrigatório | Descrição | Restrições/Notas |
| :--- | :--- | :---: | :--- | :--- |
| `role` | `string` | **Sim** | Papel do emissor da mensagem. | Valores comuns: `user`, `assistant`, `system`. |
| `content` | `string` | **Sim** | Conteúdo textual da mensagem. | - |

### Exemplo JSON
```json
{
  "role": "user",
  "content": "Preciso de ajuda com minha senha."
}
```
