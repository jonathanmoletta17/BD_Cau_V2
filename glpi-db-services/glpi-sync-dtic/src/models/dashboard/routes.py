"""
GLPI Data Service V3 - SIS Dashboard API Routes
FastAPI endpoints for SIS Dashboard
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from src.core.database import Database
from .models import (
    MaintenanceGeneralStats,
    EntityRankingItem,
    CategoryRankingItem,
    HistoryDayItem,
    SupportLevelItem,
    MaintenanceNewTicketItem,
    TechnicianRankingItem,
    TechnicianDetail,
    TicketDetail
)
from .service import (
    get_general_stats,
    get_entity_ranking,
    get_category_ranking,
    get_ticket_history,
    get_support_levels,
    get_new_tickets,
    get_technician_ranking,
    get_chargers_data,
    get_technician_details,
    get_ticket_details
)

# Create router with prefix matching frontend expectations
# Frontend calls: /api/v1/sis/dashboard/stats-gerais
# Main app mounts at /api/v1
# So prefix here is /sis/dashboard
router = APIRouter(tags=["DTIC Dashboard"])


def get_db_session():
    """Dependency injection for DTIC database session."""
    session = Database.get_session(schema="dtic")
    try:
        yield session
    finally:
        session.close()


@router.get("/dashboard/stats-gerais", response_model=MaintenanceGeneralStats)
async def stats_gerais(
    inicio: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    fim: Optional[str] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db_session)
):
    """Retorna estatísticas gerais de tickets por status."""
    try:
        result = get_general_stats(db, inicio, fim)
        return MaintenanceGeneralStats(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")


@router.get("/dashboard/ranking-entidades", response_model=List[EntityRankingItem])
async def ranking_entidades(
    inicio: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    fim: Optional[str] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db_session)
):
    """Retorna ranking de entidades por quantidade de tickets."""
    try:
        results = get_entity_ranking(db, inicio, fim)
        return [EntityRankingItem(**item) for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ranking de entidades: {str(e)}")


@router.get("/dashboard/ranking-categorias", response_model=List[CategoryRankingItem])
async def ranking_categorias(
    inicio: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    fim: Optional[str] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db_session)
):
    """Retorna ranking de categorias ITIL por quantidade de tickets."""
    try:
        results = get_category_ranking(db, inicio, fim)
        return [CategoryRankingItem(**item) for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ranking de categorias: {str(e)}")


@router.get("/dashboard/tickets-novos", response_model=List[MaintenanceNewTicketItem])
async def tickets_novos(
    limit: int = Query(10, description="Limite de tickets"),
    db: Session = Depends(get_db_session)
):
    """Retorna todos os tickets com status 'Novo' (status_id = 1)."""
    try:
        results = get_new_tickets(db)
        return [MaintenanceNewTicketItem(**item) for item in results][:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tickets novos: {str(e)}")


@router.get("/dashboard/historico", response_model=List[HistoryDayItem])
async def historico(
    inicio: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    fim: Optional[str] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db_session)
):
    """Retorna histórico diário de tickets criados e resolvidos."""
    try:
        results = get_ticket_history(db, inicio, fim)
        return [HistoryDayItem(**item) for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico: {str(e)}")


@router.get("/dashboard/support-levels", response_model=List[SupportLevelItem])
async def support_levels(
    inicio: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    fim: Optional[str] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db_session)
):
    """Retorna distribuição de tickets por nível de suporte."""
    try:
        results = get_support_levels(db, inicio, fim)
        return [SupportLevelItem(**item) for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar níveis de suporte: {str(e)}")


@router.get("/dashboard/ranking-tecnicos", response_model=List[TechnicianRankingItem])
async def ranking_tecnicos(
    inicio: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    fim: Optional[str] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db_session)
):
    """Retorna ranking de técnicos por quantidade de tickets atribuídos."""
    try:
        results = get_technician_ranking(db, inicio, fim)
        return [TechnicianRankingItem(**item) for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ranking de técnicos: {str(e)}")


@router.get("/dashboard/chargers")
def chargers_dashboard(
    dateStart: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    dateEnd: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    db: Session = Depends(get_db_session)
):
    """Retorna dados do dashboard de carregadores (status e histórico)."""
    try:
        results = get_chargers_data(db, dateStart, dateEnd)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados de carregadores: {str(e)}")


@router.get("/dashboard/technician/{tech_id}", response_model=TechnicianDetail)
async def technician_details(
    tech_id: int,
    db: Session = Depends(get_db_session)
):
    """Retorna detalhes do técnico e suas estatísticas."""
    try:
        result = get_technician_details(db, tech_id)
        if not result:
            raise HTTPException(status_code=404, detail="Técnico não encontrado")
        return TechnicianDetail(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar detalhes do técnico: {str(e)}")


@router.get("/dashboard/ticket/{ticket_id}", response_model=TicketDetail)
async def ticket_details(
    ticket_id: int,
    db: Session = Depends(get_db_session)
):
    """Retorna detalhes completos do ticket (timeline)."""
    try:
        result = get_ticket_details(db, ticket_id)
        if not result:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        return TicketDetail(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar detalhes do ticket: {str(e)}")
