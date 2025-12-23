"""
GLPI Data Service V3 - DTIC Search Routes
API endpoints for smart search (DTIC schema)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from src.core.database import Database
from .models import SearchResponse, StatsResponse
from .service import search_tickets, get_suggestions, get_search_stats

router = APIRouter(prefix="/sis/search", tags=["DTIC Search"])

def get_db_session():
    """Dependency injection for DTIC database session."""
    session = Database.get_session(schema="dtic")
    try:
        yield session
    finally:
        session.close()

@router.get("", response_model=SearchResponse)
async def search(
    q: Optional[str] = Query(None, description="Termo de busca (título, descrição)"),
    status: Optional[str] = Query(None, description="IDs de status separados por vírgula"),
    entidade_id: Optional[int] = Query(None, description="ID da entidade"),
    data_inicio: Optional[str] = Query(None, description="Data inicial (ISO)"),
    data_fim: Optional[str] = Query(None, description="Data final (ISO)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session)
):
    """Busca tickets com filtros."""
    try:
        return search_tickets(
            db, q, status, entidade_id, data_inicio, data_fim, page, per_page
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggest", response_model=List[str])
async def suggest(
    field: str = Query(..., description="Campo para sugestão (entidade, requerente, tecnico)"),
    prefix: str = Query(..., description="Prefixo para busca"),
    db: Session = Depends(get_db_session)
):
    """Retorna sugestões para autocomplete."""
    try:
        return get_suggestions(db, field, prefix)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=StatsResponse)
async def stats(
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    entidade_id: Optional[int] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    db: Session = Depends(get_db_session)
):
    """Retorna estatísticas da busca atual."""
    try:
        return get_search_stats(db, q, status, entidade_id, data_inicio, data_fim)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
