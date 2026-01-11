from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    db.connect()
    is_connected = await db.verify_connectivity()
    if is_connected:
        logger.info("Successfully connected to Neo4j.")
    else:
        logger.error("Failed to connect to Neo4j on startup.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

from app.api.api import api_router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify backend and database status."""
    is_db_connected = await db.verify_connectivity()
    status = "ok" if is_db_connected else "degraded"
    return {
        "status": status,
        "db": "connected" if is_db_connected else "disconnected",
        "version": "0.3"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
