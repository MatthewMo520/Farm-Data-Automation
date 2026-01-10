"""
Farm Data Automation - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from backend.api import recordings, health, clients, schema_mappings, auth
from backend.core.config import settings
from backend.core.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting up Farm Data Automation API...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Farm Data Automation API...")


app = FastAPI(
    title="Farm Data Automation API",
    description="ML/AI data processing agent for agricultural voice recordings",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(recordings.router, prefix="/api/v1", tags=["recordings"])
app.include_router(clients.router, prefix="/api/v1", tags=["clients"])
app.include_router(schema_mappings.router, prefix="/api/v1", tags=["schema-mappings"])

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")


@app.get("/")
async def root():
    """Serve frontend dashboard"""
    frontend_html = frontend_path / "templates" / "index.html"
    if frontend_html.exists():
        return FileResponse(frontend_html)
    else:
        return {
            "message": "Farm Data Automation API",
            "version": "0.1.0",
            "status": "running"
        }


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Farm Data Automation API",
        "version": "0.1.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
