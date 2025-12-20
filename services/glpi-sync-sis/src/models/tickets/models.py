"""
SIS Tickets Models - Schema SIS
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime
from sqlalchemy.types import JSON
from src.core.models import Vector # Import Vector type

from src.core.base import Base


class Ticket(Base):
    """Main ticket model - SIS schema."""
    __tablename__ = 'tickets'
    __table_args__ = {'schema': 'sis'}  # ← SIS schema
    
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
    
    # Impacto e Urgência
    impact = Column(Integer, CheckConstraint('impact BETWEEN 1 AND 5'))
    urgency = Column(Integer, CheckConstraint('urgency BETWEEN 1 AND 5'))
    
    # Relacionamentos (IDs)
    categoria_id = Column(Integer)
    entidade_id = Column(Integer, index=True)  # ← Filtrar por entidade
    localizacao_id = Column(Integer)
    
    # SLA/OLA
    tempo_para_resolver = Column(Integer)
    tempo_para_atribuir = Column(Integer)
    
    # Tipo de Requisição
    tipo_requisicao_id = Column(Integer)
    
    # Timestamps
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
    
    def __repr__(self):
        return f"<Ticket(glpi_id={self.glpi_id}, titulo='{self.titulo[:50]}')>"

class TicketKnowledge(Base):
    """
    RAG/Knowledge Base for Tickets.
    Stores embeddings and content for semantic search.
    """
    __tablename__ = 'ticket_knowledge'
    __table_args__ = {'schema': 'sis'} # SIS schema

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, unique=True, nullable=False, index=True) # One-to-One with Ticket
    
    # Content used for embedding (usually Title + Description)
    content = Column(Text, nullable=False)
    
    # Vector Embedding (pgvector)
    embedding = Column(Vector) 
    
    # Metadata for filtering/context
    metadata_json = Column(JSON, default={})
    
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<TicketKnowledge(ticket_id={self.ticket_id})>"
