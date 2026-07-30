from fastapi import APIRouter

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine, Base
from app.routers import market
from app.config.settings import settings

# Initialize database tables
Base.metadata.create_all(bind=engine)

router = APIRouter()

# Register routers
router.include_router(market.router)

@router.get("/")
def read_root():
    return {"message": "Market Intelligence Agent API is running."}

# --- Agentverse SDK Injection ---
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))
try:
    from packages.agent_adapter import AgentverseWrapper
    
    async def legacy_market_handler(payload):
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
            print(f"Market Agent failed to read memory: {e}")

        desc = payload.description.lower()
        
        findings = []
        recommendations = []
        risk_score = 4
        confidence = 0.88

        if "competitor" in desc or "market" in desc:
            findings.append("Primary competitors are launching aggressive ad campaigns capitalizing on our incident.")
            findings.append("Estimated 5% market share risk over the next quarter.")
            recommendations.append("Deploy targeted counter-marketing in key demographics.")
            risk_score = 7

        elif "data breach" in desc or "cyber" in desc:
            findings.append("Competitors in our sector have faced similar breaches; industry trust is generally low.")
            recommendations.append("Position the company as a leader in post-breach transparency.")
            risk_score = 6

        elif "supply" in desc or "delay" in desc:
            findings.append("Industry-wide supply constraints detected. Competitors are also delayed.")
            recommendations.append("Communicate that this is an industry-wide issue to deflect direct brand damage.")
            risk_score = 4

        else:
            findings.append("No immediate competitor exploitation detected.")
            recommendations.append("Maintain standard market monitoring.")

        # Collaborative check: Did customer agent find high risk?
        cust_out = agent_outputs.get("customer_reputation", {})
        if cust_out.get("risk_score", 0) > 7:
            findings.append("High customer risk noted. Market share highly vulnerable.")
            recommendations.append("Accelerate customer retention programs to prevent churn to competitors.")
            risk_score += 2

        return (findings, recommendations, confidence, min(10, risk_score))

    AgentverseWrapper(router).register(
        agent_name="market_intelligence",
        port=8001,
        capabilities=["Market Trend Prediction", "Competitor Risk"],
        dependencies=[],
        legacy_handler=legacy_market_handler
    )
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")

