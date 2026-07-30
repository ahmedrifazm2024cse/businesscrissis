from fastapi import APIRouter, BackgroundTasks
from typing import List
from models.final_intelligence import (
    BusinessImpactAssessment, DecisionHistory, BusinessHistory, CrisisHistory,
    RecommendationHistory, LearningHistory, CoordinatorHistory
)
from workflows.autonomous_orchestrator import run_supply_chain_orchestrator

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

@router.get("/business-impact", response_model=List[BusinessImpactAssessment])
async def get_business_impact(skip: int = 0, limit: int = 50):
    return await BusinessImpactAssessment.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.get("/decisions", response_model=List[DecisionHistory])
async def get_decisions(skip: int = 0, limit: int = 50):
    return await DecisionHistory.find_all().sort("-timestamp").skip(skip).limit(limit).to_list()

@router.get("/business-history", response_model=List[BusinessHistory])
async def get_business_history(skip: int = 0, limit: int = 50):
    return await BusinessHistory.find_all().sort("-timestamp").skip(skip).limit(limit).to_list()

@router.get("/crises", response_model=List[CrisisHistory])
async def get_crises(skip: int = 0, limit: int = 50):
    return await CrisisHistory.find_all().sort("-identified_at").skip(skip).limit(limit).to_list()

@router.get("/learning", response_model=List[LearningHistory])
async def get_learning(skip: int = 0, limit: int = 50):
    return await LearningHistory.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.get("/coordinator-logs", response_model=List[CoordinatorHistory])
async def get_coordinator_logs(skip: int = 0, limit: int = 50):
    return await CoordinatorHistory.find_all().sort("-timestamp").skip(skip).limit(limit).to_list()

@router.post("/trigger")
async def trigger_orchestrator(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_supply_chain_orchestrator)
    return {"message": "End-to-end supply chain orchestration triggered."}
