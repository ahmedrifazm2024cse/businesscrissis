import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

# Ensure the root project directory is in the sys path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from app.database.mongodb import init_db
from app.api.main import api_router
from app.websocket.manager import manager
from app.middleware.logging import LoggingMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing Autonomous Business Commander AI...")
    
    # Initialize unified database connection
    app.state.db_client = await init_db()
    
    logger.info("Database initialized successfully.")
    
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

# Custom Logging Middleware
app.add_middleware(LoggingMiddleware)

# Include the main API router
app.include_router(api_router, prefix="/api")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WS messages if needed
    except Exception as e:
        logger.info(f"WebSocket disconnected: {e}")
    finally:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Welcome to the Autonomous Business Commander AI.",
        "version": "2.0"
    }

@app.get("/api/health")
async def get_health():
    return {
        "status": "online",
        "commander": "active",
        "agents_registered": 13
    }

if __name__ == "__main__":
    import uvicorn
    # Make sure we run from the backend directory context
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
