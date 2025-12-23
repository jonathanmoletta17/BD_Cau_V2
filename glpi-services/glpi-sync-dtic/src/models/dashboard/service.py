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
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def get_general_stats(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> dict:
    """
    Get general ticket statistics by status.
    
    Args:
        db: Database session
        inicio: Start date (ISO format, optional)
        fim: End date (ISO format, optional)
    
    Returns:
        Dict with counts: novos, em_atendimento, pendentes, planejados, resolvidos
    """
    # Parse dates
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    # Base query
    # Base query for date-filtered stats
    query = db.query(Ticket).filter(Ticket.is_deleted == False)
    
    # Apply date filters if provided
    if inicio_dt:
        query = query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.criado_em <= fim_dt)
    
    # Count by status (with date filter)
    em_atendimento = query.filter(Ticket.status_id == 2).count()
    planejados = query.filter(Ticket.status_id == 3).count()
    pendentes = query.filter(Ticket.status_id == 4).count()
    resolvidos = query.filter(or_(Ticket.status_id == 5, Ticket.status_id == 6)).count()

    # Special case for "Novos": Ignore date filters, show total backlog
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
    
    # Query
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
    
    # Apply date filters
    if inicio_dt:
        query = query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        query = query.filter(Ticket.criado_em <= fim_dt)
    
    # Group and order
    results = query.group_by(User.id, User.realname, User.firstname, User.name) \
                   .order_by(func.count(TicketUser.ticket_id).desc()) \
                   .all()
    
    return [
        {"tecnico": row.tecnico, "tickets": row.tickets}
        for row in results
    ]


def get_level_stats(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> dict:
    """
    Get ticket statistics by Support Level (N1-N4) based on Assigned Group.
    
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
    
    Args:
        db: Database session
        inicio: Start date (ISO format, optional)
        fim: End date (ISO format, optional)
    
    Returns:
        Dict with N1-N4 keys, each containing status counts and total
    """
    # Parse dates
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    # Base query for Tickets
    # We need to join with TicketGroup to filter by assigned group
    base_query = db.query(Ticket).join(TicketGroup, Ticket.id == TicketGroup.ticket_id) \
                   .filter(Ticket.is_deleted == False) \
                   .filter(TicketGroup.type == 2)  # Type 2 = Assigned Group
    
    # Apply date filters
    if inicio_dt:
        base_query = base_query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        base_query = base_query.filter(Ticket.criado_em <= fim_dt)
    
    # Helper function to count tickets by status for a specific group ID
    def count_by_group(group_id):
        # Filter by specific group ID
        filtered_query = base_query.filter(TicketGroup.group_id == group_id)
        
        novos = filtered_query.filter(Ticket.status_id == 1).count()
        em_progresso = filtered_query.filter(Ticket.status_id == 2).count()
        pendentes = filtered_query.filter(Ticket.status_id == 4).count()
        resolvidos = filtered_query.filter(or_(Ticket.status_id == 5, Ticket.status_id == 6)).count()
        total = novos + em_progresso + pendentes + resolvidos
        
        return {
            "novos": novos,
            "em_progresso": em_progresso,
            "pendentes": pendentes,
            "resolvidos": resolvidos,
            "total": total
        }
    
    # Calculate stats for each level (Group IDs 89, 90, 91, 92)
    return {
        "N1": count_by_group(89),
        "N2": count_by_group(90),
        "N3": count_by_group(91),
        "N4": count_by_group(92)
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

