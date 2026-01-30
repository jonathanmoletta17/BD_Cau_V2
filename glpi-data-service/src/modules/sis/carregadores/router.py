from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from src.core.database import Database
from .schemas import KanbanData, ChargerItem, CarregadorRankingItem
from .service import CarregadoresService

router = APIRouter(prefix="/sis/carregadores", tags=["SIS - Carregadores"])

def get_db_session():
    yield from Database.get_db(context="sis")

@router.get("", response_model=List[ChargerItem])
def get_chargers_list(db: Session = Depends(get_db_session)):
    """List all chargers and their current status."""
    return CarregadoresService.get_list(db)

@router.get("/kanban", response_model=KanbanData)
def get_kanban(db: Session = Depends(get_db_session)):
    """Get Kanban board data (Occupied vs Available)."""
    return CarregadoresService.get_kanban(db)

@router.get("/ranking", response_model=List[CarregadorRankingItem])
def get_ranking(start: str = None, end: str = None, db: Session = Depends(get_db_session)):
    """Get ranking of chargers."""
    return CarregadoresService.get_ranking(db, start, end)
