# RELATÓRIO DE AUDITORIA - Schema DTIC

**Data:** 2025-12-07 18:02:01

---

## SUMÁRIO EXECUTIVO

- **Total de Tabelas:** 12
- **Tabelas Vazias:** 1
- **Total de Registros:** 62,740

## PROBLEMAS ENCONTRADOS

### CRÍTICO

- **ticket_changes.usuario_id**: Coluna completamente vazia
- **tickets.entidade_id**: Coluna completamente vazia
- **tickets.localizacao_id**: Coluna completamente vazia
- **tickets.item_relacionado_id**: Coluna completamente vazia
- **tickets.tempo_para_resolver**: Coluna completamente vazia
- **tickets.tempo_para_atribuir**: Coluna completamente vazia
- **tickets.tempo_acao_total**: Coluna completamente vazia
- **tickets.solucionado_em**: Coluna completamente vazia
- **tickets.fechado_em**: Coluna completamente vazia
- **tickets_users**: TABELA VAZIA

### AVISOS

- **glpi_locations.parent_id**: 74.0% nulos
- **ticket_changes.valor_antigo**: 50.2% nulos
- **ticket_changes.valor_antigo**: ID_PARENTHESES (78 ocorrências)
- **ticket_changes.valor_novo**: ID_PARENTHESES (100 ocorrências)
- **tickets.titulo**: HTML_ENTITY (1 ocorrências)
- **tickets.descricao**: ID_PARENTHESES (25 ocorrências)

---

## ANÁLISE DETALHADA POR TABELA


### glpi_entities

**Registros:** 89

| Coluna | Tipo | Nulos | Problemas | Amostra |
|--------|------|-------|-----------|---------|
| id | INTEGER | 0.0% | - | - |
| name | VARCHAR(255) | 0.0% | - | PIRATINI |
| completename | TEXT | 0.0% | - | Entidade raiz > PIRATINI |
| level | INTEGER | 0.0% | - | - |
| entities_id | INTEGER | 3.4% | - | - |
| sincronizado_em | TIMESTAMP | 0.0% | - | - |


### glpi_groups

**Registros:** 170

| Coluna | Tipo | Nulos | Problemas | Amostra |
|--------|------|-------|-----------|---------|
| id | INTEGER | 0.0% | - | - |
| name | VARCHAR(255) | 0.0% | - | CC-SE-SUBJUR-DINFO |
| is_task | BOOLEAN | 0.0% | - | - |
| is_itemgroup | BOOLEAN | 0.0% | - | - |
| sincronizado_em | TIMESTAMP | 0.0% | - | - |


### glpi_groups_users

**Registros:** 1,257

| Coluna | Tipo | Nulos | Problemas | Amostra |
|--------|------|-------|-----------|---------|
| id | INTEGER | 0.0% | - | - |
| groups_id | INTEGER | 0.0% | - | - |
| users_id | INTEGER | 0.0% | - | - |
| is_dynamic | BOOLEAN | 0.0% | - | - |
| is_manager | BOOLEAN | 0.0% | - | - |
| sincronizado_em | TIMESTAMP | 0.0% | - | - |


### glpi_itilcategories

**Registros:** 131

| Coluna | Tipo | Nulos | Problemas | Amostra |
|--------|------|-------|-----------|---------|
| id | INTEGER | 0.0% | - | - |
| name | VARCHAR(255) | 0.0% | - | EMAIL |
| completename | TEXT | 0.0% | - | ACESSO A SISTEMAS > OFFICE 365 > EMAIL |
| level | INTEGER | 0.8% | - | - |
| parent_id | INTEGER | 0.8% | - | - |
| ancestors_cache | TEXT | 3.8% | - | {"1":1,"20":20} |
| sincronizado_em | TIMESTAMP | 0.8% | - | - |


### glpi_locations

**Registros:** 77

| Coluna | Tipo | Nulos | Problemas | Amostra |
|--------|------|-------|-----------|---------|
| id | INTEGER | 0.0% | - | - |
| name | VARCHAR(255) | 0.0% | - | Casa Civil 1005 |
| level | INTEGER | 0.0% | - | - |
| parent_id | INTEGER | 74.0% | MOSTLY_NULL | - |
| ancestors_cache | TEXT | 0.0% | - | [] |
| sincronizado_em | TIMESTAMP | 0.0% | - | - |


### glpi_profiles

**Registros:** 18

| Coluna | Tipo | Nulos | Problemas | Amostra |
|--------|------|-------|-----------|---------|
| id | INTEGER | 0.0% | - | - |
| name | VARCHAR(255) | 0.0% | - | Self-Service |
| is_default | BOOLEAN | 0.0% | - | - |
| sincronizado_em | TIMESTAMP | 0.0% | - | - |


### glpi_profiles_users

**Registros:** 2,546

