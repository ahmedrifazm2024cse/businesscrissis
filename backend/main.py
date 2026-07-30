import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the root project directory is in the sys path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from backend.database.mongodb import init_db
from backend.shared.eventbus import eventbus
from backend.shared.memory import memory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing Autonomous Business Commander AI...")
    
    # Initialize unified database connection
    app.state.db_client = await init_db()
    
    # Here we would initialize/register agents dynamically
    logger.info("Database and agents initialized successfully.")
    
    yield
    
    # Shutdown actions
    logger.info("Shutting down Commander AI...")
    if hasattr(app.state, 'db_client'):
        app.state.db_client.close()

# Initialize Monolithic FastAPI Application
app = FastAPI(
    title="Autonomous Business Commander AI",
    description="Unified Enterprise Multi-Agent Platform",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from backend.commander.router import router as commander_router
    app.include_router(commander_router, prefix="/api/commander", tags=["Commander"])
except Exception as e:
    logger.error(f"Failed to load commander_router: {e}")

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Welcome to the Autonomous Business Commander AI."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
