from pydantic import BaseModel
from typing import List, Optional

class ChargerItem(BaseModel):
    id: int
    nome: str
    status: str  # 'ocupado' | 'disponivel'
    localizacao: Optional[str] = None
    tempo_atribuido: Optional[str] = None
    # Minutos disponíveis quando o carregador está livre
    tempo_disponivel: Optional[str] = None
    ticket_id: Optional[int] = None
    # Referência para disponíveis: data do último fechado/solucionado
    ref_date: Optional[str] = None
    # Métricas comerciais diárias e status do expediente
    tempo_ocupado_min_hoje: Optional[float] = 0
    tempo_disponivel_min_hoje: Optional[float] = 0
    expediente_status: Optional[str] = 'aguardando'

class CarregadorRankingItem(BaseModel):
    id: int
    nome: str
    tickets_atribuidos: int

class KanbanTicket(BaseModel):
    id: int
    titulo: str
    localizacao: Optional[str] = None

class KanbanOccupiedItem(BaseModel):
    id: int
    nome: str
    ticket: KanbanTicket
    tempo_min: int
    tempo_ocupado_min_hoje: Optional[int] = 0
    expediente_status: Optional[str] = 'aguardando'

class KanbanAvailableItem(BaseModel):
    id: int
    nome: str
    ultimo_ticket: Optional[KanbanTicket] = None
    tempo_min: int
    tempo_disponivel_min_hoje: Optional[int] = 0
    expediente_status: Optional[str] = 'aguardando'

class KanbanData(BaseModel):
    ocupados: List[KanbanOccupiedItem]
    disponiveis: List[KanbanAvailableItem]
