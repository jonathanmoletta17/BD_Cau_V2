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

