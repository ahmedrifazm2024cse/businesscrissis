import sys
import os
import httpx
from fastapi import FastAPI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from packages.agent_adapter.wrapper import AgentverseWrapper

app = FastAPI(title="Communication & PR Agent")
MEMORY_URL = os.getenv("MEMORY_URL", "http://localhost:8102/api/memory")
AGENT_NAME = "communication_pr"
PORT = 8012

async def pr_logic(payload):
    crisis_id = payload.crisis_id
    
    # Read Shared Memory
    context = {}
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{MEMORY_URL}/{crisis_id}")
            if resp.status_code == 200:
                context = resp.json()
    except Exception as e:
        print(f"Failed to read memory: {e}")
        
    severity = payload.severity
    desc = payload.description
    
    findings = ["Drafted comprehensive communication suite."]
    recommendations = [
        "Publish Social Media Statement immediately.", 
        "Send Customer Email within 1 hour.",
        "Hold Press Release until CEO approval."
    ]
    
    # Generated Assets based on workflow results
    data = {
        "customer_email": f"Subject: Important Update Regarding {desc[:20]}...\nDear Customer, we are actively addressing the situation. Your data/service is our priority.",
        "press_release": f"FOR IMMEDIATE RELEASE: The company is responding to a {severity} level incident involving {desc}. We have activated our Enterprise Multi-Agent AI Platform to resolve the crisis.",
        "internal_memo": f"To All Staff: Please be advised of a {severity} incident. Do not speak to media. Direct all inquiries to PR.",
        "social_media": f"We are aware of the current issues and are working rapidly to resolve them. Thank you for your patience. #Update",
        "ceo_brief": f"CEO Briefing: Crisis ID {crisis_id} ({severity}). System is orchestrating mitigation. PR assets are prepared."
    }
    
    return (findings, recommendations, 0.90, 2)

try:
    AgentverseWrapper(app).register(
        agent_name=AGENT_NAME,
        port=PORT,
        capabilities=["Press Release Generation", "Internal Comms", "CommunicationPrepared"],
        dependencies=[],
        legacy_handler=pr_logic
    )
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
