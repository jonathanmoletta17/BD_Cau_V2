"""
GLPI Data Service V3 - Database Module
Simplified database session management with multi-schema support.
Optimized for performance: Single Engine + Connection Pooling.
"""
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from .config import config

# Base is now in src.core.base
from .base import Base


class Database:
    """
    Database manager using Single Engine Pattern.
    
    Optimizations:
    - Single SQLAlchemy Engine for the entire application (enables connection pooling).
    - Session-per-request pattern.
    - Dynamic schema switching via 'SET search_path'.
    """
    
    _engine = None
    _session_factory = None

    @classmethod
    def _initialize(cls):
        """Initialize the single engine and session factory if not already done."""
        if cls._engine is None:
            cls._engine = create_engine(
                config.DATABASE_URL,
                # Default pool settings are usually sufficient (pool_size=5, max_overflow=10)
                # pool_pre_ping=True helps verify connections before usage
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
    def get_session(cls, context: str = "dtic") -> Session:
        """
        Create a new database session for the given context.
        
        Args:
            context: Business context ('dtic' or 'sis')
        
        Returns:
            SQLAlchemy Session configured for the context's schema
        """
        # Ensure engine is initialized
        if cls._engine is None:
            cls._initialize()
            
        schema = config.get_schema(context)
        session = cls._session_factory()
        
        try:
            # Set PostgreSQL search_path to use the correct schema transparently
            session.execute(text(f"SET search_path TO {schema}, public"))
        except Exception:
            session.close()
            raise
        
        return session
    
    @classmethod
    def get_db(cls, context: str = "dtic") -> Generator[Session, None, None]:
        """
        Dependency injection helper for FastAPI.
        """
        session = cls.get_session(context)
        try:
            yield session
        finally:
            session.close()
    
    @classmethod
    def close_all(cls):
        """Dispose of the engine (useful for testing/graceful shutdown)."""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None

# Alias for backward compatibility (used by main.py dependency injection)
get_db = Database.get_db
get_db_session = Database.get_db
