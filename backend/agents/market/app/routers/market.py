from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.market import (
    MarketAnalysisResponse, DashboardDataResponse,
    RiskDetailsResponse, OpportunityDetailsResponse,
    CrisisAnalysisRequest, CrisisAnalysisResponse
)
from app.services.agent_service import execute_market_analysis, get_latest_report
from app.services.analytics import calculate_market_scores
from app.services.forecasting import forecast_demand
from app.utils.data_loader import (
    load_competitors, load_market_news, load_pricing, load_industry_trends
)
from typing import Dict, Any, List
import json
import time
import asyncio

router = APIRouter(prefix="/api/market", tags=["market"])

@router.get("/status")
def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok", "service": "Market Intelligence Agent API", "ts": time.time()}

@router.get("/agent-logs")
async def stream_agent_logs():
    """
    SSE endpoint that streams live agent log entries to the frontend.
    Clients receive a continuous stream of JSON-encoded log events.
    """
    from app.agents.crew import get_logs, is_agent_running

    async def event_generator():
        sent_count = 0
        # Immediate heartbeat so connection opens fast
        yield "data: {\"type\": \"heartbeat\"}\n\n"
        while True:
            logs = get_logs()
            new_logs = logs[sent_count:]
            for entry in new_logs:
                yield f"data: {json.dumps(entry)}\n\n"
                sent_count += 1
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@router.post("/agent-logs/clear")
def clear_agent_logs():
    """Clear the agent log queue."""
    from app.agents.crew import clear_logs
    clear_logs()
    return {"cleared": True}

@router.get("/dashboard", response_model=DashboardDataResponse)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    latest = get_latest_report(db)
    scores = calculate_market_scores()
    forecast = forecast_demand()
    
    competitors = load_competitors().to_dict(orient="records")
    news = load_market_news().to_dict(orient="records")
    pricing = load_pricing().to_dict(orient="records")
    trends = load_industry_trends().to_dict(orient="records")
    
    return {
        "marketRiskScore": latest.market_risk_score,
        "competitorThreat": latest.competitor_threat,
        "marketOpportunity": latest.market_opportunity,
        "demandForecastSummary": latest.demand_forecast,
        "confidence": latest.confidence,
        "competitors": competitors,
        "news": news,
        "pricing": pricing,
        "trends": trends,
        "demandForecast": {
            "historical": forecast["historical"],
            "forecast": forecast["forecast"],
            "message": forecast["message"]
        },
        "recommendations": latest.recommendations
    }

@router.get("/report")
def get_full_report(db: Session = Depends(get_db)):
    latest = get_latest_report(db)
    return {
        "id": latest.id,
        "timestamp": latest.timestamp,
        "agent": "Market Intelligence",
        "marketRiskScore": latest.market_risk_score,
        "competitorThreat": latest.competitor_threat,
        "marketOpportunity": latest.market_opportunity,
        "demandForecast": latest.demand_forecast,
        "confidence": latest.confidence,
        "keyFindings": latest.key_findings,
        "recommendations": latest.recommendations
    }

@router.get("/risk", response_model=RiskDetailsResponse)
def get_risk_details(db: Session = Depends(get_db)):
    scores = calculate_market_scores()
    return {
        "overallScore": scores["marketRiskScore"],
        "competitorThreatScore": scores["competitorThreatScore"],
        "economicRiskScore": scores["economicRiskScore"],
        "demandRiskScore": scores["demandRiskScore"],
        "riskFactors": scores["riskFactors"]
    }

@router.get("/opportunities", response_model=OpportunityDetailsResponse)
def get_opportunity_details(db: Session = Depends(get_db)):
    scores = calculate_market_scores()
    return {
        "overallOpportunityScore": scores["opportunityScore"],
        "opportunities": scores["opportunities"]
    }

@router.post("/analyze", response_model=MarketAnalysisResponse)
def run_analysis(db: Session = Depends(get_db)):
    try:
        report = execute_market_analysis(db)
        return {
            "agent": "Market Intelligence",
            "marketRiskScore": report.market_risk_score,
            "competitorThreat": report.competitor_threat,
            "marketOpportunity": report.market_opportunity,
            "demandForecast": report.demand_forecast,
            "confidence": report.confidence,
            "keyFindings": report.key_findings,
            "recommendations": report.recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute analysis: {str(e)}")

@router.post("/crisis-analyze", response_model=CrisisAnalysisResponse)
def analyze_crisis_simulation(request: CrisisAnalysisRequest):
    try:
        from app.agents.crew import run_crisis_intelligence_crew
        crisis_data = request.model_dump()
        result = run_crisis_intelligence_crew(crisis_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute crisis analysis: {str(e)}")
