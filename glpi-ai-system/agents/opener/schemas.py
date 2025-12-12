from pydantic import BaseModel, Field
from typing import Optional, Literal

class TicketContext(BaseModel):
    # O que o usuário disse (Raw)
    original_complaint: str
    
    # Raciocínio (Chain of Thought)
    reasoning: Optional[str] = Field(default=None, description="Explicação passo-a-passo antes de preencher os campos")
    
    # O que extraímos (Slots)
    summary: Optional[str] = Field(default=None, description="Título curto para o GLPI")
    description: Optional[str] = Field(default=None, description="Descrição técnica enriquecida")
    location: Optional[str] = Field(default=None, description="Local exato (Prédio, Sala, Andar)")
    
    # Matriz ITIL (Calculada pelo Agente, não perguntada diretamente)
    urgency: Optional[Literal["Alta", "Média", "Baixa"]] = Field(default=None)
    impact: Optional[Literal["Individual", "Setorial", "Organizacional"]] = Field(default=None)
    
    # Controle de Estado
    intent: Optional[str] = Field(default=None, description="Intenção detectada (ex: internet_issue)")
    missing_info: list[str] = Field(default_factory=list, description="Lista de slots faltando")
    history: list[str] = Field(default_factory=list, description="Histórico da conversa")
    
    technical_question_asked: bool = False
    ready_to_submit: bool = False
    
    # Comunicação
    response_to_user: Optional[str] = Field(default=None, description="A pergunta ou confirmação para o usuário")
