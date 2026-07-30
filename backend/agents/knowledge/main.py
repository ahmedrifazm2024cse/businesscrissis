import sys
import os
import json
import httpx
from fastapi import FastAPI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from packages.agent_adapter.wrapper import AgentverseWrapper

app = FastAPI(title="Knowledge Manager Agent")
MEMORY_URL = os.getenv("MEMORY_URL", "http://localhost:8102/api/memory")
AGENT_NAME = "knowledge_manager"
PORT = 8016
DB_FILE = os.path.join(os.path.dirname(__file__), "knowledge_base.json")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"crises": []}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

async def knowledge_logic(payload):
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

    db = load_db()
    
    # Store this crisis
    crisis_record = {
        "crisis_id": crisis_id,
        "description": payload.description,
        "severity": payload.severity,
        "context": context
    }
    
    # Update if exists, else append
    existing = next((c for c in db["crises"] if c["crisis_id"] == crisis_id), None)
    if existing:
        existing.update(crisis_record)
    else:
        db["crises"].append(crisis_record)
    
    save_db(db)

    # Search for similar past crises
    desc_words = set(payload.description.lower().split())
    similar_crises = []
    
    for past in db["crises"]:
        if past["crisis_id"] == crisis_id:
            continue
        past_words = set(past["description"].lower().split())
        overlap = len(desc_words.intersection(past_words))
        if overlap > 2:
            similar_crises.append(past["crisis_id"])

    findings = [f"Stored current crisis '{crisis_id}' into knowledge base."]
    recommendations = []
    
    if similar_crises:
        findings.append(f"Found {len(similar_crises)} similar past incidents.")
        recommendations.append(f"Review historical playbook from {similar_crises[0]}.")
    else:
        findings.append("No directly similar past incidents found.")
        recommendations.append("Establish new playbook baseline for this incident type.")

    return (findings, recommendations, 0.95, 2)

try:
    AgentverseWrapper(app).register(
        agent_name=AGENT_NAME,
        port=PORT,
        capabilities=["Historical Context Search", "KnowledgeUpdated"],
        dependencies=[],
        legacy_handler=knowledge_logic
    )
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
