"""
GLPI Data Service V3 - DTIC Ticket Relationship Models
"""
from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime

from src.core.base import Base


class TicketUser(Base):
    """N:N relationship between tickets and users with type."""
    __tablename__ = 'tickets_users'
    __table_args__ = (
        UniqueConstraint('ticket_id', 'user_id', 'type', name='uq_ticket_user_type'),
        {'schema': 'dtic'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('dtic.tickets.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('dtic.glpi_users.id'), nullable=False, index=True)
    type = Column(Integer, nullable=False, index=True)  # 1=Requester, 2=Assigned, 3=Observer
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TicketUser(ticket={self.ticket_id}, user={self.user_id}, type={self.type})>"


class TicketGroup(Base):
    """N:N relationship between tickets and groups."""
    __tablename__ = 'tickets_groups'
    __table_args__ = (
        UniqueConstraint('ticket_id', 'group_id', 'type', name='uq_ticket_group_type'),
        {'schema': 'dtic'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('dtic.tickets.id', ondelete='CASCADE'), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey('dtic.glpi_groups.id'), nullable=False, index=True)
    type = Column(Integer, nullable=False, index=True)  # 1=Requester, 2=Assigned
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TicketGroup(ticket={self.ticket_id}, group={self.group_id}, type={self.type})>"


class TicketChange(Base):
    """Historical changes to tickets."""
    __tablename__ = 'ticket_changes'
    __table_args__ = (
        Index('ix_dtic_ticket_changes_ticket_data', 'ticket_id', 'data_mudanca'),
        Index('ix_dtic_ticket_changes_campo_data', 'campo', 'data_mudanca'),
        {'schema': 'dtic'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    glpi_id = Column(Integer, unique=True, nullable=False, index=True)
    ticket_id = Column(Integer, ForeignKey('dtic.tickets.id', ondelete='CASCADE'), nullable=False, index=True)
    data_mudanca = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    usuario_id = Column(Integer)
    usuario_nome = Column(String(255))
    campo = Column(String(100))
    campo_id = Column(Integer)
    valor_antigo = Column(Text)
    valor_novo = Column(Text)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TicketChange(glpi_id={self.glpi_id}, campo='{self.campo}')>"
