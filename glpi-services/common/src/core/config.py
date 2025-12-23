"""
GLPI Integrations Common - Configuration
Generic configuration loader using Pydantic or os.getenv.
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class CommonConfig:
    """Base configuration shared across services."""
    
    # Database
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "glpi_data")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # DTIC Context Config Helpers
    @property
    def GLPI_DTIC_URL(self) -> str:
        return os.getenv("GLPI_PROD_URL_CONFIG", "")
        
    @property
    def GLPI_DTIC_APP_TOKEN(self) -> str:
        return os.getenv("GLPI_PROD_APP_TOKEN", "")
        
    @property
    def GLPI_DTIC_USER_TOKEN(self) -> str:
        return os.getenv("GLPI_PROD_USER_TOKEN", "")

    # SIS Context Config Helpers
    @property
    def GLPI_SIS_URL(self) -> str:
        return os.getenv("GLPI_SIS_URL", "")
        
    @property
    def GLPI_SIS_APP_TOKEN(self) -> str:
        return os.getenv("GLPI_SIS_APP_TOKEN", "")
        
    @property
    def GLPI_SIS_USER_TOKEN(self) -> str:
        return os.getenv("GLPI_SIS_USER_TOKEN", "")

config = CommonConfig()
