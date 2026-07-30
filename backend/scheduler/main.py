from fastapi import FastAPI
import asyncio
import datetime

app = FastAPI(title="Scheduler Service", version="1.0.0")

# Background task placeholder
async def run_daily_reports():
    while True:
        print(f"[{datetime.datetime.utcnow()}] Running scheduled jobs...")
        await asyncio.sleep(86400) # Wait 24 hours

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_daily_reports())

@app.get("/api/scheduler/status")
async def get_status():
    return {"status": "running", "next_job": "daily_report_generation"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8107, reload=True)
