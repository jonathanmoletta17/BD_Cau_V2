
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.models.search.routes import router as search_router
from src.models.dashboard.routes import router as dashboard_router
from src.models.config.router import router as config_router

app = FastAPI(title="GLPI SIS Service", version="3.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(search_router)
app.include_router(dashboard_router)
app.include_router(config_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "glpi-sync-sis"}
