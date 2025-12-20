from typing import Optional
import os
from pydantic import model_validator
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
    
    # Legacy / Default
    GLPI_API_URL: Optional[str] = "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php"
    GLPI_APP_TOKEN: Optional[str] = None
    GLPI_USER_TOKEN: Optional[str] = None
    
    # Inference Server Config
    INFERENCE_SERVER_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_MODEL: str = "llama3.1"

    class Config:
        env_file = ".env"
        extra = "ignore"
        
    @model_validator(mode='after')
    def set_defaults(self):
        # Fallback Logic: Propagate Legacy Vars to Prod/Test if missing
        if not self.GLPI_PROD_URL and self.GLPI_API_URL:
            self.GLPI_PROD_URL = self.GLPI_API_URL
        if not self.GLPI_PROD_APP_TOKEN and self.GLPI_APP_TOKEN:
             self.GLPI_PROD_APP_TOKEN = self.GLPI_APP_TOKEN
        if not self.GLPI_PROD_USER_TOKEN and self.GLPI_USER_TOKEN:
             self.GLPI_PROD_USER_TOKEN = self.GLPI_USER_TOKEN
             
        # Also default Test to Legacy if missing (Hybrid setup usually shares, or specifically overrides)
        if not self.GLPI_TEST_URL and self.GLPI_API_URL:
            self.GLPI_TEST_URL = self.GLPI_API_URL
        if not self.GLPI_TEST_APP_TOKEN and self.GLPI_APP_TOKEN:
             self.GLPI_TEST_APP_TOKEN = self.GLPI_APP_TOKEN
        if not self.GLPI_TEST_USER_TOKEN and self.GLPI_USER_TOKEN:
             self.GLPI_TEST_USER_TOKEN = self.GLPI_USER_TOKEN
        return self

settings = Settings()
