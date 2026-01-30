"""
SIS Ticket Relationship Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, UniqueConstraint, Index, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime

from src.core.base import Base


class TicketUser(Base):
    """N:N relationship between tickets and users (SIS schema)."""
    __tablename__ = 'tickets_users'
    __table_args__ = (
        UniqueConstraint('ticket_id', 'user_id', 'type', name='uq_sis_tickets_users'),
        {'schema': 'sis'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('sis.tickets.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('sis.glpi_users.id'), nullable=False, index=True)
    type = Column(Integer, nullable=False, index=True)  # 1=Requester, 2=Assigned, 3=Observer
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TicketUser(ticket={self.ticket_id}, user={self.user_id}, type={self.type})>"


class TicketGroup(Base):
    """N:N relationship between tickets and groups (SIS schema)."""
    __tablename__ = 'tickets_groups'
    __table_args__ = (
        UniqueConstraint('ticket_id', 'group_id', 'type', name='uq_sis_tickets_groups'),
        {'schema': 'sis'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('sis.tickets.id', ondelete='CASCADE'), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey('sis.glpi_groups.id'), nullable=False, index=True)
    type = Column(Integer, nullable=False, index=True)  # 1=Requester, 2=Assigned
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TicketGroup(ticket={self.ticket_id}, group={self.group_id}, type={self.type})>"


class TicketChange(Base):
    """Ticket changes history (SIS schema)."""
    __tablename__ = 'ticket_changes'
    __table_args__ = (
        Index('ix_sis_ticket_changes_ticket_data', 'ticket_id', 'data_mudanca'),
        Index('ix_sis_ticket_changes_campo_data', 'campo', 'data_mudanca'),
        {'schema': 'sis'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    glpi_id = Column(Integer, unique=True, nullable=False, index=True)
    ticket_id = Column(Integer, ForeignKey('sis.tickets.id', ondelete='CASCADE'), nullable=False, index=True)
    data_mudanca = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    usuario_id = Column(Integer)
    campo = Column(String(255))
    valor_antigo = Column(Text)
    valor_novo = Column(Text)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    
    def __repr__(self):
        return f"<TicketChange(ticket={self.ticket_id}, field='{self.campo}')>"


class TicketItem(Base):
    """N:N relationship between tickets and items (Assets) (SIS schema)."""
    __tablename__ = 'glpi_items_tickets'
    __table_args__ = (
        Index('ix_sis_items_tickets_item', 'itemtype', 'items_id'),
        {'schema': 'sis'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tickets_id = Column(Integer, nullable=False, index=True) # Not FK because it might refer to GLPI ID
    itemtype = Column(String(100), nullable=False)
    items_id = Column(Integer, nullable=False)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TicketItem(ticket={self.tickets_id}, item={self.itemtype}:{self.items_id})>"
