from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.models import EventPayload

app = FastAPI(title="Event Bus Service", version="1.0.0")

# In-memory event store for MVP pub/sub
# In production, this would be Redis Pub/Sub, Kafka, or RabbitMQ
events_store: List[EventPayload] = []

@app.post("/api/eventbus/publish")
async def publish_event(event: EventPayload):
    events_store.append(event)
    print(f"[EventBus] Published: {event.event_type} by {event.publisher}")
    return {"status": "published", "event_id": event.event_id}

@app.get("/api/eventbus/events", response_model=List[EventPayload])
async def get_events(limit: int = 100):
    return events_store[-limit:]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8101, reload=True)
