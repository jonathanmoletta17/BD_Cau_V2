"""
GLPI Data Service V3 - Dashboard API Routes
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
    get_technician_ranking,
    get_level_stats,
    get_recent_activities
)

# Create router with prefix and tags
router = APIRouter(prefix="/dtic", tags=["DTIC Dashboard"])


def get_db_session():
    """Dependency injection for DTIC database session."""
    yield from Database.get_db(context="dtic")


@router.get("/metrics-gerais", response_model=MaintenanceGeneralStats)
async def metrics_gerais(
    inicio: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    fim: Optional[str] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db_session)
):
    """
    Retorna estatísticas gerais de tickets por status.
    
    - **novos**: Status 1 (Novo) - **SEMPRE TOTAL (Ignora filtro de data)**
    - **em_progresso**: Status 2 (Atribuído) + Status 3 (Planejado)
    - **pendentes**: Status 4 (Pendente)
    - **resolvidos**: Status 5 (Resolvido) + 6 (Fechado)
    """
    try:
        result = get_general_stats(db, inicio, fim)
        return MaintenanceGeneralStats(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")


@router.get("/ranking-entidades", response_model=List[EntityRankingItem])
async def ranking_entidades(
    inicio: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    fim: Optional[str] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db_session)
):
    """
    Retorna ranking de entidades por quantidade de tickets.
    
    Ordenado por ticket_count em ordem decrescente.
    """
    try:
        results = get_entity_ranking(db, inicio, fim)
        return [EntityRankingItem(**item) for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ranking de entidades: {str(e)}")


@router.get("/ranking-categorias", response_model=List[CategoryRankingItem])
async def ranking_categorias(
    inicio: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    fim: Optional[str] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db_session)
):
    """
    Retorna ranking de categorias ITIL por quantidade de tickets.
    
    Ordenado por ticket_count em ordem decrescente.
    """
    try:
        results = get_category_ranking(db, inicio, fim)
        return [CategoryRankingItem(**item) for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ranking de categorias: {str(e)}")


@router.get("/tickets-novos", response_model=List[MaintenanceNewTicketItem])
async def tickets_novos(
    db: Session = Depends(get_db_session)
):
    """
    Retorna todos os tickets com status "Novo" (status_id = 1).
    
    Ordenado por data de criação em ordem decrescente.
    """
    try:
        results = get_new_tickets(db)
        return [MaintenanceNewTicketItem(**item) for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tickets novos: {str(e)}")


@router.get("/ranking-tecnicos", response_model=List[TechnicianRankingItem])
async def ranking_tecnicos(
    inicio: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    fim: Optional[str] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db_session)
):
    """
    Retorna ranking de técnicos por quantidade de tickets atribuídos.
    
    Ordenado por tickets em ordem decrescente.
    
    **Nota**: Este endpoint pode ser lento com grandes volumes de dados.
    """
    try:
        results = get_technician_ranking(db, inicio, fim)
        return [TechnicianRankingItem(**item) for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ranking de técnicos: {str(e)}")


@router.get("/status-niveis")
async def status_niveis(
    inicio: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    fim: Optional[str] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db_session)
):
    """
    Retorna estatísticas de tickets por nível de prioridade (N1-N4) e status.
    
    - **N1**: Prioridade Muito Alta (5)
    - **N2**: Prioridade Alta (4)
    - **N3**: Prioridade Média (3)
    - **N4**: Prioridade Baixa/Muito Baixa (1-2)
    
    Cada nível contém contadores por status: novos, em_progresso, pendentes, resolvidos, total
    """
    try:
        result = get_level_stats(db, inicio, fim)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas por nível: {str(e)}")


@router.get("/atividades-recentes")
async def atividades_recentes(
    limit: int = Query(10, ge=1, le=100, description="Número máximo de atividades a retornar"),
    db: Session = Depends(get_db_session)
):
    """
    Retorna as atividades recentes (alterações em tickets).
    
    Ordenado por data de mudança em ordem decrescente.
    """
    try:
        results = get_recent_activities(db, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar atividades recentes: {str(e)}")
