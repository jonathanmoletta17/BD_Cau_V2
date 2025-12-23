"""
GLPI Integrations Common - Core Models
SyncState and Bootstrap tracking.
"""
from sqlalchemy import Column, String, DateTime, Integer, JSON
from datetime import datetime
from .base import Base
from sqlalchemy.types import UserDefinedType

class Vector(UserDefinedType):
    """
    SQLAlchemy Type for PostgreSQL pgvector.
    Assume 768 dimensions default (nomic-embed-text / nv-embed).
    """
    cache_ok = True

    def get_col_spec(self, **kw):
        return "vector(768)" # nomic-embed-text is 768d 

    def bind_processor(self, dialect):
        def process(value):
            return str(value)
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            # Parse '[1,2,3]' string back to list if needed, or return as string
            # SQLAlchemy might need list.
            if value is None: return None
            # Basic parsing if driver doesn't handle it
            return value 
        return process

class SyncState(Base):
    """
    Control table to track the last synchronization timestamp.
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
    Dead Letter Queue for Ticket Changes.
    """
    __tablename__ = 'orphan_changes'
    __table_args__ = {'schema': 'public'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    glpi_log_id = Column(Integer, unique=True, nullable=False)
    glpi_ticket_id = Column(Integer, nullable=False)
    context = Column(String(50), nullable=False) 
    payload = Column(JSON, nullable=False) 
    attempt_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_attempt = Column(DateTime(timezone=True), default=datetime.utcnow)
