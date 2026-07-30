import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

logger = logging.getLogger(__name__)

async def init_db():
    try:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        client = AsyncIOMotorClient(mongodb_uri)
        
        # Initialize Beanie with our models
        from backend.database.models import User, AgentRegistry, WorkflowHistory, KnowledgeItem, Report
        await init_beanie(
            database=client.agentverse,
            document_models=[
                User,
                AgentRegistry,
                WorkflowHistory,
                KnowledgeItem,
                Report
            ]
        )
        
        logger.info(f"Connected to MongoDB at {mongodb_uri.split('@')[-1] if '@' in mongodb_uri else mongodb_uri} and initialized Beanie")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
