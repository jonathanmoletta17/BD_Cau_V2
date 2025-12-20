from typing import List
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from src.config import settings
from src.utils.logging import setup_logger
from src.models import ClassificationRequest, ClassificationResponse, ChatMessage
from src.services.glpi_client import GLPIClient
from src.services.sync_service import SyncService
from src.services.llm_service import LLMService
from src.services.classifier_service import ClassifierService
from src.services.chat_service import ChatService

logger = setup_logger("glpi_agent_main")

# --- Dependency Container (Simple Manual Injection) ---
class Container:
    glpi_client = GLPIClient()
    llm_service = LLMService()
    
    sync_service = SyncService(glpi_client)
    classifier_service = ClassifierService(llm_service)
    chat_service = ChatService(llm_service, classifier_service)

container = Container()

# --- Lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting GLPI Agent V2 (Full Context Architecture)...")
    logger.info(f"Environment: {settings.ENV}")
    
    # Initial Sync
    try:
        await container.sync_service.sync_categories()
    except Exception as e:
        logger.error(f"Startup sync failed: {e}")
    
    yield
    
    logger.info("Shutting down GLPI Agent V2...")

app = FastAPI(title="GLPI AI Agent V2", lifespan=lifespan)

# --- Endpoints ---
@app.get("/health")
def health_check():
    """
    K8s/Docker Health Probe.
    """
    total_cats = len(container.sync_service.categories)
    return {
        "status": "healthy", 
        "version": "2.1.0-fullcontext",
        "ready": total_cats > 0,
        "details": {
            "loaded_categories": total_cats,
            "architecture": "Full Context (No RAG)"
        }
    }

@app.post("/classify", response_model=ClassificationResponse)
async def classify_ticket(request: ClassificationRequest):
    """
    Classify a ticket description into a GLPI Category using Full Context LLM.
    """
    try:
        result = await container.classifier_service.classify(request)
        return result
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(history: List[ChatMessage], session_id: str = "api_client"):
    """
    Conversational endpoint. Sends message history, returns Assistant response + actions.
    """
    try:
        return await container.chat_service.handle_message(history, session_id)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
