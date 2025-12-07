"""
GLPI Data Service V3 - Database Module
Simplified database session management with multi-schema support
"""
from typing import Dict, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import NullPool

from .config import config

# Declarative Base for all SQLAlchemy models
Base = declarative_base()


class Database:
    """
    Simplified database manager with multi-schema support.
    
    Each context (DTIC, SIS) operates on its own PostgreSQL schema.
    """
    
    _engines: Dict[str, any] = {}
    _session_makers: Dict[str, sessionmaker] = {}
    
    @classmethod
    def _get_engine(cls, schema: str):
        """Get or create engine for a schema."""
        if schema not in cls._engines:
            engine = create_engine(
                config.DATABASE_URL,
                poolclass=NullPool,
                echo=config.LOG_LEVEL == "DEBUG"
            )
            cls._engines[schema] = engine
        return cls._engines[schema]
    
    @classmethod
    def _get_session_maker(cls, schema: str) -> sessionmaker:
        """Get or create session maker for a schema."""
        if schema not in cls._session_makers:
            engine = cls._get_engine(schema)
            cls._session_makers[schema] = sessionmaker(
                bind=engine,
                expire_on_commit=False
            )
        return cls._session_makers[schema]
    
    @classmethod
    def get_session(cls, context: str = "dtic") -> Session:
        """
        Create a new database session for the given context.
        
        Args:
            context: Business context ('dtic' or 'sis')
        
        Returns:
            SQLAlchemy Session configured for the context's schema
        
        Usage:
            session = Database.get_session(context="dtic")
            try:
                tickets = session.query(Ticket).all()
                session.commit()
            finally:
                session.close()
        """
        schema = config.get_schema(context)
        SessionMaker = cls._get_session_maker(schema)
        session = SessionMaker()
        
        # Set PostgreSQL search_path to use the correct schema
        from sqlalchemy import text
        session.execute(text(f"SET search_path TO {schema}, public"))
        
        return session
    
    @classmethod
    def get_db(cls, context: str = "dtic") -> Generator[Session, None, None]:
        """
        Dependency injection helper for FastAPI.
        
        Usage:
            @router.get("/tickets")
            def get_tickets(db: Session = Depends(lambda: Database.get_db(context="dtic"))):
                ...
        """
        session = cls.get_session(context)
        try:
            yield session
        finally:
            session.close()
    
    @classmethod
    def close_all(cls):
        """Close all database connections (for testing/shutdown)."""
        for engine in cls._engines.values():
            engine.dispose()
        cls._engines.clear()
        cls._session_makers.clear()
