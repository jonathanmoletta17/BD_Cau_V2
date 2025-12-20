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
    MaintenanceNewTicketItem,
    TechnicianRankingItem
)
from .service import (
    get_general_stats,
    get_entity_ranking,
    get_category_ranking,
    get_new_tickets,
    get_technician_ranking
)

# Create router with prefix matching frontend expectations
# Frontend calls: /api/v1/sis/dashboard/stats-gerais
# Main app mounts at /api/v1
# So prefix here is /sis/dashboard
router = APIRouter(prefix="/sis", tags=["SIS Dashboard"])


def get_db_session():
    """Dependency injection for SIS database session."""
    yield from Database.get_db(context="sis")


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
        # Note: service.get_new_tickets does not currently accept limit in the replicated code, 
        # but the frontend sends it. We can slice the result or update service.
        # For simplicity, we get all and slice here, but ideal is DB limit.
        results = get_new_tickets(db)
        return [MaintenanceNewTicketItem(**item) for item in results][:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tickets novos: {str(e)}")


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
