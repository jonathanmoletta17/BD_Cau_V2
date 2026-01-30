"""
GLPI Data Service V3 - Dashboard Service Layer
Business logic for dashboard queries using SQLAlchemy
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, case

from ..metadata.models import User, Entity, ITILCategory, Group
from ..tickets.models import Ticket
from ..tickets.relationship_models import TicketUser, TicketChange, TicketGroup


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO date string to datetime object."""
    if not date_str:
        return None
    try:
        # Try parsing ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt
    except (ValueError, AttributeError):
        return None





def get_entity_ranking(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> List[dict]:
    """
    Get entity ranking by ticket count.
    
    Args:
        db: Database session
        inicio: Start date (ISO format, optional)
        fim: End date (ISO format, optional)
    
    Returns:
        List of dicts with entity_name and ticket_count
    """
    # Parse dates
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)

    # Adjust end date to include the entire day
    if fim_dt and fim_dt.hour == 0 and fim_dt.minute == 0 and fim_dt.second == 0:
        fim_dt = fim_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Query with join
    query = db.query(
        func.coalesce(Entity.completename, Entity.name, 'Sem Entidade').label('entity_name'),
        func.count(Ticket.id).label('ticket_count')
    ).outerjoin(Entity, Ticket.entidade_id == Entity.id) \
     .filter(Ticket.is_deleted == False)
    
    # Apply date filters
    if inicio_dt:
        query = query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.criado_em <= fim_dt)
    
    # Group and order
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
    """
    Get category ranking by ticket count.
    
    Args:
        db: Database session
        inicio: Start date (ISO format, optional)
        fim: End date (ISO format, optional)
    
    Returns:
        List of dicts with category_name and ticket_count
    """
    # Parse dates
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)

    # Adjust end date to include the entire day
    if fim_dt and fim_dt.hour == 0 and fim_dt.minute == 0 and fim_dt.second == 0:
        fim_dt = fim_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Query with join
    query = db.query(
        func.coalesce(ITILCategory.completename, ITILCategory.name, 'Sem Categoria').label('category_name'),
        func.count(Ticket.id).label('ticket_count')
    ).outerjoin(ITILCategory, Ticket.categoria_id == ITILCategory.id) \
     .filter(Ticket.is_deleted == False)
    
    # Apply date filters
    if inicio_dt:
        query = query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.criado_em <= fim_dt)
    
    # Group and order
    results = query.group_by(ITILCategory.id, ITILCategory.completename, ITILCategory.name) \
                   .order_by(func.count(Ticket.id).desc()) \
                   .all()
    
    return [
        {"category_name": row.category_name, "ticket_count": row.ticket_count}
        for row in results
    ]


def get_new_tickets(
    db: Session
) -> List[dict]:
    """
    Get all new tickets with details.
    
    Args:
        db: Database session
    
    Returns:
        List of dicts with id, titulo, solicitante, data, entidade, prioridade
    """
    # Subquery to get requester (type=1) for each ticket
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
    
    # Main query
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
    
    # Priority mapping
    priority_map = {
        5: "Muito Alta",
        4: "Alta",
        3: "Média",
        2: "Baixa",
        1: "Muito Baixa"
    }
    
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
    """
    Get technician ranking by assigned ticket count.
    
    Args:
        db: Database session
        inicio: Start date (ISO format, optional)
        fim: End date (ISO format, optional)
    
    Returns:
        List of dicts with tecnico and tickets count
    """
    # Parse dates
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    # Adjust end date to include the entire day
    if fim_dt and fim_dt.hour == 0 and fim_dt.minute == 0 and fim_dt.second == 0:
        fim_dt = fim_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Query: Count RESOLVED tickets by Technician within the period
    # Filter by Solved (5) or Closed (6) status
    # Date filter applies to 'solucionado_em' (Resolution Date)
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
     .filter(Ticket.is_deleted == False) \
     .filter(or_(Ticket.status_id == 5, Ticket.status_id == 6))  # Only Resolved/Closed
    
    # Apply date filters on Resolution Date
    if inicio_dt:
        query = query.filter(Ticket.solucionado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.solucionado_em <= fim_dt)
    
    # Group and order
    results = query.group_by(User.id, User.realname, User.firstname, User.name) \
                   .order_by(func.count(TicketUser.ticket_id).desc()) \
                   .all()
    
    return [
        {"tecnico": row.tecnico, "tickets": row.tickets}
        for row in results
    ]


