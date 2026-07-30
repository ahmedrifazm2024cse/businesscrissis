import pytest
from unittest.mock import patch, AsyncMock
from workflows.autonomous_orchestrator import (
    load_context_node,
    execute_parallel_modules_node,
    analyze_business_impact_node,
    decision_engine_node,
    gemini_reasoning_node,
    update_memory_node,
    notify_coordinator_node,
    SupplyChainGlobalState
)
from models.final_intelligence import BusinessImpactAssessment, RecommendationHistory, CrisisHistory, LearningHistory, CoordinatorHistory, BusinessHistory, DecisionHistory
from tests.db_test_utils import setup_test_db

@pytest.mark.asyncio
async def test_end_to_end_orchestration():
    await setup_test_db([BusinessImpactAssessment, RecommendationHistory, CrisisHistory, LearningHistory, CoordinatorHistory, BusinessHistory, DecisionHistory])
    
    # Setup initial state
    state: SupplyChainGlobalState = {
        "trigger_event": "Test Trigger",
        "inventory": [],
        "suppliers": [],
        "shipments": [],
        "forecasts": [],
        "warehouses": [],
        "procurement": [],
        "costs": [],
        "routes": [],
        "shortages": [],
        "context": {},
        "raw_impact_scores": {},
        "decision_payload": {},
        "gemini_reasoning": {},
        "coordinator_payload": {}
    }

    # 1. Context Load
    with patch('workflows.autonomous_orchestrator.memory_engine.retrieve_recent_context', new_callable=AsyncMock) as mock_ctx:
        mock_ctx.return_value = {"active_crises_count": 1}
        state.update(await load_context_node(state))
        assert state["context"]["active_crises_count"] == 1

    # 2. Parallel Execution (Mock internal monitors to return data)
    with patch('workflows.autonomous_orchestrator.run_inventory_monitor', new_callable=AsyncMock) as mock_inv, \
         patch('workflows.autonomous_orchestrator.run_supplier_monitor', new_callable=AsyncMock) as mock_sup, \
         patch('workflows.autonomous_orchestrator.run_forecast_monitor', new_callable=AsyncMock) as mock_for, \
         patch('workflows.autonomous_orchestrator.run_shipment_monitor', new_callable=AsyncMock) as mock_shp, \
         patch('workflows.autonomous_orchestrator.run_warehouse_monitor', new_callable=AsyncMock) as mock_wh, \
         patch('workflows.autonomous_orchestrator.run_procurement_monitor', new_callable=AsyncMock) as mock_proc, \
         patch('workflows.autonomous_orchestrator.run_cost_monitor', new_callable=AsyncMock) as mock_cost, \
         patch('workflows.autonomous_orchestrator.run_route_monitor', new_callable=AsyncMock) as mock_route, \
         patch('workflows.autonomous_orchestrator.run_shortage_monitor', new_callable=AsyncMock) as mock_short:
        
        mock_inv.return_value = [{"finding": "Low Stock"}]
        mock_sup.return_value = [{"finding": "Supplier Offline"}]
        
        state.update(await execute_parallel_modules_node(state))
        assert len(state["inventory"]) == 1
        assert len(state["suppliers"]) == 1

    # 3. Impact Analysis
    with patch('workflows.autonomous_orchestrator.business_impact_analyzer.calculate_scores') as mock_impact:
        mock_impact.return_value = {"crisis_severity": "High"}
        state.update(await analyze_business_impact_node(state))
        assert state["raw_impact_scores"]["crisis_severity"] == "High"

    # 4. Decision Engine
    with patch('workflows.autonomous_orchestrator.decision_engine.process_telemetry') as mock_decision:
        mock_decision.return_value = {"critical_actions": ["Reroute shipment", "Find new supplier"]}
        state.update(await decision_engine_node(state))
        assert "Find new supplier" in state["decision_payload"]["critical_actions"]

    # 5. Gemini AI
    with patch('workflows.autonomous_orchestrator.business_impact_analyzer.analyze_with_ai', new_callable=AsyncMock) as mock_ai, \
         patch('workflows.autonomous_orchestrator.memory_engine.retrieve_similar_crises', new_callable=AsyncMock) as mock_similar:
        mock_ai.return_value = {
            "executive_summary": "Issue detected.", 
            "confidence": 0.89,
            "root_cause": "Test Root Cause",
            "business_explanation": "Test Explanation",
            "risk_explanation": "Test Risk",
            "recovery_plan": "Test Recovery",
            "business_recommendation": "Test Recommendation",
            "priority": "High",
            "expected_business_outcome": "Stable"
        }
        mock_similar.return_value = []
        
        state.update(await gemini_reasoning_node(state))
        assert state["gemini_reasoning"]["confidence"] == 0.89

    # 6. Memory Update
    state.update(await update_memory_node(state))

    # 7. Notify Coordinator
    with patch('workflows.autonomous_orchestrator.manager.broadcast', new_callable=AsyncMock) as mock_broad, \
         patch('workflows.autonomous_orchestrator.memory_engine.log_coordinator_interaction', new_callable=AsyncMock) as mock_log:
        
        state.update(await notify_coordinator_node(state))
        payload = state["coordinator_payload"]
        
        assert payload["agent"] == "Supply Chain Agent"
        assert payload["severity"] == "High"
        assert payload["confidence"] == 0.89
        
        mock_broad.assert_called_once()
        mock_log.assert_called_once()

    print("✅ E2E Orchestration Test Passed!")
