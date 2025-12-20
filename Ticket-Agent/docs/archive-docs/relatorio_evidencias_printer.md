# Relatório de Evidências Operacionais: PRINTER_ISSUE

**Analista:** N2 (Agente)
**Fonte de Dados:** API GLPI (Tickets recentes)
**Amostra:** 7 tickets qualificados (de 101 analisados)
**Data da Análise:** 17/12/2025

Este relatório apresenta fatos observados nos dados históricos para subsidiar a decisão de governança sobre a identificação de impressoras.

---

## 1. Preenchimento de Campos Estruturados

### Evidência Observada
**100% dos tickets analisados (7/7) possuem os campos de localização e ativo vazios.**
Os campos `locations_id` e `items_id` (que vinculariam o chamado a uma impressora específica do inventário) chegaram zerados (`0` ou `None`) ao suporte.

### Exemplo Real (Anonimizado)
> **Ticket #81552**
> **Título:** "Suprimentos (Toner, Cartucho) - Toner da impressora acabou"
> **Conteúdo:** "Kyocera da Contabilidade..."
> **Dados:** `locations_id: 0`, `items_id: None`

### Limitação do Dado
A amostra reflete tickets recentes. Pode haver variação se existirem tickets abertos via portal legado onde o usuário fosse forçado a selecionar um item (se essa feature existia), mas no fluxo atual (Chat/API), o dado não chega.

---

## 2. Frequência de Identificadores no Texto

### Evidência Observada
**0% dos tickets (0/7) contêm identificadores técnicos inequívocos no corpo da descrição.**
Nenhum ticket da amostra mencionou endereço IP ("192..."), Caminho de Fila ("\\print...") ou Código de Patrimônio/Etiqueta.

### Exemplo Real
> **Ticket #81502**
> **Descrição:** "...impressora do segundo andar da casa amarela..."
> **Análise:** O técnico precisa saber onde fica a "casa amarela" e qual impressora está no "segundo andar".

### Limitação do Dado
Não prova que o usuário *não sabe* o dado, apenas que ele *não fornece espontaneamente* sem um prompt específico.

---

## 3. Padrão de Identificação pelo Usuário

### Evidência Observada
**Uso predominante de "Referências Locativas Informais" ou "Referência por Apelido".**
Os usuários identificam o ativo pelo local onde ele está ("da Contabilidade", "do Departamento") ou pela marca ("Kyocera").

### Exemplo Real
> **Ticket #81530**
> **Descrição:** "Impressora nao esta imprimindo nada" (Sem nenhuma referência de local).
> **Consequência N2:** Impossível atuar sem contato telefônico prévio (Triagem Incompleta).

---

## 4. Conclusão da Análise (Sem Decisão)

Os dados mostram que **o fluxo atual gera tickets "Órfãos de Ativo"**.
O Suporte N2 recebe a intenção correta (classificação de categoria funciona), mas recebe zero contexto sobre *qual* máquina é o alvo.
Não há evidência de que usuários forneçam patrimônio espontaneamente.

**Gargalo Identificado:** Dependência de conhecimento tácito do técnico ("Essa é a impressora que fica na mesa da Maria") ou contato ativo (Retrabalho).
