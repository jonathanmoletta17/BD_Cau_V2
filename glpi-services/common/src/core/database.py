"""
GLPI Integrations Common - Database Module
Single Engine Pattern with Schema Context Switching.
"""
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from .config import config
from .base import Base

class Database:
    _engine = None
    _session_factory = None

    @classmethod
    def _initialize(cls):
        """Initialize the single engine and session factory if not already done."""
        if cls._engine is None:
            cls._engine = create_engine(
                config.DATABASE_URL,
                pool_pre_ping=True,
                echo=config.LOG_LEVEL == "DEBUG"
            )
            cls._session_factory = sessionmaker(
                bind=cls._engine,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )

    @classmethod
    def get_session(cls, schema: str = "public") -> Session:
        """
        Create a new database session with a specific schema search path.
        """
        if cls._engine is None:
            cls._initialize()
            
        session = cls._session_factory()
        
        try:
            # Set PostgreSQL search_path transparently
            session.execute(text(f"SET search_path TO {schema}, public"))
        except Exception:
            session.close()
            raise
        
        return session
    
    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            cls._initialize()
        return cls._engine
