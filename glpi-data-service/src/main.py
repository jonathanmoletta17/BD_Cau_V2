"""
GLPI Data Service V3
Clean, simplified architecture with vertical slices
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.core import config
from src.modules.dtic.dashboard import router as dashboard_router
from src.modules.dtic.search import router as search_router
from src.modules.sis.dashboard import router as sis_dashboard_router
from src.modules.sis.search import router as sis_search_router
from src.modules.sis.carregadores import router as sis_carregadores_router
from src.modules.sis.config import router as sis_config_router
from src.modules.sis.smart_search import router as sis_smart_search_router
# OPTIONAL: knowledge module requires pgvector extension (not available in apt)
# To enable: compile pgvector from source and uncomment below
# from src.modules.dtic.knowledge.router import router as knowledge_router
from src.modules.dtic.tickets.analysis_routes import router as analysis_router
from src.core.database import Database, Base
from sqlalchemy import text

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GLPI Data Service V3",
    description="Clean architecture with vertical slices for DTIC and SIS contexts",
    version="3.0.0"
)

# Startup Event: Init DB
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Database...")
    Database._initialize()
    engine = Database._engine
    
    with engine.connect() as conn:
        # 1. Create schemas if they don't exist
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS dtic"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS sis"))
        conn.commit()
        
        # 2. Enable pgvector extension (may not be available in all environments)
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        except Exception as e:
            logger.warning(f"pgvector extension not available: {e}")
    
    # 3. Create tables (if they don't exist)
    # Note: In DTICuction we use Alembic, here for simplicity we use create_all
    # We must import models so Base knows about them
    # OPTIONAL: KnowledgeEntry requires pgvector extension
    # from src.modules.dtic.knowledge.models import KnowledgeEntry
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized (Knowledge/RAG module optional - install pgvector to enable).")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1") # Advanced Analysis
# OPTIONAL: knowledge router requires pgvector
# app.include_router(knowledge_router, prefix="/api/v1") # RAG Support
app.include_router(sis_dashboard_router, prefix="/api/v1")
app.include_router(sis_search_router, prefix="/api/v1")
app.include_router(sis_carregadores_router, prefix="/api/v1")
app.include_router(sis_config_router, prefix="/api/v1")
app.include_router(sis_smart_search_router, prefix="/api/v1/sis")

# Health check
@app.get("/health")
async def health():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "architecture": "vertical-slices"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "GLPI Data Service V3",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/health"
    }

logger.info("🚀 GLPI Data Service V3 started (Clean Architecture)")
for route in app.routes:
    logger.info(f"Route: {route.path} {route.name}")

