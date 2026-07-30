from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from models.supplier_intelligence import (
    SupplierProfile, SupplierPerformance, SupplierRisk,
    SupplierPrediction, SupplierRecommendation, SupplierAlert,
    SupplierHistory, SupplierAIAnalysis
)
from workflows.supplier_monitor import run_supplier_monitor

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

class SupplierCreate(BaseModel):
    supplier_id: str
    name: str
    categories: List[str]
    products_supplied: List[str]
    location: str
    country: str
    is_primary: bool = False
    capacity_per_month: int
    contract_status: str
    contact_email: str

@router.get("", response_model=List[SupplierProfile])
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None
):
    query = SupplierProfile.find_all()
    if category:
        # Simplistic array contains search
        pass # Beanie requires more complex query for array contains if not strict, but we can return all and filter
    
    sups = await query.skip(skip).limit(limit).to_list()
    if category:
        sups = [s for s in sups if category in s.categories]
    return sups

@router.get("/risk", response_model=List[SupplierRisk])
async def get_supplier_risks(skip: int = 0, limit: int = 50):
    return await SupplierRisk.find_all().sort("-calculated_at").skip(skip).limit(limit).to_list()

@router.get("/health", response_model=List[SupplierAIAnalysis])
async def get_supplier_health(skip: int = 0, limit: int = 50):
    return await SupplierAIAnalysis.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.get("/recommendations", response_model=List[SupplierRecommendation])
async def get_supplier_recommendations(skip: int = 0, limit: int = 50):
    return await SupplierRecommendation.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.get("/alerts", response_model=List[SupplierAlert])
async def get_supplier_alerts(skip: int = 0, limit: int = 50):
    return await SupplierAlert.find_all().sort("-created_at").skip(skip).limit(limit).to_list()

@router.get("/predictions", response_model=List[SupplierPrediction])
async def get_supplier_predictions(skip: int = 0, limit: int = 50):
    return await SupplierPrediction.find_all().sort("-predicted_at").skip(skip).limit(limit).to_list()

@router.get("/{supplier_id}", response_model=SupplierProfile)
async def get_supplier(supplier_id: str):
    sup = await SupplierProfile.find_one(SupplierProfile.supplier_id == supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return sup

@router.post("")
async def create_supplier(supplier: SupplierCreate):
    existing = await SupplierProfile.find_one(SupplierProfile.supplier_id == supplier.supplier_id)
    if existing:
        raise HTTPException(status_code=400, detail="Supplier already exists")
    
    new_sup = SupplierProfile(**supplier.dict())
    await new_sup.insert()
    return new_sup

@router.post("/analyze")
async def trigger_supplier_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_supplier_monitor)
    return {"message": "Supplier Intelligence Monitor started in background"}

@router.post("/simulate")
async def simulate_supplier_crisis(supplier_id: str, crisis_type: str = "Political Instability"):
    """Injects a sudden risk spike into a supplier's profile to trigger AI analysis."""
    risk = await SupplierRisk.find(SupplierRisk.supplier_id == supplier_id).sort("-calculated_at").first_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="No risk profile found for supplier")
        
    if crisis_type == "Political Instability":
        risk.political_risk = 95.0
    elif crisis_type == "Natural Disaster":
        risk.natural_disaster_risk = 99.0
    elif crisis_type == "Financial Default":
        risk.financial_risk = 100.0
        
    await risk.save()
    return {"message": f"Injected {crisis_type} risk for {supplier_id}. Run analysis to see the effect."}

@router.delete("/{supplier_id}")
async def delete_supplier(supplier_id: str):
    sup = await SupplierProfile.find_one(SupplierProfile.supplier_id == supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")
    await sup.delete()
    return {"message": "Supplier deleted"}
