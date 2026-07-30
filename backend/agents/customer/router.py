from fastapi import APIRouter

from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import init_db
from api.routers import coordinator, websockets
from core.scheduler import start_scheduler
import logging
import sys
import asyncio
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def validate_apis():
    logger.info("Validating external API configurations...")
    
    async def check_api(name, url, params=None):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code in [200, 400, 401, 403]: 
                    if resp.status_code == 200:
                        data = resp.json()
                        if "error_message" in data:
                            logger.error(f"? {name} API Key invalid: {data['error_message']}")
                            return False
                        logger.info(f"? {name} API is configured and reachable.")
                        return True
                    else:
                        logger.error(f"? {name} API Key invalid (HTTP {resp.status_code})")
                        return False
        except Exception as e:
            logger.error(f"? {name} API connection failed: {e}")
            return False

    results = await asyncio.gather(
        check_api("OpenWeather", "https://api.openweathermap.org/data/2.5/weather", {"q": "London", "appid": settings.WEATHER_API_KEY}),
        check_api("OpenRouteService", "https://api.openrouteservice.org/v2/directions/driving-car", {"api_key": settings.OPENROUTESERVICE_API_KEY, "start": "8.681495,49.41461", "end": "8.687872,49.420318"}),
        check_api("NewsAPI", "https://newsapi.org/v2/everything", {"q": "supply chain", "apiKey": settings.NEWS_API_KEY}),
        check_api("ExchangeRate", f"https://v6.exchangerate-api.com/v6/{settings.EXCHANGE_RATE_API_KEY}/latest/USD")
    )
    
    if not all(results):
        logger.warning("?? Some external APIs failed validation. The system will rely on AI estimations and cached fallback data.")
    else:
        logger.info("? All external API configurations validated successfully.")
    
    logger.info("? Core configurations validated.")

@asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("Starting up Autonomous Business Crisis Commander...")
#     try:
#         await validate_apis()
#     except Exception as e:
#         logger.critical(f"Failed to validate configurations: {e}")
#         sys.exit(1)
#         
#     await init_db()
#     start_scheduler()
#     yield

router = APIRouter()

from api.routers import coordinator, websockets, inventory, forecast, supplier, shipment, warehouse, procurement, cost, route, shortage, intelligence

router.include_router(coordinator.router, prefix=settings.API_V1_STR)
router.include_router(inventory.router, prefix=settings.API_V1_STR)
router.include_router(forecast.router, prefix=settings.API_V1_STR)
router.include_router(supplier.router, prefix=settings.API_V1_STR)
router.include_router(shipment.router, prefix=settings.API_V1_STR)
router.include_router(warehouse.router, prefix=settings.API_V1_STR)
router.include_router(procurement.router, prefix=settings.API_V1_STR)
router.include_router(cost.router, prefix=settings.API_V1_STR)
router.include_router(route.router, prefix=settings.API_V1_STR)
router.include_router(shortage.router, prefix=settings.API_V1_STR)
router.include_router(intelligence.router, prefix=settings.API_V1_STR)
router.include_router(websockets.router)

@router.get("/")
async def root():
    return {"message": "Welcome to ABCC API"}

# --- Agentverse SDK Injection ---
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))
try:
    from packages.agent_adapter import AgentverseWrapper
    
    async def legacy_customer_handler(payload):
        import httpx
        # Read from shared memory
        memory_url = os.getenv("MEMORY_URL", "http://localhost:8102/api/memory")
        crisis_id = payload.crisis_id
        agent_outputs = {}
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{memory_url}/{crisis_id}")
                if resp.status_code == 200:
                    agent_outputs = resp.json().get("agent_outputs", {})
        except Exception as e:
            print(f"Customer Rep Agent failed to read memory: {e}")

        desc = payload.description.lower()
        severity = payload.severity

        # Intelligent Simulation Logic
        findings = []
        recommendations = []
        risk_score = 3
        confidence = 0.85

        # Heuristics based on keywords
        if "data breach" in desc or "cyber" in desc or "hack" in desc:
            findings.append("Customer sentiment is sharply declining due to privacy concerns (-45% in 2 hours).")
            findings.append("High volume of account deletion requests detected on social media.")
            recommendations.append("Immediately offer 12 months of free credit monitoring to all affected users.")
            recommendations.append("Draft proactive apology emphasizing data encryption standards.")
            risk_score = 9 if severity == "CRITICAL" else 7
            confidence = 0.95

        elif "recall" in desc or "defect" in desc:
            findings.append("Negative reviews spiking on major retail channels regarding product safety.")
            findings.append("Brand trust index dropped by 12 points.")
            recommendations.append("Announce a frictionless, no-questions-asked refund policy.")
            risk_score = 8
            confidence = 0.90

        elif "delay" in desc or "supply" in desc or "shortage" in desc:
            findings.append("Customer frustration increasing over unfulfilled orders.")
            recommendations.append("Send proactive delay notification emails with 15% discount codes for future purchases.")
            risk_score = 5
            confidence = 0.92

        else:
            findings.append("Baseline sentiment stable, but monitoring active keywords.")
            recommendations.append("Maintain standard social media engagement protocol.")

        return (findings, recommendations, confidence, risk_score)

    AgentverseWrapper(router).register(
        agent_name="customer_reputation",
        port=8006,
        capabilities=["Reputation Score", "Brand Sentiment"],
        dependencies=[],
        legacy_handler=legacy_customer_handler
    )
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")
