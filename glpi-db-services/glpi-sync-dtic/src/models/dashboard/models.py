"""
GLPI Data Service V3 - SIS Dashboard Response Models
Pydantic models for SIS Dashboard API responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class MaintenanceGeneralStats(BaseModel):
    """Estatísticas gerais de tickets por status."""
    novos: int = Field(..., description="Tickets com status 1 (Novo)")
    em_progresso: int = Field(..., description="Tickets com status 2 (Atribuído) + 3 (Planejado)")
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


class HistoryDayItem(BaseModel):
    """Item de histórico diário de tickets."""
    date: str = Field(..., description="Data no formato DD/MM")
    created: int = Field(..., description="Tickets criados neste dia")
    resolved: int = Field(..., description="Tickets resolvidos neste dia")


class SupportLevelItem(BaseModel):
    """Item de distribuição por nível de suporte."""
    nivel: str = Field(..., description="Nível de suporte (N1, N2, N3, N4)")
    total: int = Field(..., description="Total de tickets neste nível")


class MaintenanceNewTicketItem(BaseModel):
    """Ticket novo/recente para visualização resumida."""
    id: int = Field(..., description="ID GLPI do ticket")
    titulo: str = Field(..., description="Título do ticket")
    solicitante: str = Field(..., description="Nome do solicitante")
    data: str = Field(..., description="Data de criação (formato: dd/MM/yyyy HH:mm)")
    entidade: str = Field(..., description="Nome da entidade")
    prioridade: str = Field(None, description="Prioridade do ticket (Baixa, Média, Alta, etc)")


class TechnicianRankingItem(BaseModel):
    """Item de ranking de técnicos por quantidade de tickets atribuídos."""
    tecnico: str = Field(..., description="Nome do técnico")
    tickets: int = Field(..., description="Total de tickets atribuídos ao técnico")


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
    url: Optional[str] = None
