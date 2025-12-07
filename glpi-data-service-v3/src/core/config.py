"""
GLPI Data Service V3 - Core Configuration
Clean, simplified configuration for multi-context support (DTIC & SIS)
"""
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Centralized configuration for GLPI Data Service V3."""
    
    # PostgreSQL Configuration
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "glpi_data")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "glpi_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    
    # Database URL
    DATABASE_URL: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    
    # Schema mapping for contexts (DTIC and SIS live in separate schemas)
    SCHEMAS: Dict[str, str] = {
        "dtic": "dtic",
        "sis": "sis"
    }
    
    # GLPI API Configuration (DTIC)
    GLPI_DTIC_URL: str = os.getenv("GLPI_DTIC_URL", "")
    GLPI_DTIC_APP_TOKEN: str = os.getenv("GLPI_DTIC_APP_TOKEN", "")
    GLPI_DTIC_USER_TOKEN: str = os.getenv("GLPI_DTIC_USER_TOKEN", "")
    
    # GLPI API Configuration (SIS - future)
    GLPI_SIS_URL: str = os.getenv("GLPI_SIS_URL", "")
    GLPI_SIS_APP_TOKEN: str = os.getenv("GLPI_SIS_APP_TOKEN", "")
    GLPI_SIS_USER_TOKEN: str = os.getenv("GLPI_SIS_USER_TOKEN", "")
    
    # Application Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_schema(cls, context: str) -> str:
        """Get PostgreSQL schema for a given context."""
        return cls.SCHEMAS.get(context.lower(), "dtic")
    
    @classmethod
    def get_glpi_url(cls, context: str) -> str:
        """Get GLPI API URL for a given context."""
        return cls.GLPI_SIS_URL if context.lower() == "sis" else cls.GLPI_DTIC_URL
    
    @classmethod
    def get_glpi_app_token(cls, context: str) -> str:
        """Get GLPI App Token for a given context."""
        return cls.GLPI_SIS_APP_TOKEN if context.lower() == "sis" else cls.GLPI_DTIC_APP_TOKEN
    
    @classmethod
    def get_glpi_user_token(cls, context: str) -> str:
        """Get GLPI User Token for a given context."""
        return cls.GLPI_SIS_USER_TOKEN if context.lower() == "sis" else cls.GLPI_DTIC_USER_TOKEN


# Global config instance
config = Config()