| Coluna | Tipo | Nulos | Problemas | Amostra |
|--------|------|-------|-----------|---------|
| id | INTEGER | 0.0% | - | - |
| users_id | INTEGER | 0.0% | - | - |
| profiles_id | INTEGER | 0.0% | - | - |
| entities_id | INTEGER | 0.0% | - | - |
| is_recursive | BOOLEAN | 0.0% | - | - |
| is_dynamic | BOOLEAN | 0.0% | - | - |
| sincronizado_em | TIMESTAMP | 0.0% | - | - |


### glpi_users

**Registros:** 2,409

| Coluna | Tipo | Nulos | Problemas | Amostra |
|--------|------|-------|-----------|---------|
| id | INTEGER | 0.0% | - | - |
| name | VARCHAR(255) | 0.0% | - | yasmine-freitas |
| realname | VARCHAR(255) | 0.1% | - | Iensen de Freitas |
| firstname | VARCHAR(255) | 0.1% | - | Yasmine |
| email | VARCHAR(255) | 1.2% | - | yasmine-freitas@casacivil.rs.gov.br |
| is_active | BOOLEAN | 0.0% | - | - |
| is_deleted | BOOLEAN | 0.0% | - | - |
| sincronizado_em | TIMESTAMP | 0.0% | - | - |


### ticket_changes

**Registros:** 37,632

| Coluna | Tipo | Nulos | Problemas | Amostra |
|--------|------|-------|-----------|---------|
| id | INTEGER | 0.0% | - | - |
| glpi_id | INTEGER | 0.0% | - | - |
| ticket_id | INTEGER | 0.0% | - | - |
| data_mudanca | TIMESTAMP | 0.0% | - | - |
| usuario_id | INTEGER | 100.0% | FULLY_NULL | - |
| usuario_nome | VARCHAR(255) | 0.0% | - | Anderson da Silva Morim de Oliveira |
| campo | VARCHAR(100) | 0.0% | - | Entidade |
| campo_id | INTEGER | 0.0% | - | - |
| valor_antigo | TEXT | 50.2% | MOSTLY_NULL, ID_PARENTHESES | Entidade raiz > PIRATINI > CENTRAL DE ATENDIMENTOS |
| valor_novo | TEXT | 30.1% | ID_PARENTHESES | Entidade raiz > PIRATINI > CENTRAL DE ATENDIMENTOS |
| sincronizado_em | TIMESTAMP | 0.0% | - | - |


### tickets

**Registros:** 11,339

| Coluna | Tipo | Nulos | Problemas | Amostra |
|--------|------|-------|-----------|---------|
| id | INTEGER | 0.0% | - | - |
| glpi_id | INTEGER | 0.0% | - | - |
| titulo | VARCHAR(500) | 0.0% | HTML_ENTITY | troca de perifierico |
| descricao | TEXT | 0.2% | ID_PARENTHESES | usuário solicita troca de teclado |
| status_id | INTEGER | 0.0% | - | - |
| prioridade_id | INTEGER | 0.0% | - | - |
| tipo_id | INTEGER | 0.0% | - | - |
| impact | INTEGER | 0.0% | - | - |
| urgency | INTEGER | 0.0% | - | - |
| categoria_id | INTEGER | 0.6% | - | - |
| entidade_id | INTEGER | 100.0% | FULLY_NULL | - |
| localizacao_id | INTEGER | 100.0% | FULLY_NULL | - |
| item_relacionado_id | INTEGER | 100.0% | FULLY_NULL | - |
| ultimo_atualizador_id | INTEGER | 0.0% | - | - |
| tempo_para_resolver | INTEGER | 100.0% | FULLY_NULL | - |
| tempo_para_atribuir | INTEGER | 100.0% | FULLY_NULL | - |
| tempo_primeira_interacao | INTEGER | 37.3% | - | - |
| tempo_acao_total | INTEGER | 100.0% | FULLY_NULL | - |
| tipo_requisicao_id | INTEGER | 0.0% | - | - |
| criado_em | TIMESTAMP | 0.0% | - | - |
| atualizado_em | TIMESTAMP | 0.0% | - | - |
| solucionado_em | TIMESTAMP | 100.0% | FULLY_NULL | - |
| fechado_em | TIMESTAMP | 100.0% | FULLY_NULL | - |
| url | VARCHAR(500) | 0.0% | - | http://10.72.16.202/atual/front/ticket.form.php?id |
| is_deleted | BOOLEAN | 0.0% | - | - |
| ticket_hash | VARCHAR(32) | 0.0% | - | 0006bdb027c4bc396deaf28500e22441 |
| sincronizado_em | TIMESTAMP | 0.0% | - | - |
| versao | INTEGER | 0.0% | - | - |


### tickets_groups

**Registros:** 7,072

| Coluna | Tipo | Nulos | Problemas | Amostra |
|--------|------|-------|-----------|---------|
| id | INTEGER | 0.0% | - | - |
| ticket_id | INTEGER | 0.0% | - | - |
| group_id | INTEGER | 0.0% | - | - |
| type | INTEGER | 0.0% | - | - |
| sincronizado_em | TIMESTAMP | 0.0% | - | - |


### tickets_users

**Registros:** 0

**Status:** VAZIA
