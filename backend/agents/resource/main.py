import sys
import os
import httpx
from fastapi import FastAPI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from packages.agent_adapter.wrapper import AgentverseWrapper

app = FastAPI(title="Resource Allocation Agent")
MEMORY_URL = os.getenv("MEMORY_URL", "http://localhost:8102/api/memory")
AGENT_NAME = "resource_allocator"
PORT = 8013

async def resource_logic(payload):
    crisis_id = payload.crisis_id
    
    # Read Shared Memory
    agent_outputs = {}
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{MEMORY_URL}/{crisis_id}")
            if resp.status_code == 200:
                agent_outputs = resp.json().get("agent_outputs", {})
    except Exception as e:
        print(f"Failed to read memory: {e}")

    findings = []
    recommendations = []
    
    if "financial" in agent_outputs:
        findings.append("Financial constraints identified from financial agent.")
        recommendations.append("Reallocate 15% of Q3 discretionary budget to emergency reserve.")
    else:
        findings.append("Standard budget reserves available.")
        
    if "supply_chain" in agent_outputs:
        findings.append("Supply chain disruptions noted.")
        recommendations.append("Authorize emergency procurement budget of up to $500k.")
        
    if "cyberagent" in agent_outputs or "cyber" in agent_outputs:
        findings.append("Cyber incident demands IT resources.")
        recommendations.append("Approve unlimited overtime for InfoSec and IT staff.")
        
    if not findings:
        findings.append("No specific agent constraints identified.")
        recommendations.append("Maintain standard resource allocation.")

    return (findings, recommendations, 0.85, 3)

try:
    AgentverseWrapper(app).register(
        agent_name=AGENT_NAME,
        port=PORT,
        capabilities=["Budget Allocation", "Staffing Suggestions", "ResourcesAllocated"],
        dependencies=[],
        legacy_handler=resource_logic
    )
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
