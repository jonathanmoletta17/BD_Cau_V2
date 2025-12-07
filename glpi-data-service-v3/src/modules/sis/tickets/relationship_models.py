"""
SIS Ticket Relationship Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime

from src.core.database import Base


class TicketUser(Base):
    """N:N relationship between tickets and users (SIS schema)."""
    __tablename__ = 'tickets_users'
    __table_args__ = (
        UniqueConstraint('ticket_id', 'user_id', 'type', name='uq_sis_tickets_users'),
        Index('ix_sis_tickets_users_ticket', 'ticket_id'),
        Index('ix_sis_tickets_users_user', 'user_id'),
        {'schema': 'sis'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)  # 1=Requester, 2=Assigned, 3=Observer
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TicketUser(ticket={self.ticket_id}, user={self.user_id}, type={self.type})>"


class TicketGroup(Base):
    """N:N relationship between tickets and groups (SIS schema)."""
    __tablename__ = 'tickets_groups'
    __table_args__ = (
        UniqueConstraint('ticket_id', 'group_id', 'type', name='uq_sis_tickets_groups'),
        Index('ix_sis_tickets_groups_ticket', 'ticket_id'),
        Index('ix_sis_tickets_groups_group', 'group_id'),
        {'schema': 'sis'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)  # 1=Requester, 2=Assigned
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TicketGroup(ticket={self.ticket_id}, group={self.group_id}, type={self.type})>"


class TicketChange(Base):
    """Ticket changes history (SIS schema)."""
    __tablename__ = 'ticket_changes'
    __table_args__ = (
        Index('ix_sis_ticket_changes_ticket', 'ticket_id'),
        Index('ix_sis_ticket_changes_date', 'data_mudanca'),
        {'schema': 'sis'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    glpi_id = Column(Integer, index=True)
    ticket_id = Column(Integer, nullable=False)
    data_mudanca = Column(TIMESTAMP(timezone=True), nullable=False)
    usuario_id = Column(Integer)
    campo = Column(String(255))
    valor_antigo = Column(Text)
    valor_novo = Column(Text)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TicketChange(ticket={self.ticket_id}, field='{self.campo}')>"
