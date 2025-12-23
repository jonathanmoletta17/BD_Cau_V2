"""
GLPI Data Service V3 - Search Service
Business logic for smart search
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, aliased
from sqlalchemy import or_, and_, func, desc, distinct

from src.modules.dtic.tickets.models import Ticket
from src.modules.dtic.tickets.relationship_models import TicketUser, TicketGroup
from src.modules.dtic.metadata.models import Entity, ITILCategory, User, Location
from .models import SearchItem, SearchResponse, StatsResponse, StatItem

# Mapeamento de Status GLPI
STATUS_MAP = {
    1: "Novo",
    2: "Em Atendimento (Atribuído)",
    3: "Em Atendimento (Planejado)",
    4: "Pendente",
    5: "Solucionado",
    6: "Fechado"
}

# Mapeamento de Prioridade GLPI
PRIORITY_MAP = {
    1: "Muito Baixa",
    2: "Baixa",
    3: "Média",
    4: "Alta",
    5: "Muito Alta",
    6: "Crítica"
}

def _apply_filters(query, filters: Dict[str, Any]):
    """Aplica filtros comuns à query."""
    
    # Filtro de Texto (Busca ampla)
    if filters.get('q'):
        term = f"%{filters['q']}%"
        query = query.filter(
            or_(
                Ticket.titulo.ilike(term),
                Ticket.descricao.ilike(term),
                # TODO: Adicionar busca por ID se for numérico
            )
        )
    
    # Filtro de Status
    if filters.get('status'):
        # Se for string separada por vírgula
        if isinstance(filters['status'], str):
            status_list = [int(s) for s in filters['status'].split(',') if s.isdigit()]
            if status_list:
                query = query.filter(Ticket.status_id.in_(status_list))
        elif isinstance(filters['status'], list):
            query = query.filter(Ticket.status_id.in_(filters['status']))

    # Filtro de Entidade
    if filters.get('entidade_id'):
        query = query.filter(Ticket.entidade_id == filters['entidade_id'])

    # Filtro de Data
    if filters.get('data_inicio'):
        query = query.filter(Ticket.criado_em >= filters['data_inicio'])
    
    if filters.get('data_fim'):
        query = query.filter(Ticket.criado_em <= filters['data_fim'])

    return query

def search_tickets(
    db: Session, 
    q: Optional[str] = None,
    status: Optional[str] = None,
    entidade_id: Optional[int] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
) -> Dict[str, Any]:
    """
    Busca tickets com filtros avançados.
    """
    filters = {
        'q': q,
        'status': status,
        'entidade_id': entidade_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    }

    # Aliases para joins
    RequesterUser = aliased(User)
    TechnicianUser = aliased(User)
    RequesterRel = aliased(TicketUser)
    TechnicianRel = aliased(TicketUser)

    # Query Base
    query = db.query(
        Ticket,
        Entity.name.label('entidade_name'),
        RequesterUser.name.label('requerente_name'),
        TechnicianUser.name.label('tecnico_name')
    ).join(
        Entity, Ticket.entidade_id == Entity.id, isouter=True
    ).join(
        RequesterRel, 
        and_(Ticket.id == RequesterRel.ticket_id, RequesterRel.type == 1), # 1 = Requerente
        isouter=True
    ).join(
        RequesterUser,
        RequesterRel.user_id == RequesterUser.id,
        isouter=True
    ).join(
        TechnicianRel,
        and_(Ticket.id == TechnicianRel.ticket_id, TechnicianRel.type == 2), # 2 = Técnico
        isouter=True
    ).join(
        TechnicianUser,
        TechnicianRel.user_id == TechnicianUser.id,
        isouter=True
    )

    # Aplica Filtros
    query = _apply_filters(query, filters)

    # Contagem Total (para paginação)
    # Usamos distinct(Ticket.id) para evitar duplicatas causadas pelos joins N:N se houver múltiplos atores
    # Mas aqui pegamos apenas o primeiro de cada tipo, então distinct é bom garantir
    total = query.distinct(Ticket.id).count()

    # Paginação e Ordenação
    query = query.order_by(desc(Ticket.criado_em))
    query = query.offset((page - 1) * per_page).limit(per_page)

    results = query.all()

    # Formata Resultados
    items = []
    seen_ids = set() # Evitar duplicatas se o join trouxer múltiplas linhas
    
    for row in results:
        ticket = row.Ticket
        if ticket.id in seen_ids:
            continue
        seen_ids.add(ticket.id)

        items.append(SearchItem(
            id=ticket.id,
            glpi_id=ticket.glpi_id,
            titulo=ticket.titulo,
            descricao=ticket.descricao,
            status_id=ticket.status_id,
            status_desc=STATUS_MAP.get(ticket.status_id, "Desconhecido"),
            prioridade_id=ticket.prioridade_id or 0,
            prioridade_desc=PRIORITY_MAP.get(ticket.prioridade_id, "Normal"),
            entidade=row.entidade_name or "N/A",
            data_criacao=ticket.criado_em,
            data_atualizacao=ticket.atualizado_em,
            requerente=row.requerente_name,
            tecnico=row.tecnico_name
        ))

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page
    }

def get_suggestions(db: Session, field: str, prefix: str) -> List[str]:
    """Retorna sugestões para autocomplete."""
    if not prefix or len(prefix) < 2:
        return []
    
    term = f"%{prefix}%"
    limit = 10

    if field == 'entidade':
        results = db.query(Entity.name).filter(Entity.name.ilike(term)).limit(limit).all()
        return [r[0] for r in results]
    
    elif field in ['requerente', 'tecnico']:
        results = db.query(User.name).filter(User.name.ilike(term)).limit(limit).all()
        return [r[0] for r in results]
    
    return []

def get_search_stats(
    db: Session, 
    q: Optional[str] = None,
    status: Optional[str] = None,
    entidade_id: Optional[int] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None
) -> Dict[str, Any]:
    """Retorna estatísticas baseadas na busca atual."""
    
    filters = {
        'q': q,
        'status': status,
        'entidade_id': entidade_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    }

    # Base Query para Stats
    base_query = db.query(Ticket)
    base_query = _apply_filters(base_query, filters)

    # Stats por Status
    status_counts = base_query.with_entities(
        Ticket.status_id, func.count(Ticket.id)
    ).group_by(Ticket.status_id).all()

    by_status = []
    for status_id, count in status_counts:
        by_status.append(StatItem(
            label=STATUS_MAP.get(status_id, f"Status {status_id}"),
            value=count
        ))

    # Stats por Prioridade
    priority_counts = base_query.with_entities(
        Ticket.prioridade_id, func.count(Ticket.id)
    ).group_by(Ticket.prioridade_id).all()

    by_priority = []
    for priority_id, count in priority_counts:
        if priority_id:
            by_priority.append(StatItem(
                label=PRIORITY_MAP.get(priority_id, f"Prioridade {priority_id}"),
                value=count
            ))

    total = base_query.count()

    return {
        "by_status": by_status,
        "by_priority": by_priority,
        "total": total
    }
