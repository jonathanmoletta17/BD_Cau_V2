"""
GLPI Data Service V3 - SIS Search Models
Pydantic models for search responses (reutiliza modelos do DTIC)
"""
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class SearchItem(BaseModel):
    """Simplified ticket model for search results."""
    id: int
    glpi_id: int
    titulo: str
    descricao: Optional[str] = None
    status_id: int
    status_desc: str
    prioridade_id: int
    prioridade_desc: str
    entidade: str
    data_criacao: datetime
    data_atualizacao: datetime
    requerente: Optional[str] = None
    tecnico: Optional[str] = None

class SearchResponse(BaseModel):
    """Paginated search response."""
    items: List[SearchItem]
    total: int
    page: int
    pages: int

class StatItem(BaseModel):
    """Generic stat item."""
    label: str
    value: int
    color: Optional[str] = None

class StatsResponse(BaseModel):
    """Search statistics response."""
    by_status: List[StatItem]
    by_priority: List[StatItem]
    total: int
