from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from models.cost_intelligence import (
    CostAnalysis, CostTrend, CostPrediction, BudgetMonitoring,
    CostRecommendation, CostAlert, CostHistory, CostAIAnalysis
)
from workflows.cost_monitor import run_cost_monitor

router = APIRouter(prefix="/cost", tags=["cost"])

@router.get("/dashboard", response_model=List[CostAnalysis])
async def get_cost_dashboard(skip: int = 0, limit: int = 50):
    return await CostAnalysis.find_all().sort("-date").skip(skip).limit(limit).to_list()

@router.get("/trends", response_model=List[CostTrend])
async def get_cost_trends(skip: int = 0, limit: int = 50):
    return await CostTrend.find_all().sort("-date").skip(skip).limit(limit).to_list()

@router.get("/predictions", response_model=List[CostPrediction])
async def get_cost_predictions(skip: int = 0, limit: int = 50):
    return await CostPrediction.find_all().sort("-predicted_at").skip(skip).limit(limit).to_list()

@router.get("/budget", response_model=List[BudgetMonitoring])
async def get_budget_monitoring(skip: int = 0, limit: int = 50):
    return await BudgetMonitoring.find_all().sort("-updated_at").skip(skip).limit(limit).to_list()

@router.get("/recommendations", response_model=List[CostRecommendation])
async def get_cost_recommendations(skip: int = 0, limit: int = 50):
    return await CostRecommendation.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.get("/alerts", response_model=List[CostAlert])
async def get_cost_alerts(skip: int = 0, limit: int = 50):
    return await CostAlert.find_all().sort("-created_at").skip(skip).limit(limit).to_list()

@router.get("/analysis", response_model=List[CostAIAnalysis])
async def get_cost_analysis(skip: int = 0, limit: int = 50):
    return await CostAIAnalysis.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.post("/analyze")
async def trigger_cost_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_cost_monitor)
    return {"message": "Cost Optimization Monitor started in background"}

@router.post("/simulate")
async def simulate_budget_overrun():
    """Injects a fake budget overrun by setting actual spend to a massive number."""
    bm = BudgetMonitoring(
        department="Transportation",
        allocated_budget=80000.0,
        actual_spend=950000.0, # Massive overrun
        variance=-870000.0,
        status="Over Budget"
    )
    await bm.insert()
    
    # Run the monitor to pick this up indirectly via alerts or just to demonstrate
    # Actually, we can just run the monitor to calculate a high total cost if we modify underlying data.
    # But since the monitor creates its own budget check based on live data, 
    # we can just insert this for the dashboard to see, and run the monitor so it fires its own.
    
    return {"message": "Injected critical budget overrun for Transportation. Dashboard updated."}
