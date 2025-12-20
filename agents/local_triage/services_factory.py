import os
import sys
from pathlib import Path

# Add project root to path to ensure cross-agent imports work
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# CRITICAL: Agent A uses "from src..." imports. We must add its root to path.
agent_a_root = project_root / "agents" / "triage"
sys.path.append(str(agent_a_root))

# Import the Engine from Agent A
# Import the Engine from Agent A
try:
    from agents.triage.src.services.classifier_service import ClassifierService
    from agents.triage.src.services.llm_service import LLMService
    from agents.triage.src.config import settings
except ImportError:
    # Fallback to local import if running in same context
    from src.services.classifier_service import ClassifierService
    from src.services.llm_service import LLMService
    from src.config import settings

class ServicesFactory:
    """
    Factory to instantiate shared services (The Engine) for Agent B.
    Ensures singletons where appropriate.
    """
    _classifier_instance = None
    _llm_instance = None

    @classmethod
    def get_llm_service(cls) -> LLMService:
        if not cls._llm_instance:
            # We assume Ollama is running locally as per .env
            cls._llm_instance = LLMService()
        return cls._llm_instance

    @classmethod
    def get_classifier_service(cls) -> ClassifierService:
        if not cls._classifier_instance:
            llm = cls.get_llm_service()
            cls._classifier_instance = ClassifierService(llm_service=llm)
        return cls._classifier_instance

# Global Accessors
def get_classifier():
    return ServicesFactory.get_classifier_service()

def get_llm_service():
    return ServicesFactory.get_llm_service()
