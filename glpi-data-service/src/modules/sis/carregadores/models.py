from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime

from src.core.database import Base

class Carregador(Base):
    """GLPI Plugin Generic Object: Carregador (SIS schema)."""
    __tablename__ = 'glpi_plugin_genericobject_carregadors'
    __table_args__ = {'schema': 'sis'}
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), index=True)
    entities_id = Column(Integer, index=True)
    is_deleted = Column(Boolean, default=False)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Carregador(id={self.id}, name='{self.name}')>"
