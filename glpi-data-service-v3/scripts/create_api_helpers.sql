-- API Helper Views - V3
-- Views que retornam dados com IDs corretos para uso com GLPI API

-- 1. View de Tickets para API
CREATE OR REPLACE VIEW dtic.v_tickets_api AS
SELECT 
    t.glpi_id AS ticket_id,
    t.titulo,
    t.descricao,
    t.status_id,
    t.prioridade_id,
    t.categoria_id,
    t.entidade_id,
    t.criado_em,
    t.atualizado_em,
    t.solucionado_em,
    t.fechado_em,
    t.url
FROM dtic.tickets t;

COMMENT ON VIEW dtic.v_tickets_api IS 'Tickets com GLPI IDs prontos para uso com API';

-- 2. View de Tickets com Usuários para API
CREATE OR REPLACE VIEW dtic.v_tickets_users_api AS
SELECT 
    t.glpi_id AS ticket_id,
    u.id AS user_id,
    u.name AS user_name,
    u.realname AS user_realname,
    tu.type AS user_type,
    CASE tu.type
        WHEN 1 THEN 'Requester'
        WHEN 2 THEN 'Assigned'
        WHEN 3 THEN 'Observer'
        ELSE 'Unknown'
    END AS user_type_label
FROM dtic.tickets_users tu
JOIN dtic.tickets t ON tu.ticket_id = t.id
JOIN dtic.glpi_users u ON tu.user_id = u.id;

COMMENT ON VIEW dtic.v_tickets_users_api IS 'Relacionamento Ticket-User com IDs corretos para API';

-- 3. View de Tickets com Groups para API
CREATE OR REPLACE VIEW dtic.v_tickets_groups_api AS
SELECT 
    t.glpi_id AS ticket_id,
    g.id AS group_id,
    g.name AS group_name,
    tg.type AS group_type,
    CASE tg.type
        WHEN 1 THEN 'Requester'
        WHEN 2 THEN 'Assigned'
        ELSE 'Unknown'
    END AS group_type_label
FROM dtic.tickets_groups tg
JOIN dtic.tickets t ON tg.ticket_id = t.id
JOIN dtic.glpi_groups g ON tg.group_id = g.id;

COMMENT ON VIEW dtic.v_tickets_groups_api IS 'Relacionamento Ticket-Group com IDs corretos para API';

-- 4. View Completa: Ticket + Todos Atores
CREATE OR REPLACE VIEW dtic.v_tickets_full_api AS
SELECT 
    t.glpi_id AS ticket_id,
    t.titulo,
    t.status_id,
    t.prioridade_id,
    -- Aggregar usuários
    (
        SELECT json_agg(json_build_object(
            'user_id', u.id,
            'name', u.name,
            'type', tu.type
        ))
        FROM dtic.tickets_users tu
        JOIN dtic.glpi_users u ON tu.user_id = u.id
        WHERE tu.ticket_id = t.id
    ) AS users,
    -- Aggregar grupos
    (
        SELECT json_agg(json_build_object(
            'group_id', g.id,
            'name', g.name,
            'type', tg.type
        ))
        FROM dtic.tickets_groups tg
        JOIN dtic.glpi_groups g ON tg.group_id = g.id
        WHERE tg.ticket_id = t.id
    ) AS groups
FROM dtic.tickets t;

COMMENT ON VIEW dtic.v_tickets_full_api IS 'Tickets completos com atores agregados - IDs prontos para API';
