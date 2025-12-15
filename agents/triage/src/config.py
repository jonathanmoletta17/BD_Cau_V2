from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Config
    ENV: str = "dev"
    OPENER_TARGET_ENV: str = "test"
    
    # Mock Auth (Dev Only)
    MOCK_AUTH_ENABLED: bool = False
    
    # GLPI Config (PROD - Source of Truth / Read Only)
    GLPI_PROD_URL: Optional[str] = None
    GLPI_PROD_APP_TOKEN: Optional[str] = None
    GLPI_PROD_USER_TOKEN: Optional[str] = None

    # GLPI Config (TEST - Sandbox / Write Target)
    GLPI_TEST_URL: Optional[str] = None
    GLPI_TEST_APP_TOKEN: Optional[str] = None
    GLPI_TEST_USER_TOKEN: Optional[str] = None
    
    # Legacy / Default (to avoid breaking simple local setups if .env isn't updated)
    GLPI_API_URL: Optional[str] = None
    GLPI_APP_TOKEN: Optional[str] = None
    GLPI_USER_TOKEN: Optional[str] = None
    
    # Inference Server Config
    INFERENCE_SERVER_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_MODEL: str = "llama3.1"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
