import logging
from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, START, END
import uuid
from datetime import datetime
import asyncio

from services.business_impact import business_impact_analyzer
from services.decision_engine import decision_engine
from services.memory_engine import memory_engine
from models.final_intelligence import BusinessImpactAssessment, RecommendationHistory
from api.routers.websockets import manager
import json

# Import the 9 specific sub-agent monitors
from workflows.inventory_monitor import run_inventory_monitor
from workflows.forecast_monitor import run_forecast_monitor
from workflows.supplier_monitor import run_supplier_monitor
from workflows.shipment_monitor import run_shipment_monitor
from workflows.warehouse_monitor import run_warehouse_monitor
from workflows.procurement_monitor import run_procurement_monitor
from workflows.cost_monitor import run_cost_monitor
from workflows.route_monitor import run_route_monitor
from workflows.shortage_monitor import run_shortage_monitor

logger = logging.getLogger(__name__)

class SupplyChainGlobalState(TypedDict):
    trigger_event: str
    
    # Context
    context: Dict[str, Any]
    
    # Telemetry
    inventory: List[Dict[str, Any]]
    forecasts: List[Dict[str, Any]]
    suppliers: List[Dict[str, Any]]
    shipments: List[Dict[str, Any]]
    warehouses: List[Dict[str, Any]]
    procurements: List[Dict[str, Any]]
    costs: List[Dict[str, Any]]
    routes: List[Dict[str, Any]]
    shortages: List[Dict[str, Any]]
    
    # Analysis
    raw_impact_scores: Dict[str, Any]
    decision_payload: Dict[str, Any]
    gemini_reasoning: Dict[str, Any]
    
    # Outputs
    coordinator_payload: Dict[str, Any]

async def load_context_node(state: SupplyChainGlobalState):
    logger.info("Orchestrator: Loading Long-Term Context...")
    context = await memory_engine.retrieve_recent_context()
    return {"context": context}

async def execute_parallel_modules_node(state: SupplyChainGlobalState):
    logger.info("Orchestrator: Executing 9 Intelligence Modules in Parallel...")
    
    # We use asyncio.gather with return_exceptions=True so one failure doesn't crash the orchestrator
    results = await asyncio.gather(
        run_inventory_monitor(),
        run_forecast_monitor(),
        run_supplier_monitor(),
        run_shipment_monitor(),
        run_warehouse_monitor(),
        run_procurement_monitor(),
        run_cost_monitor(),
        run_route_monitor(),
        run_shortage_monitor(),
        return_exceptions=True
    )
    
    def safe_get(idx):
        res = results[idx]
        if isinstance(res, Exception):
            logger.error(f"Module {idx} failed during parallel execution: {res}")
            return []
        return res or []

    return {
        "inventory": safe_get(0),
        "forecasts": safe_get(1),
        "suppliers": safe_get(2),
        "shipments": safe_get(3),
        "warehouses": safe_get(4),
        "procurements": safe_get(5),
        "costs": safe_get(6),
        "routes": safe_get(7),
        "shortages": safe_get(8)
    }

async def analyze_business_impact_node(state: SupplyChainGlobalState):
    logger.info("Orchestrator: Calculating Business Impact Scores...")
    telemetry = {
        "inventory": state.get("inventory", []),
        "forecasts": state.get("forecasts", []),
        "suppliers": state.get("suppliers", []),
        "shipments": state.get("shipments", []),
        "warehouses": state.get("warehouses", []),
        "procurements": state.get("procurements", []),
        "costs": state.get("costs", []),
        "routes": state.get("routes", []),
        "shortages": state.get("shortages", [])
    }
    
    scores = business_impact_analyzer.calculate_scores(telemetry)
    return {"raw_impact_scores": scores}

async def decision_engine_node(state: SupplyChainGlobalState):
    logger.info("Orchestrator: Decision Engine running deduplication and ranking...")
    telemetry = {
        "inventory": state.get("inventory", []),
        "forecasts": state.get("forecasts", []),
        "suppliers": state.get("suppliers", []),
        "shipments": state.get("shipments", []),
        "warehouses": state.get("warehouses", []),
        "procurements": state.get("procurements", []),
        "costs": state.get("costs", []),
        "routes": state.get("routes", []),
        "shortages": state.get("shortages", [])
    }
    decision_payload = decision_engine.process_telemetry(telemetry)
    return {"decision_payload": decision_payload}

async def gemini_reasoning_node(state: SupplyChainGlobalState):
    logger.info("Orchestrator: Executing Gemini AI Reasoning...")
    telemetry_summary = {
        "shortages_count": len(state.get("shortages", [])),
        "suppliers_count": len(state.get("suppliers", [])),
        "shipments_count": len(state.get("shipments", []))
    }
    scores = state.get("raw_impact_scores", {})
    context = state.get("context", {})
    decision = state.get("decision_payload", {})
    
    # Retrieve similar past crises based on severity
    past_crises = await memory_engine.retrieve_similar_crises(scores.get("crisis_severity", "Low"), limit=2)
    
    combined_context = {
        "telemetry_counts": telemetry_summary,
        "recent_context": context,
        "past_crises_lessons": past_crises,
        "decision_engine_actions": decision
    }
    
    ai_result = await business_impact_analyzer.analyze_with_ai(combined_context, scores)
    
    # Save to DB
    assessment = BusinessImpactAssessment(
        assessment_id=str(uuid.uuid4()),
        revenue_loss=scores.get("revenue_loss", 0),
        profit_loss=scores.get("profit_loss", 0),
        inventory_loss=scores.get("inventory_loss", 0),
        recovery_cost=scores.get("recovery_cost", 0),
        recovery_time_days=scores.get("recovery_time_days", 0),
        business_impact_score=scores.get("business_impact_score", 0),
        business_risk_score=scores.get("business_risk_score", 0),
        business_health_score=scores.get("business_health_score", 0),
        crisis_severity=scores.get("crisis_severity", "Low"),
        **ai_result
    )
    await assessment.insert()
    
    return {"gemini_reasoning": ai_result}

