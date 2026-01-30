"""
GLPI Data Service V3 - Core Base
Declarative Base for SQLAlchemy models.
Separated to avoid circular imports with database.py and config.py.
"""
from sqlalchemy.orm import declarative_base

# Declarative Base for all SQLAlchemy models
Base = declarative_base()
