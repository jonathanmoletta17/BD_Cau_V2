"""
SIS Smart Search Routes
Endpoint para busca inteligente de tickets SIS
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.core.database import Database
from . import service

router = APIRouter(prefix="/smart-search", tags=["SIS Smart Search"])

def get_db():
    """Dependency to get database session"""
    return Database.get_session()

@router.get("/tickets")
def search_tickets(
    search: Optional[str] = Query(None, description="Search term"),
    status: Optional[int] = Query(None, description="Ticket status filter"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """
    Busca inteligente de tickets SIS com filtros
    """
    return service.search_tickets(db, search, status, skip, limit)

@router.get("/metrics")
def get_kpi_metrics(db: Session = Depends(get_db)):
    """
    Retorna métricas agregadas (KPIs) dos tickets SIS
    """
    return service.get_kpi_metrics(db)
