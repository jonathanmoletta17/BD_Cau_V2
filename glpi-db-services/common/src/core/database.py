"""
GLPI Integrations Common - Database Module
Single Engine Pattern with Schema Context Switching.
"""
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from .config import config
from .base import Base

# Initialize engine immediately
engine = create_engine(
    config.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=config.LOG_LEVEL == "DEBUG"
)

# Session factory for background tasks
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

def get_db_session(schema: str = "public") -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes with schema context switching.
    """
    session = SessionLocal()
    try:
        if schema:
            session.execute(text(f"SET search_path TO {schema}, public"))
        yield session
    except Exception:
        session.close()
        raise
    finally:
        session.close()

# Legacy compatibility wrapper
class Database:
    @classmethod
    def get_session(cls, schema: str = "public") -> Session:
        session = SessionLocal()
        session.execute(text(f"SET search_path TO {schema}, public"))
        return session
    
    @classmethod
    def get_engine(cls):
        return engine
