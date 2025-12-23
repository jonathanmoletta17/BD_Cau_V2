from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from src.core.database import SessionLocal
from src.models.dashboard.routes import router as dashboard_router
from src.models.metadata.router import router as metadata_router
from src.models.quality.routes import router as quality_router
from src.models.config.router import router as config_router
from src.models.search.routes import router as search_router
from src.services.quality.monitor import QualityMonitor

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GLPI DTIC Service", version="3.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scheduler configuration
scheduler = BackgroundScheduler()

def run_quality_checks_job():
    """Job to run quality checks periodically"""
    try:
        logger.info("Scheduler: Starting quality checks...")
        with SessionLocal() as db:
            monitor = QualityMonitor(db)
            monitor.run_all_checks()
        logger.info("Scheduler: Quality checks completed.")
    except Exception as e:
        logger.error(f"Scheduler Error: {str(e)}")

@app.on_event("startup")
async def startup_event():
    # Start scheduler
    if not scheduler.running:
        trigger = CronTrigger(hour='*', minute=0)  # Every hour
        scheduler.add_job(
            run_quality_checks_job,
            trigger=trigger,
            id='quality_monitor',
            replace_existing=True,
            name='Monitoramento de Qualidade GLPI'
        )
        scheduler.start()
        logger.info("APScheduler started with quality_monitor job (hourly)")

@app.on_event("shutdown")
async def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shut down")

# Routers
app.include_router(dashboard_router, prefix="/dtic")
app.include_router(metadata_router, prefix="/dtic")
app.include_router(quality_router, prefix="/dtic")
app.include_router(config_router, prefix="/dtic")
app.include_router(search_router, prefix="/dtic")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "glpi-sync-dtic"}
