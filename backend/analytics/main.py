from fastapi import FastAPI
import random

app = FastAPI(title="Analytics Service", version="1.0.0")

@app.get("/api/analytics/risk-trends")
async def get_risk_trends():
    return {
        "trend_data": [
            {"time": f"0{i}:00", "risk": random.randint(20, 90)}
            for i in range(8, 15)
        ]
    }

@app.get("/api/analytics/agent-utilization")
async def get_utilization():
    return {
        "decision": 85,
        "market": 45,
        "customer": 12,
        "supply": 92
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8108, reload=True)
