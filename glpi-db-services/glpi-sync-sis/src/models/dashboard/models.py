"""
GLPI Data Service V3 - SIS Dashboard Response Models
Pydantic models for SIS Dashboard API responses
"""
from pydantic import BaseModel, Field


class MaintenanceGeneralStats(BaseModel):
    """EstatÃ­sticas gerais de tickets por status."""
    novos: int = Field(..., description="Tickets com status 1 (Novo)")
    em_progresso: int = Field(..., description="Tickets com status 2 (AtribuÃ­do) + 3 (Planejado)")
    pendentes: int = Field(..., description="Tickets com status 4 (Pendente)")
    resolvidos: int = Field(..., description="Tickets com status 5 (Resolvido) + 6 (Fechado)")


class EntityRankingItem(BaseModel):
    """Item de ranking de entidades por quantidade de tickets."""
    entity_name: str = Field(..., description="Nome completo da entidade")
    ticket_count: int = Field(..., description="Total de tickets da entidade")


class CategoryRankingItem(BaseModel):
    """Item de ranking de categorias por quantidade de tickets."""
    category_name: str = Field(..., description="Nome completo da categoria")
    ticket_count: int = Field(..., description="Total de tickets da categoria")


class MaintenanceNewTicketItem(BaseModel):
    """Ticket novo/recente para visualizaÃ§Ã£o resumida."""
    id: int = Field(..., description="ID GLPI do ticket")
    titulo: str = Field(..., description="TÃ­tulo do ticket")
    solicitante: str = Field(..., description="Nome do solicitante")
    data: str = Field(..., description="Data de criaÃ§Ã£o (formato: dd/MM/yyyy HH:mm)")
    entidade: str = Field(..., description="Nome da entidade")
    prioridade: str = Field(None, description="Prioridade do ticket (Baixa, MÃ©dia, Alta, etc)")


class TechnicianRankingItem(BaseModel):
    """Item de ranking de tÃ©cnicos por quantidade de tickets atribuÃ­dos."""
    tecnico: str = Field(..., description="Nome do tÃ©cnico")
    tickets: int = Field(..., description="Total de tickets atribuÃ­dos ao tÃ©cnico")

from typing import List, Optional

class TechnicianDetailStats(BaseModel):
    """Estatísticas detalhadas do técnico."""
    total_tickets: int
    resolved_tickets: int
    avg_resolution_time_hours: float
    satisfaction_rate: Optional[float] = None

class TechnicianDetail(BaseModel):
    """Detalhes completos do técnico."""
    id: int
    name: str
    stats: TechnicianDetailStats

class TicketTimelineItem(BaseModel):
    """Item da timeline do ticket (followup ou mudança)."""
    id: int
    date: str
    type: str # "followup", "change", "task"
    author: str
    content: str

class TicketDetail(BaseModel):
    """Detalhes completos do ticket."""
    id: int
    glpi_id: int
    title: str
    description: str
    status: str
    priority: str
    creation_date: str
    solve_date: Optional[str] = None
    requester: str
    technician: Optional[str] = None
    timeline: List[TicketTimelineItem]

