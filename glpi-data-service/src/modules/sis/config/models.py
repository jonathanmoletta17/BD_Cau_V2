from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from src.core.database import Base

class Setting(Base):
    __tablename__ = 'settings'
    __table_args__ = {'schema': 'sis'}

    key = Column(String(100), primary_key=True)
    value = Column(JSONB)
