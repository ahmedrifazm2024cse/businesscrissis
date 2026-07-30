import sys
import os
import httpx
from fastapi import FastAPI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from packages.agent_adapter.wrapper import AgentverseWrapper

app = FastAPI(title="Notification Agent")
MEMORY_URL = os.getenv("MEMORY_URL", "http://localhost:8102/api/memory")
AGENT_NAME = "notification"
PORT = 8014

async def notification_logic(payload):
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

    severity = payload.severity
    findings = [f"Assessed notification requirements for {severity} crisis."]
    recommendations = []
    
    notify_executives = True
    notify_employees = False
    notify_customers = False
    
    if severity in ["HIGH", "CRITICAL"]:
        notify_employees = True
        
    if "customer_reputation" in agent_outputs or "cyberagent" in agent_outputs or "cyber" in agent_outputs:
        notify_customers = True
        
    if notify_customers:
        recommendations.append("Dispatch mass notification to all active customers via email and SMS.")
    if notify_employees:
        recommendations.append("Send urgent internal alert to all global staff.")
        
    recommendations.append("Ping C-Suite via priority paging system.")

    return (findings, recommendations, 0.99, 1)

try:
    AgentverseWrapper(app).register(
        agent_name=AGENT_NAME,
        port=PORT,
        capabilities=["Emergency Broadcast", "Stakeholder Alerts"],
        dependencies=[],
        legacy_handler=notification_logic
    )
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
