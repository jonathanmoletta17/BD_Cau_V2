
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from src.core.database import get_db_session
from .analysis_service import TicketAnalysisService

router = APIRouter(prefix="/analysis", tags=["DTIC Analysis"])

@router.get("/tickets/{ticket_id}/timeline")
async def get_ticket_timeline(
    ticket_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Retorna a linha do tempo detalhada e legível de um ticket.
    Use ticket_id do GLPI.
    """
    timeline = TicketAnalysisService.get_ticket_timeline(db, ticket_id)
    if not timeline:
        # Não retornar 404 se apenas não tiver changes, mas se o ticket não existir
        # O service retorna [] se não achar ticket. Vamos assumir que [] é válido ou erro.
        # Melhor verificar existência antes ou aceitar vazio.
        return []
    return timeline

@router.get("/tickets/{ticket_id}/health")
async def get_ticket_health(
    ticket_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Retorna métricas de saúde do ticket (reaberturas, trocas de técnico).
    """
    result = TicketAnalysisService.analyze_ticket_health(db, ticket_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/global/bottlenecks")
async def get_global_bottlenecks(
    days: int = Query(30, description="Dias para análise retroativa"),
    db: Session = Depends(get_db_session)
):
    """
    Retorna os gargalos de processo (tempo médio em cada status) dos últimos X dias.
    """
    return TicketAnalysisService.get_process_bottlenecks(db, days)
