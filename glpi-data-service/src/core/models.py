"""
Core Models for GLPI Data Service
"""
from sqlalchemy import Column, String, DateTime, Integer, JSON
from datetime import datetime
from src.core.base import Base

class SyncState(Base):
    """
    Control table to track the last synchronization timestamp for each context/entity.
    Used for Delta Sync (Incremental updates).
    """
    __tablename__ = 'sync_state'
    __table_args__ = {'schema': 'public'}

    # Composite Key: Context (dtic/sis) + Entity Type (Ticket, User, etc)
    context = Column(String(50), primary_key=True)
    entity_type = Column(String(50), primary_key=True)
    
    last_sync = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SyncState(context={self.context}, entity={self.entity_type}, last_sync={self.last_sync})>"

class BootstrapState(Base):
    __tablename__ = 'bootstrap_state'
    __table_args__ = {'schema': 'public'}
    context = Column(String(50), primary_key=True)
    status = Column(String(50))
    last_attempt = Column(DateTime(timezone=True), default=datetime.utcnow)

class OrphanChange(Base):
    """
    Dead Letter Queue for Ticket Changes (Logs) that arrive before the Ticket exists locally.
    """
    __tablename__ = 'orphan_changes'
    __table_args__ = {'schema': 'public'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    glpi_log_id = Column(Integer, unique=True, nullable=False)
    glpi_ticket_id = Column(Integer, nullable=False)
    context = Column(String(50), nullable=False) # dtic or sis
    payload = Column(JSON, nullable=False) # Store full log data to retry later
    attempt_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_attempt = Column(DateTime(timezone=True), default=datetime.utcnow)
