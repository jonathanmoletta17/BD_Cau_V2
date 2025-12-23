"""
GLPI Data Service V3 - SIS Dashboard Service Layer
Business logic for dashboard queries using SQLAlchemy
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, text

from ..metadata.models import User, Entity, ITILCategory
from ..tickets.models import Ticket
from ..tickets.relationship_models import TicketUser
from src.core.config import config

# Relationship models might be in tickets/models.py or tickets/relationship_models.py
# Check imports based on file existence. Assuming TicketUser is available via tickets.models or tickets.relationship_models
# In DTIC it was in tickets.models. Let's try that.

def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO date string to datetime object."""
    if not date_str:
        return None
    try:
        # Try parsing ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None



def _format_timeline_content(field: str, old_val: Optional[str], new_val: Optional[str]) -> str:
    """Format timeline changes into human-readable text."""
    # Ensure values are strings or empty
    s_old = str(old_val) if old_val is not None else ""
    s_new = str(new_val) if new_val is not None else ""
    
    # Mappings
    status_map = {
        '1': "Novo", '2': "Em Atendimento", '3': "Planejado", 
        '4': "Pendente", '5': "Solucionado", '6': "Fechado"
    }
    priority_map = {
        '5': "Muito Alta", '4': "Alta", '3': "Média", 
        '2': "Baixa", '1': "Muito Baixa"
    }
    bool_map = {'0': 'Não', '1': 'Sim'}
    
    formatted_old = s_old
    formatted_new = s_new

    if field == 'Status':
        formatted_old = status_map.get(s_old, s_old)
        formatted_new = status_map.get(s_new, s_new)
    elif field == 'Prioridade':
        formatted_old = priority_map.get(s_old, s_old)
        formatted_new = priority_map.get(s_new, s_new)
    elif field == 'Leve em conta o tempo':
        formatted_old = bool_map.get(s_old, s_old)
        formatted_new = bool_map.get(s_new, s_new)
        
    # Formatting
    if not s_old:
        return f"{field}: -> {formatted_new}"
    if not s_new:
        return f"{field}: {formatted_old} ->"
        
    return f"{field}: {formatted_old} -> {formatted_new}"


def get_general_stats(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> dict:
    """Get general ticket statistics by status."""
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    query = db.query(Ticket).filter(Ticket.is_deleted == False)
    
    if inicio_dt:
        query = query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.criado_em <= fim_dt)
    
    em_atendimento = query.filter(Ticket.status_id == 2).count()
    planejados = query.filter(Ticket.status_id == 3).count()
    pendentes = query.filter(Ticket.status_id == 4).count()
    resolvidos = query.filter(or_(Ticket.status_id == 5, Ticket.status_id == 6)).count()

    # "Novos" ignores date filter (backlog)
    novos = db.query(Ticket).filter(
        Ticket.is_deleted == False,
        Ticket.status_id == 1
    ).count()
    
    return {
        "novos": novos,
        "em_progresso": em_atendimento + planejados,
        "pendentes": pendentes,
        "resolvidos": resolvidos
    }


def get_entity_ranking(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> List[dict]:
    """Get entity ranking by ticket count."""
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    query = db.query(
        func.coalesce(Entity.completename, Entity.name, 'Sem Entidade').label('entity_name'),
        func.count(Ticket.id).label('ticket_count')
    ).outerjoin(Entity, Ticket.entidade_id == Entity.id) \
     .filter(Ticket.is_deleted == False)
    
    if inicio_dt:
        query = query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.criado_em <= fim_dt)
    
    results = query.group_by(Entity.id, Entity.completename, Entity.name) \
                   .order_by(func.count(Ticket.id).desc()) \
                   .all()
    
    return [
        {"entity_name": row.entity_name, "ticket_count": row.ticket_count}
        for row in results
    ]


def get_category_ranking(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> List[dict]:
    """Get category ranking by ticket count."""
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    query = db.query(
        func.coalesce(ITILCategory.completename, ITILCategory.name, 'Sem Categoria').label('category_name'),
        func.count(Ticket.id).label('ticket_count')
    ).outerjoin(ITILCategory, Ticket.categoria_id == ITILCategory.id) \
     .filter(Ticket.is_deleted == False)
    
    if inicio_dt:
        query = query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.criado_em <= fim_dt)
    
    results = query.group_by(ITILCategory.id, ITILCategory.completename, ITILCategory.name) \
                   .order_by(func.count(Ticket.id).desc()) \
                   .all()
    
    return [
        {"category_name": row.category_name, "ticket_count": row.ticket_count}
        for row in results
    ]


