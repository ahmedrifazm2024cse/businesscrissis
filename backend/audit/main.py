from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any
import datetime
import uuid

app = FastAPI(title="Audit & Compliance Service", version="1.0.0")

class AuditEvent(BaseModel):
    actor: str
    action: str
    resource: str
    details: Dict[str, Any]

audit_log = []

def write_to_immutable_log(event: AuditEvent):
    # In production, this would write to a WORM (Write Once Read Many) drive or blockchain ledger
    record = {
        "audit_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        **event.dict()
    }
    audit_log.append(record)
    print(f"AUDIT LOGGED: {record}")

@app.post("/api/audit/log")
async def log_action(event: AuditEvent, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_to_immutable_log, event)
    return {"status": "queued"}

@app.get("/api/audit/history")
async def get_history():
    return {"logs": audit_log[-100:]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8106, reload=True)
