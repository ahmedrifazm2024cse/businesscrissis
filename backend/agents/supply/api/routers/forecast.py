from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from datetime import datetime
from models.forecast import (
    ForecastResult, ForecastHistory, ForecastRecommendation,
    ForecastAlert, ForecastAccuracy
)
from workflows.forecast_monitor import run_forecast_monitor

router = APIRouter(prefix="/forecast", tags=["forecast"])

@router.get("", response_model=List[ForecastResult])
async def get_forecasts(
    skip: int = Query(0, ge=0), 
    limit: int = Query(50, ge=1, le=100),
    sku: Optional[str] = None
):
    query = ForecastResult.find_all()
    if sku:
        query = ForecastResult.find(ForecastResult.sku == sku)
        
    return await query.sort("-generated_at").skip(skip).limit(limit).to_list()

@router.get("/history", response_model=List[ForecastHistory])
async def get_forecast_history(
    skip: int = Query(0, ge=0), 
    limit: int = Query(50, ge=1, le=100),
    sku: Optional[str] = None
):
    query = ForecastHistory.find_all()
    if sku:
        query = ForecastHistory.find(ForecastHistory.sku == sku)
        
    return await query.sort("-date").skip(skip).limit(limit).to_list()

@router.get("/recommendations", response_model=List[ForecastRecommendation])
async def get_forecast_recommendations(
    skip: int = Query(0, ge=0), 
    limit: int = Query(50, ge=1, le=100),
    sku: Optional[str] = None
):
    query = ForecastRecommendation.find_all()
    if sku:
        query = ForecastRecommendation.find(ForecastRecommendation.sku == sku)
        
    return await query.sort("-created_at").skip(skip).limit(limit).to_list()

@router.get("/alerts", response_model=List[ForecastAlert])
async def get_forecast_alerts(
    skip: int = Query(0, ge=0), 
    limit: int = Query(50, ge=1, le=100),
    sku: Optional[str] = None
):
    query = ForecastAlert.find_all()
    if sku:
        query = ForecastAlert.find(ForecastAlert.sku == sku)
        
    return await query.sort("-created_at").skip(skip).limit(limit).to_list()

@router.get("/accuracy", response_model=List[ForecastAccuracy])
async def get_forecast_accuracy(
    skip: int = Query(0, ge=0), 
    limit: int = Query(50, ge=1, le=100),
    sku: Optional[str] = None
):
    query = ForecastAccuracy.find_all()
    if sku:
        query = ForecastAccuracy.find(ForecastAccuracy.sku == sku)
        
    return await query.sort("-calculated_at").skip(skip).limit(limit).to_list()

@router.post("/run")
async def trigger_forecast_run(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_forecast_monitor)
    return {"message": "Demand forecast monitor started in background"}

@router.post("/simulate")
async def simulate_demand_spike(sku: str, spike_amount: float):
    """Injects a sudden spike into the forecast history to simulate a trend change."""
    record = ForecastHistory(
        sku=sku,
        date=datetime.now(),
        sales_quantity=spike_amount,
        inventory_movement=spike_amount
    )
    await record.insert()
    return {"message": f"Simulated demand spike of {spike_amount} for {sku}"}

@router.delete("/history/{record_id}")
async def delete_history_record(record_id: str):
    # Using Beanie's get method
    from bson import ObjectId
    try:
        record = await ForecastHistory.get(ObjectId(record_id))
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        await record.delete()
        return {"message": "Record deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")
