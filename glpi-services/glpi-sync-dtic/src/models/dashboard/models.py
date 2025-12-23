"""
GLPI Data Service V3 - Dashboard Response Models
Pydantic models for SIS Dashboard API responses
"""
from pydantic import BaseModel, Field


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
