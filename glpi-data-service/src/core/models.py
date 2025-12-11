"""
Core Models for GLPI Data Service
"""
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from src.core.database import Base

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