def get_ticket_history(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> List[dict]:
    """
    Get daily ticket history (created and resolved) for the date range.
    Returns list of {date: 'DD/MM', created: int, resolved: int}
    """
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    # Query for tickets created per day
    created_query = db.query(
        func.date(Ticket.criado_em).label('dia'),
        func.count(Ticket.id).label('criados')
    ).filter(Ticket.is_deleted == False)
    
    if inicio_dt:
        created_query = created_query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        created_query = created_query.filter(Ticket.criado_em <= fim_dt)
    
    created_results = created_query.group_by(func.date(Ticket.criado_em)).all()
    
    # Query for tickets resolved per day (status 5=Resolvido or 6=Fechado)
    resolved_query = db.query(
        func.date(Ticket.solucionado_em).label('dia'),
        func.count(Ticket.id).label('resolvidos')
    ).filter(
        Ticket.is_deleted == False,
        Ticket.solucionado_em.isnot(None),
        Ticket.status_id.in_([5, 6])  # Resolvido ou Fechado
    )
    
    if inicio_dt:
        resolved_query = resolved_query.filter(Ticket.solucionado_em >= inicio_dt)
    if fim_dt:
        resolved_query = resolved_query.filter(Ticket.solucionado_em <= fim_dt)
    
    resolved_results = resolved_query.group_by(func.date(Ticket.solucionado_em)).all()
    
    # Combine results into a dict by date
    daily_stats = {}
    
    for row in created_results:
        date_str = row.dia.strftime('%d/%m') if row.dia else 'N/A'
        daily_stats[date_str] = {'date': date_str, 'created': row.criados, 'resolved': 0}
    
    for row in resolved_results:
        date_str = row.dia.strftime('%d/%m') if row.dia else 'N/A'
        if date_str in daily_stats:
            daily_stats[date_str]['resolved'] = row.resolvidos
        else:
            daily_stats[date_str] = {'date': date_str, 'created': 0, 'resolved': row.resolvidos}
    
    # Sort by date and return as list
    sorted_results = sorted(daily_stats.values(), key=lambda x: x['date'])
    
    return sorted_results


def get_support_levels(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> List[dict]:
    """
    Get distribution of tickets by support level (N1, N2, N3, N4).
    Groups tickets by assigned group's level, only counting resolved/closed tickets.
    """
    from ..metadata.models import Group
    from ..tickets.relationship_models import TicketGroup
    
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    # Query tickets with group assignment and level
    query = db.query(
        func.coalesce(Group.name, 'Sem Nível').label('nivel'),
        func.count(Ticket.id).label('total')
    ).select_from(Ticket) \
     .outerjoin(TicketGroup, Ticket.id == TicketGroup.ticket_id) \
     .outerjoin(Group, TicketGroup.group_id == Group.id) \
     .filter(
        Ticket.is_deleted == False,
        Ticket.status_id.in_([5, 6]),  # Only resolved/closed
        TicketGroup.type == 2  # Type 2 = assigned group
    )
    
    if inicio_dt:
        query = query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.criado_em <= fim_dt)
    
    results = query.group_by(Group.name) \
                   .order_by(Group.name) \
                   .all()
    
    # Map group names to N1-N4 levels
    # This assumes group names contain "N1", "N2", "N3", "N4" or similar
    level_map = {}
    for row in results:
        group_name = row.nivel
        
        # Try to extract level from group name
        if 'N1' in group_name.upper() or 'NIVEL 1' in group_name.upper():
            nivel = 'N1'
        elif 'N2' in group_name.upper() or 'NIVEL 2' in group_name.upper():
            nivel = 'N2'
        elif 'N3' in group_name.upper() or 'NIVEL 3' in group_name.upper():
            nivel = 'N3'
        elif 'N4' in group_name.upper() or 'NIVEL 4' in group_name.upper():
            nivel = 'N4'
        else:
            nivel = 'Sem Nível'
        
        # Aggregate by level
        if nivel not in level_map:
            level_map[nivel] = 0
        level_map[nivel] += row.total
    
    # Return as list
    return [
        {"nivel": nivel, "total": total}
        for nivel, total in sorted(level_map.items())
    ]


def get_new_tickets(db: Session) -> List[dict]:
    """Get all new tickets with details."""
    # Subquery for requester
    requester_subq = db.query(
        TicketUser.ticket_id,
        func.coalesce(
            func.concat(User.realname, ' ', User.firstname),
            User.name,
            'Desconhecido'
        ).label('solicitante')
    ).join(User, TicketUser.user_id == User.id) \
     .filter(TicketUser.type == 1) \
     .distinct(TicketUser.ticket_id) \
     .subquery()
    
    query = db.query(
        Ticket.glpi_id.label('id'),
        Ticket.titulo,
        func.coalesce(requester_subq.c.solicitante, 'Desconhecido').label('solicitante'),
        Ticket.criado_em,
        func.coalesce(Entity.name, 'Sem Entidade').label('entidade'),
        Ticket.prioridade_id
    ).outerjoin(Entity, Ticket.entidade_id == Entity.id) \
     .outerjoin(requester_subq, Ticket.id == requester_subq.c.ticket_id) \
     .filter(Ticket.is_deleted == False) \
     .filter(Ticket.status_id == 1) \
     .order_by(Ticket.criado_em.desc())
    
    results = query.all()
    
    priority_map = {5: "Muito Alta", 4: "Alta", 3: "MÃ©dia", 2: "Baixa", 1: "Muito Baixa"}
    
    return [
        {
            "id": row.id,
            "titulo": row.titulo,
            "solicitante": row.solicitante,
            "data": row.criado_em.isoformat() if row.criado_em else '',
            "entidade": row.entidade,
            "prioridade": priority_map.get(row.prioridade_id, "Normal")
        }
        for row in results
    ]


def get_technician_ranking(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> List[dict]:
    """Get technician ranking by assigned ticket count."""
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    query = db.query(
        func.coalesce(
            func.concat(User.realname, ' ', User.firstname),
            User.name,
            'Desconhecido'
        ).label('tecnico'),
        func.count(TicketUser.ticket_id).label('tickets')
    ).join(User, TicketUser.user_id == User.id) \
     .join(Ticket, TicketUser.ticket_id == Ticket.id) \
     .filter(TicketUser.type == 2) \
     .filter(Ticket.is_deleted == False)
    
    if inicio_dt:
        query = query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.criado_em <= fim_dt)
    
    results = query.group_by(User.id, User.realname, User.firstname, User.name) \
                   .order_by(func.count(TicketUser.ticket_id).desc()) \
                   .all()
    
    return [
        {"tecnico": row.tecnico, "tickets": row.tickets}
        for row in results
    ]


def get_chargers_data(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> List[dict]:
    """
    Get chargers data including status, current ticket, and history.
    
    Args:
        db: Database session
        inicio: Start date (YYYY-MM-DD)
        fim: End date (YYYY-MM-DD)
        
    Returns:
        List of chargers with their details
    """
    from sqlalchemy import text
    
    # Validate dates
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    if not inicio_dt or not fim_dt:
        # Default to current month if not provided
        now = datetime.now()
        if not inicio_dt:
            inicio_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not fim_dt:
            fim_dt = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # SQL Query using CTEs for clarity and performance
    # Using specific table names based on confirmed schema
    query = text("""
        WITH active_tickets AS (
            -- Ticket ativo (nÃ£o fechado/solucionado) vinculado ao carregador
            SELECT DISTINCT ON (ct.items_id)
                ct.items_id as charger_id,
                t.glpi_id as ticket_id,
                t.titulo as ticket_name,
                t.criado_em as ticket_date,
                t.status_id as status
            FROM glpi_items_tickets ct
            INNER JOIN tickets t ON ct.tickets_id = t.glpi_id
            WHERE ct.itemtype = 'PluginGenericobjectCarregador'
                AND t.status_id NOT IN (5, 6) -- 5=SOLUCIONADO, 6=FECHADO
                AND t.is_deleted = false
            ORDER BY ct.items_id, t.criado_em DESC
        ),
        last_closed AS (
            -- Ãltimo ticket fechado do carregador
            SELECT DISTINCT ON (ct.items_id)
                ct.items_id as charger_id,
                t.glpi_id as ticket_id,
                t.titulo as ticket_name,
                t.criado_em as ticket_date,
                t.status_id as status,
                t.solucionado_em as ticket_solvedate
            FROM glpi_items_tickets ct
            INNER JOIN tickets t ON ct.tickets_id = t.glpi_id
            WHERE ct.itemtype = 'PluginGenericobjectCarregador'
                AND t.status_id IN (5, 6)
                AND t.is_deleted = false
            ORDER BY ct.items_id, t.solucionado_em DESC
        ),
        ticket_count AS (
            -- Total de tickets no perÃ­odo por carregador
            SELECT 
                ct.items_id as charger_id,
                COUNT(DISTINCT ct.tickets_id) as total_tickets
            FROM glpi_items_tickets ct
            INNER JOIN tickets t ON ct.tickets_id = t.glpi_id
            WHERE ct.itemtype = 'PluginGenericobjectCarregador'
                AND t.criado_em >= :inicio
                AND t.criado_em <= :fim
                AND t.is_deleted = false
            GROUP BY ct.items_id
        )
        SELECT 
            c.id,
            c.name,
            c.entities_id,
            c.is_deleted,
            -- Ticket ativo
            at.ticket_id as current_ticket_id,
            at.ticket_name as current_ticket_name,
            at.ticket_date as current_ticket_date,
            at.status as current_ticket_status,
            -- Ãltimo ticket fechado
            lc.ticket_id as last_ticket_id,
            lc.ticket_name as last_ticket_name,
            lc.ticket_date as last_ticket_date,
            lc.status as last_ticket_status,
            lc.ticket_solvedate as last_ticket_solvedate,
            -- Contagem no perÃ­odo
            COALESCE(tc.total_tickets, 0) as total_tickets_in_period
        FROM glpi_plugin_genericobject_carregadors c
        LEFT JOIN active_tickets at ON c.id = at.charger_id
        LEFT JOIN last_closed lc ON c.id = lc.charger_id
        LEFT JOIN ticket_count tc ON c.id = tc.charger_id
        ORDER BY c.name;
    """)
    
    result = db.execute(query, {"inicio": inicio_dt, "fim": fim_dt})
    
    rows = result.fetchall()
    chargers = []
    
    # Status is already int from DB (1-6)
    # No need for string map, but we can have a fallback
    
    for row in rows:
        charger = {
            "id": row.id,
            "name": row.name,
            "entities_id": row.entities_id if hasattr(row, 'entities_id') else 1,
            "is_deleted": row.is_deleted,
            "totalTicketsInPeriod": row.total_tickets_in_period
        }
        
        if row.current_ticket_id:
            charger["currentTicket"] = {
                "id": row.current_ticket_id,
                "name": row.current_ticket_name,
                "date": row.current_ticket_date.isoformat() if row.current_ticket_date else None,
                "status": row.current_ticket_status
            }
            
        if row.last_ticket_id:
            charger["lastTicket"] = {
                "id": row.last_ticket_id,
                "name": row.last_ticket_name,
                "date": row.last_ticket_date.isoformat() if row.last_ticket_date else None,
                "status": row.last_ticket_status,
                "solvedate": row.last_ticket_solvedate.isoformat() if row.last_ticket_solvedate else None
            }
            
        chargers.append(charger)
        
    return chargers

def get_technician_details(db: Session, tech_id: int):
    """Retorna detalhes do técnico e estatísticas."""
    query = text("""
        SELECT
            u.name as tech_name,
            COUNT(t.id) as total_tickets,
            COUNT(CASE WHEN t.status_id IN (5, 6) THEN 1 END) as resolved_tickets,
            AVG(CASE WHEN t.status_id IN (5, 6) THEN EXTRACT(EPOCH FROM (t.solucionado_em - t.criado_em))/3600 END) as avg_resolution_time
        FROM glpi_users u
        LEFT JOIN tickets_users tu ON u.id = tu.user_id AND tu.type = 2
        LEFT JOIN tickets t ON tu.ticket_id = t.id
        WHERE u.id = :tech_id
        GROUP BY u.name
    """)
    result = db.execute(query, {"tech_id": tech_id}).fetchone()
    
    if not result:
        return None
        
    return {
        "id": tech_id,
        "name": result.tech_name,
        "stats": {
            "total_tickets": result.total_tickets,
            "resolved_tickets": result.resolved_tickets,
            "avg_resolution_time_hours": round(result.avg_resolution_time or 0, 2),
            "satisfaction_rate": None
        }
    }

def get_ticket_details(db: Session, ticket_id: int):
    """Retorna detalhes do ticket e timeline."""
    # 1. Basic Info
    ticket_query = text("""
        SELECT 
            t.id, t.glpi_id, t.titulo, t.descricao as description, 
            t.status_id, t.prioridade_id, t.criado_em, t.solucionado_em,
            u_req.name as requester_name,
            u_tech.name as technician_name
        FROM tickets t
        LEFT JOIN tickets_users tu_req ON t.id = tu_req.ticket_id AND tu_req.type = 1
        LEFT JOIN glpi_users u_req ON tu_req.user_id = u_req.id
        LEFT JOIN tickets_users tu_tech ON t.id = tu_tech.ticket_id AND tu_tech.type = 2
        LEFT JOIN glpi_users u_tech ON tu_tech.user_id = u_tech.id
        WHERE t.glpi_id = :ticket_id
    """)
    
    ticket = db.execute(ticket_query, {"ticket_id": ticket_id}).fetchone()
    if not ticket:
        return None
        
    # 2. Timeline
    # 2. Timeline
    timeline_query = text("""
        SELECT 
            'change' as type,
            c.id, 
            c.data_mudanca as date, 
            c.campo, c.valor_antigo, c.valor_novo,
            u.name as author
        FROM ticket_changes c
        LEFT JOIN glpi_users u ON c.usuario_id = u.id
        JOIN tickets t ON c.ticket_id = t.id
        WHERE t.glpi_id = :ticket_id
        AND (
            (c.valor_antigo IS NOT NULL AND c.valor_antigo != '')
            OR
            (c.valor_novo IS NOT NULL AND c.valor_novo != '')
        )
        AND c.campo != 'Alteração de Sistema'
        
        ORDER BY date DESC
    """)
    
    timeline_rows = []
    try:
        timeline_rows = db.execute(timeline_query, {"ticket_id": ticket_id}).fetchall()
    except Exception as e:
        print(f"Error fetching timeline: {e}")
    
    timeline = []
    for row in timeline_rows:
        timeline.append({
            "id": row.id,
            "date": row.date.isoformat() if row.date else "",
            "type": row.type,
            "author": row.author or "Sistema",
            "content": _format_timeline_content(row.campo, row.valor_antigo, row.valor_novo)
        })
        
    status_map = {1: "Novo", 2: "Em Atendimento", 3: "Planejado", 4: "Pendente", 5: "Solucionado", 6: "Fechado"}
    priority_map = {5: "Muito Alta", 4: "Alta", 3: "Média", 2: "Baixa", 1: "Muito Baixa"}
    
    # Generate Ticket URL
    # Config URL normally ends with /apirest.php, so we strip it to get base
    base_url = config.GLPI_DTIC_URL.replace('/apirest.php', '')
    # Default to # if config is missing
    ticket_url = f"{base_url}/front/ticket.form.php?id={ticket.glpi_id}" if base_url else "#"

    return {
        "id": ticket.id,
        "glpi_id": ticket.glpi_id,
        "title": ticket.titulo,
        "description": ticket.description,
        "status": status_map.get(ticket.status_id, str(ticket.status_id)),
        "priority": priority_map.get(ticket.prioridade_id, "Normal"),
        "creation_date": ticket.criado_em.isoformat() if ticket.criado_em else "",
        "solve_date": ticket.solucionado_em.isoformat() if ticket.solucionado_em else None,
        "requester": ticket.requester_name or "N/A",
        "technician": ticket.technician_name or "N/A",
        "timeline": timeline,
        "url": ticket_url
    }
