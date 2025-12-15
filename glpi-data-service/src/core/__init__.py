"""
GLPI Data Service V3 - Core Module
"""
from .config import config, Config
from .base import Base
from .database import Database

__all__ = ["config", "Config", "Database", "Base"]
