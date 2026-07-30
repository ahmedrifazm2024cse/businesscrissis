from contextlib import asynccontextmanager
from fastapi import FastAPI
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
async def lifespan(app: FastAPI):
    logger.info("Starting up Autonomous Business Crisis Commander...")
    try:
        await validate_apis()
    except Exception as e:
        logger.critical(f"Failed to validate configurations: {e}")
        sys.exit(1)
        
    await init_db()
    start_scheduler()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.routers import coordinator, websockets, inventory, forecast, supplier, shipment, warehouse, procurement, cost, route, shortage, intelligence

app.include_router(coordinator.router, prefix=settings.API_V1_STR)
app.include_router(inventory.router, prefix=settings.API_V1_STR)
app.include_router(forecast.router, prefix=settings.API_V1_STR)
app.include_router(supplier.router, prefix=settings.API_V1_STR)
app.include_router(shipment.router, prefix=settings.API_V1_STR)
app.include_router(warehouse.router, prefix=settings.API_V1_STR)
app.include_router(procurement.router, prefix=settings.API_V1_STR)
app.include_router(cost.router, prefix=settings.API_V1_STR)
app.include_router(route.router, prefix=settings.API_V1_STR)
app.include_router(shortage.router, prefix=settings.API_V1_STR)
app.include_router(intelligence.router, prefix=settings.API_V1_STR)
app.include_router(websockets.router)

@app.get("/")
async def root():
    return {"message": "Welcome to ABCC API"}

# --- Agentverse SDK Injection ---
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))
try:
    from packages.agent_adapter import AgentverseWrapper
    
    async def legacy_supply_handler(payload):
        import httpx
        memory_url = os.getenv("MEMORY_URL", "http://localhost:8102/api/memory")
        crisis_id = payload.crisis_id
        agent_outputs = {}
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{memory_url}/{crisis_id}")
                if resp.status_code == 200:
                    agent_outputs = resp.json().get("agent_outputs", {})
        except Exception as e:
            print(f"Supply Agent failed to read memory: {e}")

        desc = payload.description.lower()
        
        findings = []
        recommendations = []
        risk_score = 3
        confidence = 0.85

        if "disaster" in desc or "weather" in desc or "strike" in desc:
            findings.append("Primary logistics routes severely impacted by external events.")
            findings.append("Tier 1 supplier availability dropped to 40%.")
            recommendations.append("Immediately route production to Tier 2 backup suppliers in unaffected regions.")
            recommendations.append("Air-freight critical inventory to prevent complete stockout.")
            risk_score = 9

        elif "delay" in desc or "shortage" in desc or "recall" in desc:
            findings.append("Inventory levels for affected SKU have reached critical minimums (2 days remaining).")
            recommendations.append("Halt all non-essential fulfillment to prioritize enterprise clients.")
            risk_score = 7
            
        elif "cyber" in desc or "ransomware" in desc:
            findings.append("Logistics API gateways compromised; automated shipping manifest generation is down.")
            recommendations.append("Switch to manual waybill processing until IT gives all-clear.")
            risk_score = 6

        else:
            findings.append("No immediate physical supply chain disruption detected.")
            recommendations.append("Maintain standard Just-In-Time (JIT) inventory levels.")

        return (findings, recommendations, confidence, risk_score)

    AgentverseWrapper(app).register(
        agent_name="supply_chain",
        port=8005,
        capabilities=["Inventory Shortage", "Logistics Impact"],
        dependencies=[],
        legacy_handler=legacy_supply_handler
    )
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
