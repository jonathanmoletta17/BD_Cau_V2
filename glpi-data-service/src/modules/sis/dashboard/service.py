"""
GLPI Data Service V3 - SIS Dashboard Service Layer
Business logic for dashboard queries using SQLAlchemy
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from ..metadata.models import User, Entity, ITILCategory
from ..tickets.models import Ticket
from ..tickets.relationship_models import TicketUser

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
    
    priority_map = {5: "Muito Alta", 4: "Alta", 3: "Média", 2: "Baixa", 1: "Muito Baixa"}
    
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