def get_general_stats(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> dict:
    """
    Get general ticket statistics by status using optimized aggregation.
    
    Args:
        db: Database session
        inicio: Start date (ISO format, optional)
        fim: End date (ISO format, optional)
    
    Returns:
        Dict with counts: novos, em_progresso, pendentes, resolvidos
    """
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    # Adjust end date to include the entire day
    if fim_dt and fim_dt.hour == 0 and fim_dt.minute == 0 and fim_dt.second == 0:
        fim_dt = fim_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # 1. Total "Novos" (Always ignoring date filter, shows backlog)
    novos = db.query(func.count(Ticket.id)).filter(
        Ticket.is_deleted == False,
        Ticket.status_id == 1
    ).scalar() or 0
    
    # 2. Aggregated Status Counts (With Date Filter)
    # Group by status_id to get all other stats in one query
    query = db.query(Ticket.status_id, func.count(Ticket.id))\
        .filter(Ticket.is_deleted == False)
    
    if inicio_dt:
        query = query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.criado_em <= fim_dt)
        
    # Exclude status 1 (Novos) as it's handled separately
    query = query.filter(Ticket.status_id != 1)
    
    status_counts = dict(query.group_by(Ticket.status_id).all())
    
    # Helper to safely get counts
    def get_count(status_id):
        return status_counts.get(status_id, 0)
    
    # Map status IDs to metrics
    # Status ID 2 = Em Atendimento (Processing)
    # Status ID 3 = Planejado (Planned)
    # Status ID 4 = Pendente (Pending)
    # Status ID 5 = Solucionado (Solved)
    # Status ID 6 = Fechado (Closed)
    
    em_progresso = get_count(2) + get_count(3)
    pendentes = get_count(4)
    resolvidos = get_count(5) + get_count(6)

    return {
        "novos": novos,
        "em_progresso": em_progresso,
        "pendentes": pendentes,
        "resolvidos": resolvidos
    }




def get_level_stats(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> dict:
    """
    Get ticket statistics by Support Level (N1-N4) using optimized aggregation.
    
    Group mapping (from database):
    - N1: Group ID 89
    - N2: Group ID 90
    - N3: Group ID 91
    - N4: Group ID 92
    
    Status mapping:
    - novos: status_id = 1
    - em_progresso: status_id = 2
    - pendentes: status_id = 4
    - resolvidos: status_id = 5 or 6
    """
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)

    # Adjust end date to include the entire day
    if fim_dt and fim_dt.hour == 0 and fim_dt.minute == 0 and fim_dt.second == 0:
        fim_dt = fim_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # IDs of interest
    target_groups = [89, 90, 91, 92]
    
    # Optimized Query:
    # Select GroupID, StatusID, Count(*)
    # Join Ticket -> TicketGroup
    # Filter by Group IDs and Date Range
    # Group By GroupID, StatusID
    query = db.query(TicketGroup.group_id, Ticket.status_id, func.count(Ticket.id))\
        .join(Ticket, Ticket.id == TicketGroup.ticket_id)\
        .filter(Ticket.is_deleted == False)\
        .filter(TicketGroup.type == 2)\
        .filter(TicketGroup.group_id.in_(target_groups))
        
    if inicio_dt:
        query = query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.criado_em <= fim_dt)
        
    results = query.group_by(TicketGroup.group_id, Ticket.status_id).all()
    
    # Process results into structured dict
    # Structure: {(group_id, status_id): count}
    data_map = {(r[0], r[1]): r[2] for r in results}
    
    def get_stats_for_group(group_id):
        def count(status_id):
            return data_map.get((group_id, status_id), 0)
            
        novos = count(1)
        em_progresso = count(2)
        pendentes = count(4)
        resolvidos = count(5) + count(6)
        total = novos + em_progresso + pendentes + resolvidos
        
        return {
            "novos": novos,
            "em_progresso": em_progresso,
            "pendentes": pendentes,
            "resolvidos": resolvidos,
            "total": total
        }

    return {
        "N1": get_stats_for_group(89),
        "N2": get_stats_for_group(90),
        "N3": get_stats_for_group(91),
        "N4": get_stats_for_group(92)
    }


def get_recent_activities(
    db: Session,
    limit: int = 10
) -> List[dict]:
    """
    Get recent ticket change activities.
    
    Args:
        db: Database session
        limit: Maximum number of activities to return
    
    Returns:
        List of dicts with action, tech, requester, time, and ticket id
    """
    try:
        # Get recent changes with ticket and user info
        query = db.query(
            TicketChange.glpi_id.label('change_id'),  # ID único da mudança
            TicketChange.data_mudanca,
            TicketChange.campo,
            TicketChange.usuario_nome,
            Ticket.glpi_id.label('ticket_id'),  # ID do ticket (para referência)
            Ticket.titulo
        ).join(Ticket, TicketChange.ticket_id == Ticket.id) \
         .filter(Ticket.is_deleted == False) \
         .order_by(TicketChange.data_mudanca.desc()) \
         .limit(limit)
        
        results = query.all()
        
        # Format activities
        activities = []
        for row in results:
            # Create a human-readable action description
            action = f"Atualizou {row.campo or 'ticket'}"
            tech = row.usuario_nome or "Sistema"
            time_str = row.data_mudanca.isoformat() if row.data_mudanca else ''
            
            activities.append({
                "action": action,
                "tech": tech,
                "requester": row.titulo[:50] if row.titulo else "",  # Use ticket title as context
                "time": time_str,
                "id": row.change_id  # ✅ ID ÚNICO da mudança (não do ticket)
            })
        
        return activities
    except Exception:
        # If no ticket_changes data or any error, return empty list
        return []

