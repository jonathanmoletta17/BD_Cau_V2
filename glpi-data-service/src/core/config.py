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
    POSTGRES_HOST: str = os.getenv("PGHOST", os.getenv("POSTGRES_HOST", "localhost"))
    POSTGRES_PORT: int = int(os.getenv("PGPORT", os.getenv("POSTGRES_PORT", "5432")))
    POSTGRES_DB: str = os.getenv("PGDATABASE", os.getenv("POSTGRES_DB", "glpi_data"))
    POSTGRES_USER: str = os.getenv("PGUSER", os.getenv("POSTGRES_USER", ""))
    POSTGRES_PASSWORD: str = os.getenv("PGPASSWORD", os.getenv("POSTGRES_PASSWORD", ""))
    
    # Database URL - prefer Replit's DATABASE_URL if available
    DATABASE_URL: str = os.getenv("DATABASE_URL") or (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    
    # Schema mapping for contexts (DTIC and SIS live in separate schemas)
    SCHEMAS: Dict[str, str] = {
        "dtic": "dtic",
        "sis": "sis"
    }
    
    # GLPI API Configuration (DTIC)
    GLPI_DTIC_URL: str = os.getenv("GLPI_DTIC_URL", os.getenv("GLPI_DTIC_URL", ""))
    GLPI_DTIC_APP_TOKEN: str = os.getenv("GLPI_DTIC_APP_TOKEN", os.getenv("GLPI_DTIC_APP_TOKEN", ""))
    GLPI_DTIC_USER_TOKEN: str = os.getenv("GLPI_DTIC_USER_TOKEN", os.getenv("GLPI_DTIC_USER_TOKEN", ""))
    
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

# Export commonly used values for convenience
DATABASE_URL = config.DATABASE_URL
LOG_LEVEL = config.LOG_LEVEL
POSTGRES_HOST = config.POSTGRES_HOST
POSTGRES_PORT = config.POSTGRES_PORT
POSTGRES_DB = config.POSTGRES_DB
POSTGRES_USER = config.POSTGRES_USER
POSTGRES_PASSWORD = config.POSTGRES_PASSWORD

# SAFETY CHECK: Prevent using Test Environment as DTICuction Source
# Disabled for Replit environment - uncomment for DTICuction usage
# if "10.72.16.202" in config.GLPI_DTIC_URL:
#     import sys
#     print("\n[CRITICAL] SAFETY LOCK: 'GLPI_DTIC_URL' is pointing to Test Environment (10.72.16.202).")
#     print("           This is FORBIDDEN for the Data Service (Source of Truth).")
#     print("           Please check GLPI_DTIC_URL in your .env file.\n")
#     sys.exit(1)
