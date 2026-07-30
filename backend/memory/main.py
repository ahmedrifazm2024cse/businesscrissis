from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.models import MemorySchema, TimelineEvent

app = FastAPI(title="Shared Memory Service", version="1.0.0")

# In-memory storage for crisis state
memory_store: Dict[str, MemorySchema] = {}

@app.post("/api/memory/initialize")
async def init_memory(crisis_id: str, conversation_id: str):
    if crisis_id in memory_store:
        raise HTTPException(status_code=400, detail="Crisis memory already initialized")
    
    memory_store[crisis_id] = MemorySchema(
        crisis_id=crisis_id,
        conversation_id=conversation_id,
        timeline=[],
        agent_outputs={}
    )
    return {"status": "initialized", "crisis_id": crisis_id}

@app.get("/api/memory/{crisis_id}", response_model=MemorySchema)
async def get_memory(crisis_id: str):
    if crisis_id not in memory_store:
        raise HTTPException(status_code=404, detail="Crisis memory not found")
    return memory_store[crisis_id]

@app.post("/api/memory/{crisis_id}/append_timeline")
async def append_timeline(crisis_id: str, event: TimelineEvent):
    if crisis_id not in memory_store:
        raise HTTPException(status_code=404, detail="Crisis memory not found")
    
    memory_store[crisis_id].timeline.append(event)
    return {"status": "success"}

@app.post("/api/memory/{crisis_id}/append_output")
async def append_agent_output(crisis_id: str, agent_name: str, payload: Dict[str, Any]):
    if crisis_id not in memory_store:
        raise HTTPException(status_code=404, detail="Crisis memory not found")
    
    if agent_name in memory_store[crisis_id].agent_outputs:
        raise HTTPException(status_code=400, detail="Overwriting agent output is prohibited")
        
    memory_store[crisis_id].agent_outputs[agent_name] = payload
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8102, reload=True)
