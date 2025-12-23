"""
GLPI Quality Monitoring - Top 5 Priority Rules
Phase 2: Dashboard-only notifications
"""

QUALITY_RULES = {
    'R01': {
        'name': 'Ticket Novo > 24h',
        'severity': 'HIGH',
        'description': 'Ticket com status Novo sem atribuição por mais de 24 horas',
        'query': """
            SELECT 
                t.id,
                t.glpi_id,
                t.titulo,
                t.status_id,
                t.criado_em,
                EXTRACT(EPOCH FROM (NOW() - t.criado_em))/3600 as hours_elapsed,
                COALESCE(u_req.name, 'N/A') as solicitante,
                COALESCE(e.name, 'N/A') as entidade
            FROM dtic.tickets t
            LEFT JOIN dtic.tickets_users tu_req ON t.id = tu_req.ticket_id AND tu_req.type = 1
            LEFT JOIN dtic.glpi_users u_req ON tu_req.user_id = u_req.id
            LEFT JOIN dtic.glpi_entities e ON t.entidade_id = e.id
            WHERE t.status_id = 1
              AND t.criado_em < NOW() - INTERVAL '24 hours'
              AND t.is_deleted = FALSE
            ORDER BY t.criado_em
        """,
        'channels': ['dashboard'],
        'threshold': 5,  # Alert if > 5 tickets
        'action': 'Atribuir técnico/grupo ou fechar tickets órfãos'
    },
    
    'R03': {
        'name': 'Ticket Ativo sem Técnico',
        'severity': 'HIGH',
        'description': 'Tickets em atendimento, planejado ou pendente sem técnico atribuído',
        'query': """
            SELECT 
                t.id,
                t.glpi_id,
                t.titulo,
                CASE t.status_id
                    WHEN 2 THEN 'Em Atendimento'
                    WHEN 3 THEN 'Planejado'
                    WHEN 4 THEN 'Pendente'
                END as status_nome,
                t.status_id,
                t.criado_em,
                COALESCE(g.name, 'Sem Grupo') as grupo,
                COALESCE(e.name, 'N/A') as entidade
            FROM dtic.tickets t
            LEFT JOIN dtic.tickets_users tu ON t.id = tu.ticket_id AND tu.type = 2
            LEFT JOIN dtic.tickets_groups tg ON t.id = tg.ticket_id AND tg.type = 2
            LEFT JOIN dtic.glpi_groups g ON tg.group_id = g.id
            LEFT JOIN dtic.glpi_entities e ON t.entidade_id = e.id
            WHERE t.status_id IN (2, 3, 4)
              AND tu.user_id IS NULL
              AND t.is_deleted = FALSE
            ORDER BY t.criado_em
        """,
        'channels': ['dashboard'],
        'threshold': 3,
        'action': 'Atribuir técnico responsável ao ticket'
    },
    
    'R04': {
        'name': 'Ticket Sem Grupo',
        'severity': 'MEDIUM',
        'description': 'Tickets sem grupo de atendimento atribuído',
        'query': """
            SELECT 
                t.id,
                t.glpi_id,
                t.titulo,
                CASE t.status_id
                    WHEN 1 THEN 'Novo'
                    WHEN 2 THEN 'Em Atendimento'
                    WHEN 3 THEN 'Planejado'
                    WHEN 4 THEN 'Pendente'
                    WHEN 5 THEN 'Resolvido'
                    WHEN 6 THEN 'Fechado'
                END as status_nome,
                t.status_id,
                t.criado_em,
                COALESCE(c.completename, 'Sem Categoria') as categoria,
                COALESCE(e.name, 'N/A') as entidade
            FROM dtic.tickets t
            LEFT JOIN dtic.tickets_groups tg ON t.id = tg.ticket_id AND tg.type = 2
            LEFT JOIN dtic.glpi_itilcategories c ON t.categoria_id = c.id
            LEFT JOIN dtic.glpi_entities e ON t.entidade_id = e.id
            WHERE tg.group_id IS NULL
              AND t.status_id NOT IN (5, 6)  -- Exclude resolved/closed
              AND t.is_deleted = FALSE
            ORDER BY t.criado_em DESC
        """,
        'channels': ['dashboard'],
        'threshold': 10,
        'action': 'Atribuir grupo de suporte apropriado'
    },
    
    'R10': {
        'name': 'Ticket Pendente > 7 dias',
        'severity': 'MEDIUM',
        'description': 'Tickets com status Pendente há mais de 7 dias',
        'query': """
            SELECT 
                t.id,
                t.glpi_id,
                t.titulo,
                t.status_id,
                t.atualizado_em as ultimo_update,
                EXTRACT(EPOCH FROM (NOW() - t.atualizado_em))/86400 as days_pending,
                COALESCE(u_tech.name, 'Sem Técnico') as tecnico,
                COALESCE(g.name, 'Sem Grupo') as grupo
            FROM dtic.tickets t
            LEFT JOIN dtic.tickets_users tu ON t.id = tu.ticket_id AND tu.type = 2
            LEFT JOIN dtic.glpi_users u_tech ON tu.user_id = u_tech.id
            LEFT JOIN dtic.tickets_groups tg ON t.id = tg.ticket_id AND tg.type = 2
            LEFT JOIN dtic.glpi_groups g ON tg.group_id = g.id
            WHERE t.status_id = 4
              AND t.atualizado_em < NOW() - INTERVAL '7 days'
              AND t.is_deleted = FALSE
            ORDER BY t.atualizado_em
        """,
        'channels': ['dashboard'],
        'threshold': 5,
        'action': 'Retomar atendimento ou fechar ticket'
    },
    
    'R06': {
        'name': 'Status Alterado sem Followup',
        'severity': 'HIGH',
        'description': 'Mudança de status sem registro de followup recente',
        'query': """
            WITH last_status_change AS (
                SELECT 
                    tc.ticket_id,
                    MAX(tc.data_mudanca) as ultima_mudanca
                FROM dtic.ticket_changes tc
                WHERE tc.campo = 'status'
                  AND tc.data_mudanca > NOW() - INTERVAL '48 hours'
                GROUP BY tc.ticket_id
            )
            SELECT 
                t.id,
                t.glpi_id,
                t.titulo,
                t.status_id,
                lsc.ultima_mudanca,
                COALESCE(u_tech.name, 'Sem Técnico') as tecnico,
                (
                    SELECT COUNT(*) 
                    FROM dtic.ticket_followups f 
                    WHERE f.ticket_id = t.id 
                    AND f.date >= lsc.ultima_mudanca
                ) as followups_apos_mudanca
            FROM dtic.tickets t
            INNER JOIN last_status_change lsc ON t.id = lsc.ticket_id
            LEFT JOIN dtic.tickets_users tu ON t.id = tu.ticket_id AND tu.type = 2
            LEFT JOIN dtic.glpi_users u_tech ON tu.user_id = u_tech.id
            WHERE NOT EXISTS (
                SELECT 1 
                FROM dtic.ticket_followups f 
                WHERE f.ticket_id = t.id 
                  AND f.date >= lsc.ultima_mudanca - INTERVAL '1 hour'
            )
            AND t.is_deleted = FALSE
            ORDER BY lsc.ultima_mudanca DESC
        """,
        'channels': ['dashboard'],
        'threshold': 3,
        'action': 'Adicionar followup documentando a ação realizada'
    },

    'R13': {
        'name': 'Sem Interação > 72h',
        'severity': 'MEDIUM',
        'description': 'Ticket em atendimento sem nenhum followup há mais de 72 horas',
        'query': """
            SELECT 
                t.id,
                t.glpi_id,
                t.titulo,
                MAX(f.date) as ultimo_followup,
                COALESCE(u_tech.name, 'Sem Técnico') as tecnico
            FROM dtic.tickets t
            LEFT JOIN dtic.ticket_followups f ON t.id = f.ticket_id
            LEFT JOIN dtic.tickets_users tu ON t.id = tu.ticket_id AND tu.type = 2
            LEFT JOIN dtic.glpi_users u_tech ON tu.user_id = u_tech.id
            WHERE t.status_id = 2 -- Em Atendimento
              AND t.is_deleted = FALSE
            GROUP BY t.id, t.glpi_id, t.titulo, u_tech.name
            HAVING MAX(f.date) < NOW() - INTERVAL '72 hours' OR MAX(f.date) IS NULL
        """,
        'channels': ['dashboard'],
        'threshold': 5,
        'action': 'Postar followup de atualização para o usuário'
    },

    'R02': {
        'name': 'Novo com Técnico',
        'severity': 'MEDIUM',
        'description': 'Ticket com status Novo mas já possui técnico atribuído (deveria estar Em Atendimento)',
        'query': """
            SELECT 
                t.id,
                t.glpi_id,
                t.titulo,
                u_tech.name as tecnico_atribuido
            FROM dtic.tickets t
            JOIN dtic.tickets_users tu ON t.id = tu.ticket_id AND tu.type = 2
            JOIN dtic.glpi_users u_tech ON tu.user_id = u_tech.id
            WHERE t.status_id = 1
              AND t.is_deleted = FALSE
        """,
        'channels': ['dashboard'],
        'threshold': 3,
        'action': 'Alterar status para Em Atendimento'
    },

    'R05': {
        'name': 'Ticket Sem Categoria',
        'severity': 'MEDIUM',
        'description': 'Tickets ativos sem categoria ITIL definida',
        'query': """
            SELECT 
                t.id,
                t.glpi_id,
                t.titulo,
                COALESCE(u_tech.name, 'Sem Técnico') as tecnico
            FROM dtic.tickets t
            LEFT JOIN dtic.tickets_users tu ON t.id = tu.ticket_id AND tu.type = 2
            LEFT JOIN dtic.glpi_users u_tech ON tu.user_id = u_tech.id
            WHERE (t.categoria_id IS NULL OR t.categoria_id = 0)
              AND t.status_id NOT IN (5, 6)
              AND t.is_deleted = FALSE
        """,
        'channels': ['dashboard'],
        'threshold': 5,
        'action': 'Classificar corretamente a categoria do chamado'
    }
}

# Rule metadata for frontend display
RULE_METADATA = {
    'R01': {'icon': '⏰', 'color': '#ef4444'},  # red-500
    'R03': {'icon': '👤', 'color': '#ef4444'},
    'R04': {'icon': '👥', 'color': '#f59e0b'},  # amber-500
    'R10': {'icon': '⏸️', 'color': '#f59e0b'},
    'R06': {'icon': '📝', 'color': '#ef4444'}
}
