# Contrato de Governança de Eventos (Fase 2)

Este documento define a semântica e as regras de autoridade para os eventos que alimentam o ecossistema de dados.

## 1. Definição de Evento Válido
Um **evento** é a menor unidade de mudança semântica registrada no sistema. No contexto da Fase 2, um evento é extraído de uma linha da `glpi_logs`.

- **Atributos Obrigatórios**:
    - `event_id`: Identificador único (original da `glpi_logs`).
    - `timestamp`: Quando a mudança ocorreu no GLPI.
    - `actor`: Quem realizou a mudança.
    - `payload`: O estado anterior e o novo estado (old_value, new_value).
    - `sequence_id`: ID incremental para garantir ordenação no Raw Event Store.

## 2. Taxonomia de Eventos

| Tipo | Descrição | Autoridade | Veracidade |
| :--- | :--- | :--- | :--- |
| **Intenção** | Criação de tickets, abertura de requisições. | Máxima | Define o nascimento do registro. |
| **Mutação** | Alteração de campos (status, técnico, categoria). | Alta | Requer integridade referencial com o pai. |
| **Correção** | Scripts de limpeza, ajustes manuais via banco. | Master | Sobrescreve projeções anteriores se necessário. |
| **Auditoria** | Logins, visualizações, logs de sistema. | Baixa | Não altera o Read Model, apenas auditoria. |

## 3. Regras de Processamento

1.  **Idempotência**: O processamento de um evento com o mesmo `event_id` deve produzir o mesmo efeito no Read Model.
2.  **Ordenação Estrita**: Projetores devem processar eventos em ordem sequencial de `sequence_id` para evitar corrupção de estado (ex: técnico B sendo atribuído antes do técnico A sair).
3.  **Descarte de Ruído**: Eventos que não possuem impacto semântico (ex: "ID Search Option" irrelevantes) são persistidos no Raw Event Store (Auditoria), mas ignorados pelos Projetores de BI.

## 4. Autoridade e Conflitos

- Em caso de conflito entre um **Log** e o **Snapshot** de API:
    - O **Log (Evento)** é a autoridade para a linha do tempo e métricas.
    - O **Snapshot** pode ser usado para "curar" o Read Model se detectarmos perda de logs (Ação Fantasma).
- O conflito deve gerar um log de **Divergência de Autoridade** para investigação técnica.
