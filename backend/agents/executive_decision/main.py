import sys, os
import httpx
from fastapi import FastAPI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from packages.agent_adapter.wrapper import AgentverseWrapper

app = FastAPI(title="Executive Decision Agent")

AGENT_NAME = "executive_decision"
PORT = 8010
CAPABILITIES = ["Global Risk Aggregation", "Strategic Planning", "ExecutiveDecisionReady"]
MEMORY_URL = os.getenv("MEMORY_URL", "http://localhost:8102/api/memory")

async def decision_logic(payload):
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
        
    findings = [f"Synthesized inputs from {len(agent_outputs)} agents."]
    recommendations = []
    
    # Simple resolution logic: compile priorities
    if "cyberagent" in agent_outputs or "cyber" in agent_outputs:
        recommendations.append("Immediate Action: Isolate affected network partitions and rotate credentials.")
    if "financial" in agent_outputs:
        recommendations.append("Immediate Action: Freeze vulnerable assets and audit exposure.")
    if "customer_reputation" in agent_outputs:
        recommendations.append("Immediate Action: Dispatch holding statement to key clients.")
    if "supply_chain" in agent_outputs:
        recommendations.append("Immediate Action: Reroute logistics to secondary suppliers.")
        
    if not recommendations:
        recommendations.append("Immediate Action: Convene emergency crisis committee.")

    return (
        findings,
        recommendations,
        0.95, # Confidence
        9 if payload.severity == "CRITICAL" else 5 # Risk Score
    )

AgentverseWrapper(app).register(
    agent_name=AGENT_NAME,
    port=PORT,
    capabilities=CAPABILITIES,
    dependencies=[],
    legacy_handler=decision_logic
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
