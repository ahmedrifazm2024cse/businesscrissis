import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.domain import (
    User, Incident, Workflow, AgentResult, Report,
    Notification, ChatHistory, BusinessMetric, AuditLog, SystemSetting
)

logger = logging.getLogger(__name__)

async def init_db():
    try:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        client = AsyncIOMotorClient(mongodb_uri)
        
        # Initialize Beanie with our models
        await init_beanie(
            database=client.agentverse,
            document_models=[
                User,
                Incident,
                Workflow,
                AgentResult,
                Report,
                Notification,
                ChatHistory,
                BusinessMetric,
                AuditLog,
                SystemSetting
            ]
        )
        
        logger.info(f"Connected to MongoDB at {mongodb_uri.split('@')[-1] if '@' in mongodb_uri else mongodb_uri} and initialized Beanie")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