async def update_memory_node(state: SupplyChainGlobalState):
    logger.info("Orchestrator: Updating Long-Term Memory...")
    scores = state.get("raw_impact_scores", {})
    reasoning = state.get("gemini_reasoning", {})
    decision_payload = state.get("decision_payload", {})
    
    # Log Business History Snapshot
    await memory_engine.log_business_history(
        health_score=scores.get("business_health_score", 100),
        risk_score=scores.get("business_risk_score", 0),
        impact_score=scores.get("business_impact_score", 0),
        crises_count=1 if scores.get("crisis_severity") in ["High", "Critical"] else 0
    )
    
    # Generate unified decision string from critical actions
    unified_decision = "; ".join(decision_payload.get("critical_actions", [reasoning.get("business_recommendation", "None")]))
    
    # Log Decision
    await memory_engine.log_decision(
        trigger=state.get("trigger_event", "Scheduled Run"),
        context=reasoning.get("executive_summary", ""),
        decision=unified_decision,
        reasoning=reasoning.get("business_explanation", ""),
        confidence=float(reasoning.get("confidence", 0.0)),
        status="Executed"
    )
    
    # Log Crisis if severe
    if scores.get("crisis_severity") in ["High", "Critical"]:
        crisis = await memory_engine.log_crisis(
            severity=scores.get("crisis_severity"),
            root_cause=reasoning.get("root_cause", ""),
            impact_estimate=scores.get("revenue_loss", 0),
            status="Active"
        )
        # Kick off an async learning summary based on assumed resolution
        await memory_engine.generate_learning_summary(crisis.crisis_id, "Crisis identified and mitigation plan generated.")

    # Save to RecommendationHistory
    all_recs = decision_payload.get("critical_actions", [])
    if reasoning.get("business_recommendation"):
        all_recs.append(reasoning.get("business_recommendation"))
        
    for action in all_recs:
        rec_doc = RecommendationHistory(
            recommendation_id=str(uuid.uuid4()),
            agent_source="Autonomous Decision Engine",
            recommendation=action,
            priority=scores.get("crisis_severity", "High"),
            outcome="Pending"
        )
        await rec_doc.insert()

    return {}

async def notify_coordinator_node(state: SupplyChainGlobalState):
    logger.info("Orchestrator: Generating Coordinator Payload...")
    reasoning = state.get("gemini_reasoning", {})
    scores = state.get("raw_impact_scores", {})
    decision_payload = state.get("decision_payload", {})
    
    # Build exact matching JSON schema
    payload = {
        "agent": "Supply Chain Agent",
        "status": "completed",
        "finding": reasoning.get("executive_summary", ""),
        "severity": scores.get("crisis_severity", "Low"),
        "confidence": float(reasoning.get("confidence", 0.97)),
        "business_impact": {
            "revenue_loss": scores.get("revenue_loss", 0),
            "business_impact_score": scores.get("business_impact_score", 0),
            "customer_impact": scores.get("customer_impact", 0),
            "production_delay_days": scores.get("production_delay_days", 0)
        },
        "recommendations": decision_payload.get("critical_actions", []) + [reasoning.get("business_recommendation", "")],
        "contributing_evidence": decision_payload.get("top_issues", []),
        "memory_reference": state.get("context", {}).get("active_crises_details", []),
        "processing_time": "async",
        "timestamp": datetime.now().isoformat()
    }
    
    await memory_engine.log_coordinator_interaction("outbound", payload, "Pending")
    
    # Broadcast to websocket
    await manager.broadcast(json.dumps({
        "type": "ORCHESTRATION_COMPLETE",
        "data": payload
    }))
    
    return {"coordinator_payload": payload}

def build_orchestrator_graph():
    builder = StateGraph(SupplyChainGlobalState)
    
    builder.add_node("load_context", load_context_node)
    builder.add_node("execute_parallel_modules", execute_parallel_modules_node)
    builder.add_node("analyze_business_impact", analyze_business_impact_node)
    builder.add_node("decision_engine", decision_engine_node)
    builder.add_node("gemini_reasoning", gemini_reasoning_node)
    builder.add_node("update_memory", update_memory_node)
    builder.add_node("notify_coordinator", notify_coordinator_node)
    
    builder.add_edge(START, "load_context")
    builder.add_edge("load_context", "execute_parallel_modules")
    builder.add_edge("execute_parallel_modules", "analyze_business_impact")
    builder.add_edge("analyze_business_impact", "decision_engine")
    builder.add_edge("decision_engine", "gemini_reasoning")
    builder.add_edge("gemini_reasoning", "update_memory")
    builder.add_edge("update_memory", "notify_coordinator")
    builder.add_edge("notify_coordinator", END)
    
    return builder.compile()

autonomous_orchestrator = build_orchestrator_graph()

async def run_supply_chain_orchestrator():
    logger.info("=== STARTING END-TO-END SUPPLY CHAIN ORCHESTRATION ===")
    try:
        await autonomous_orchestrator.ainvoke({"trigger_event": "Scheduled Global Orchestration"})
    except Exception as e:
        logger.error(f"Global Orchestration Failed: {e}")
