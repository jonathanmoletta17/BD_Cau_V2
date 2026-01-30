from sqlalchemy import Column, Integer, Text, String, JSON
from sqlalchemy.types import UserDefinedType
from src.core.base import Base

# Define Vector type for SQLAlchemy if not using pgvector-python lib heavily
class Vector(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return "vector(768)"  # nomic-embed-text is 768d usually

    def bind_processor(self, dialect):
        def process(value):
            return str(value)
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return value
        return process

class KnowledgeEntry(Base):
    __tablename__ = 'knowledge_entries'
    __table_args__ = {'schema': 'dtic'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, unique=True, index=True)
    
    # The actual content we learned from
    content = Column(Text, nullable=False)
    
    # The vector representation
    # Note: We assume 768 dimensions for nomic-embed-text
    embedding = Column(Vector) 
    
    # Helper metadata (ticket title, solution status, etc)
    metadata_json = Column(JSON, default={})

    def __repr__(self):
        return f"<KnowledgeEntry(ticket_id={self.ticket_id})>"
