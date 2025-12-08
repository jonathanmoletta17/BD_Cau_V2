"""
GLPI Data Service V3 - DTIC Tickets Models
Core domain models for ticket management
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, CheckConstraint
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime

from src.core.database import Base


class Ticket(Base):
    """
    Main ticket model - normalized architecture.
    Users and groups are in separate tables (tickets_users, tickets_groups).
    """
    __tablename__ = 'tickets'
    __table_args__ = {'schema': 'dtic'}
    
    # Identificadores
    id = Column(Integer, primary_key=True, autoincrement=True)
    glpi_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # Conteúdo
    titulo = Column(String(500), nullable=False)
    descricao = Column(Text)
    
    # Classificação
    status_id = Column(Integer)
    prioridade_id = Column(Integer)
    tipo_id = Column(Integer)
    
    # Impacto e Urgência (GLPI: 1-5)
    impact = Column(Integer, CheckConstraint('impact BETWEEN 1 AND 5'))
    urgency = Column(Integer, CheckConstraint('urgency BETWEEN 1 AND 5'))
    
    # Relacionamentos (IDs apenas - Foreign Keys implícitas)
    categoria_id = Column(Integer)
    entidade_id = Column(Integer)
    localizacao_id = Column(Integer)
    item_relacionado_id = Column(Integer)
    ultimo_atualizador_id = Column(Integer)
    
    # SLA/OLA
    tempo_para_resolver = Column(Integer)
    tempo_para_atribuir = Column(Integer)
    tempo_primeira_interacao = Column(Integer)
    tempo_acao_total = Column(Integer)
    
    # Tipo de Requisição
    tipo_requisicao_id = Column(Integer)
    
    # Timestamps (com timezone)
    criado_em = Column(TIMESTAMP(timezone=True), nullable=False)
    atualizado_em = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    solucionado_em = Column(TIMESTAMP(timezone=True))
    fechado_em = Column(TIMESTAMP(timezone=True))
    
    # Metadados
    url = Column(String(500))
    is_deleted = Column(Boolean, default=False)
    
    # Controle de Sincronização
    ticket_hash = Column(String(32), index=True)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    versao = Column(Integer, default=1)
    
    
    def __repr__(self):
        return f"<Ticket(glpi_id={self.glpi_id}, titulo='{self.titulo[:50]}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'glpi_id': self.glpi_id,
            'titulo': self.titulo,
            'status_id': self.status_id,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
