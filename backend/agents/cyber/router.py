from fastapi import APIRouter

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Append paths so we can import the agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.cyber_agent import analyze_cyber_crisis
from schemas.models import CybersecurityAnalysisSchema

router = APIRouter()

class AnalyzeRequest(BaseModel):
    incident_description: str

@router.post("/analyze", response_model=CybersecurityAnalysisSchema)
def analyze_incident(req: AnalyzeRequest):
    # This calls your crewai agent function
    analysis = analyze_cyber_crisis(req.incident_description)
    return analysis

# --- Agentverse SDK Injection ---
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))
try:
    from packages.agent_adapter import AgentverseWrapper
    
    async def legacy_cyber_handler(payload):
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
            print(f"Cyber Agent failed to read memory: {e}")

        desc = payload.description.lower()
        
        findings = []
        recommendations = []
        risk_score = 1
        confidence = 0.95

        if "ransomware" in desc or "hack" in desc or "breach" in desc or "cyber" in desc:
            findings.append("Critical network intrusion detected across main database partitions.")
            findings.append("Active exfiltration of customer PII is highly probable.")
            recommendations.append("Execute immediate server isolation protocol (Code Red).")
            recommendations.append("Initiate forced password resets for all administrative accounts.")
            risk_score = 10
            
        elif "ddos" in desc or "offline" in desc or "down" in desc:
            findings.append("Unusual volumetric traffic spiking originating from multiple botnets.")
            recommendations.append("Activate Edge network rate limiting and DDoS scrubbing centers.")
            risk_score = 7
            
        else:
            findings.append("No active cyber threats detected linked to current crisis.")
            recommendations.append("Maintain baseline SOC monitoring.")

        return (findings, recommendations, confidence, risk_score)

    AgentverseWrapper(router).register(
        agent_name="cyber",
        port=8004,
        capabilities=["Threat Detection", "Data Breach Analysis"],
        dependencies=[],
        legacy_handler=legacy_cyber_handler
    )
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")
