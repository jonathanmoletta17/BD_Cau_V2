"""
SIS Smart Search Service
Lógica de negócio para busca e métricas de tickets SIS
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, String
from src.modules.sis.tickets.models import Ticket
from src.modules.sis.tickets.relationship_models import TicketUser, TicketGroup
from src.modules.sis.metadata.models import Entity, ITILCategory, User, Group
from typing import Optional

def search_tickets(
    db: Session,
    search: Optional[str],
    status: Optional[int],
    skip: int,
    limit: int
):
    """
    Busca tickets com filtros de texto e status
    """
    # Subquery para Requester (type=1)
    requester_subq = db.query(
        TicketUser.ticket_id,
        User.id.label('user_id'),
        User.name.label('username'),
        func.coalesce(
            func.concat(User.realname, ' ', User.firstname),
            User.name,
            'Desconhecido'
        ).label('full_name')
    ).join(User, TicketUser.user_id == User.id) \
     .filter(TicketUser.type == 1) \
     .distinct(TicketUser.ticket_id) \
     .subquery()
    
    # Subquery para Technician (type=2)
    technician_subq = db.query(
        TicketUser.ticket_id,
        User.id.label('user_id'),
        User.name.label('username'),
        func.coalesce(
            func.concat(User.realname, ' ', User.firstname),
            User.name,
            'Desconhecido'
        ).label('full_name')
    ).join(User, TicketUser.user_id == User.id) \
     .filter(TicketUser.type == 2) \
     .distinct(TicketUser.ticket_id) \
     .subquery()
    
    # Subquery para Group (type=2)
    group_subq = db.query(
        TicketGroup.ticket_id,
        Group.id.label('group_id'),
        Group.name.label('group_name')
    ).join(Group, TicketGroup.group_id == Group.id) \
     .filter(TicketGroup.type == 2) \
     .distinct(TicketGroup.ticket_id) \
     .subquery()
    
    # Query principal
    query = db.query(
        Ticket.glpi_id.label('id'),
        Ticket.titulo.label('name'),
        Ticket.descricao.label('content'),
        Ticket.criado_em.label('date_creation'),
        Ticket.atualizado_em.label('date_mod'),
        Ticket.status_id.label('status'),
        Ticket.entidade_id,
        func.coalesce(Entity.name, 'Sem Entidade').label('entity_name'),
        Ticket.categoria_id,
        func.coalesce(ITILCategory.completename, ITILCategory.name).label('category_name'),
        requester_subq.c.user_id.label('requester_id'),
        requester_subq.c.username.label('requester_username'),
        requester_subq.c.full_name.label('requester_name'),
        technician_subq.c.user_id.label('technician_id'),
        technician_subq.c.username.label('technician_username'),
        technician_subq.c.full_name.label('technician_name'),
        group_subq.c.group_id,
        group_subq.c.group_name
    ).outerjoin(Entity, Ticket.entidade_id == Entity.id) \
     .outerjoin(ITILCategory, Ticket.categoria_id == ITILCategory.id) \
     .outerjoin(requester_subq, Ticket.id == requester_subq.c.ticket_id) \
     .outerjoin(technician_subq, Ticket.id == technician_subq.c.ticket_id) \
     .outerjoin(group_subq, Ticket.id == group_subq.c.ticket_id) \
     .filter(Ticket.is_deleted == False)
    
    # Filtro de status
    if status is not None:
        query = query.filter(Ticket.status_id == status)
    
    # Busca multi-campo
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Ticket.titulo).like(search_term),
                func.lower(Ticket.descricao).like(search_term),
                func.cast(Ticket.glpi_id, String).like(search_term),
                func.lower(Entity.name).like(search_term),
                func.lower(ITILCategory.name).like(search_term),
                func.lower(requester_subq.c.full_name).like(search_term)
            )
        )
    
    # Ordenar por data de criação (mais recentes primeiro)
    query = query.order_by(Ticket.criado_em.desc())
    
    # Paginação
    total = query.count()
    results = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "tickets": [{
            "id": row.id,
            "name": row.name,
            "content": row.content,
            "date_creation": row.date_creation.isoformat() if row.date_creation else None,
            "date_mod": row.date_mod.isoformat() if row.date_mod else None,
            "status": row.status,
            "entity": {
                "id": row.entidade_id,
                "name": row.entity_name
            } if row.entidade_id else None,
            "category": {
                "id": row.categoria_id,
                "name": row.category_name
            } if row.categoria_id else None,
            "requester": {
                "id": row.requester_id,
                "name": row.requester_name,
                "username": row.requester_username
            } if row.requester_id else None,
            "technician": {
                "id": row.technician_id,
                "name": row.technician_name,
                "username": row.technician_username
            } if row.technician_id else None,
            "group": {
                "id": row.group_id,
                "name": row.group_name
            } if row.group_id else None
        } for row in results]
    }

def get_kpi_metrics(db: Session):
    """
    Calcula métricas agregadas (KPIs) por status
    """
    # Agregação de tickets por status_id
    stats = db.query(
        Ticket.status_id,
        func.count(Ticket.id).label('count')
    ).filter(Ticket.is_deleted == False) \
     .group_by(Ticket.status_id).all()
    
    metrics = {
        "new": 0,
        "processing": 0,
        "planned": 0,
        "pending": 0,
        "resolved": 0
    }
    
    for status, count in stats:
        if status == 1:
            metrics["new"] = count
        elif status == 2:
            metrics["processing"] = count
        elif status == 3:
            metrics["planned"] = count
        elif status == 4:
            metrics["pending"] = count
        elif status in [5, 6]:  # SOLVED or CLOSED
            metrics["resolved"] += count
    
    return metrics
