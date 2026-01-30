"""
SIS Smart Search Service - FIXED VERSION
Correção: Removido DISTINCT() problemático, simplificado subqueries
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
    FIX: Removido DISTINCT() que causava perda de tickets
    """
    # Query principal COM LEFT JOINs diretos (sem subqueries problemáticas)
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
        # Requester fields
        func.max(func.case(
            (TicketUser.type == 1, User.id)
        )).label('requester_id'),
        func.max(func.case(
            (TicketUser.type == 1, User.name)
        )).label('requester_username'),
        func.max(func.case(
            (TicketUser.type == 1, func.coalesce(
                func.concat(User.realname, ' ', User.firstname),
                User.name
            ))
        )).label('requester_name'),
        # Technician fields
        func.max(func.case(
            (TicketUser.type == 2, User.id)
        )).label('technician_id'),
        func.max(func.case(
            (TicketUser.type == 2, User.name)
        )).label('technician_username'),
        func.max(func.case(
            (TicketUser.type == 2, func.coalesce(
                func.concat(User.realname, ' ', User.firstname),
                User.name
            ))
        )).label('technician_name'),
        # Group fields
        func.max(func.case(
            (TicketGroup.type == 2, Group.id)
        )).label('group_id'),
        func.max(func.case(
            (TicketGroup.type == 2, Group.name)
        )).label('group_name')
    ).outerjoin(Entity, Ticket.entidade_id == Entity.id) \
     .outerjoin(ITILCategory, Ticket.categoria_id == ITILCategory.id) \
     .outerjoin(TicketUser, Ticket.id == TicketUser.ticket_id) \
     .outerjoin(User, TicketUser.user_id == User.id) \
     .outerjoin(TicketGroup, Ticket.id == TicketGroup.ticket_id) \
     .outerjoin(Group, TicketGroup.group_id == Group.id) \
     .filter(Ticket.is_deleted == False) \
     .group_by(
         Ticket.id,
         Ticket.glpi_id,
         Ticket.titulo,
         Ticket.descricao,
         Ticket.criado_em,
         Ticket.atualizado_em,
         Ticket.status_id,
         Ticket.entidade_id,
         Entity.name,
         Ticket.categoria_id,
         ITILCategory.completename,
         ITILCategory.name
     )
    
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
                func.lower(ITILCategory.name).like(search_term)
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
