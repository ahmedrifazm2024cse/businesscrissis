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

@pytest.mark.asyncio
async def test_load_context_node():
    with patch('workflows.autonomous_orchestrator.memory_engine.retrieve_recent_context', new_callable=AsyncMock) as mock_retrieve:
        mock_retrieve.return_value = {"active_crises_count": 0}
        
        state: SupplyChainGlobalState = {"trigger_event": "Test"}
        result = await load_context_node(state)
        
        assert "context" in result
        assert result["context"]["active_crises_count"] == 0

@pytest.mark.asyncio
async def test_execute_parallel_modules_node():
    # Mock all the monitors
    with patch('workflows.autonomous_orchestrator.run_inventory_monitor', new_callable=AsyncMock) as mock_inv, \
         patch('workflows.autonomous_orchestrator.run_forecast_monitor', new_callable=AsyncMock) as mock_for, \
         patch('workflows.autonomous_orchestrator.run_supplier_monitor', new_callable=AsyncMock) as mock_sup, \
         patch('workflows.autonomous_orchestrator.run_shipment_monitor', new_callable=AsyncMock) as mock_shp, \
         patch('workflows.autonomous_orchestrator.run_warehouse_monitor', new_callable=AsyncMock) as mock_wh, \
         patch('workflows.autonomous_orchestrator.run_procurement_monitor', new_callable=AsyncMock) as mock_proc, \
         patch('workflows.autonomous_orchestrator.run_cost_monitor', new_callable=AsyncMock) as mock_cost, \
         patch('workflows.autonomous_orchestrator.run_route_monitor', new_callable=AsyncMock) as mock_route, \
         patch('workflows.autonomous_orchestrator.run_shortage_monitor', new_callable=AsyncMock) as mock_short:
        
        mock_inv.return_value = [{"finding": "Low inventory on SKU 123"}]
        mock_sup.return_value = [{"finding": "Supplier delayed"}]
        mock_cost.side_effect = Exception("Cost monitor failed")
        
        state: SupplyChainGlobalState = {"trigger_event": "Test"}
        result = await execute_parallel_modules_node(state)
        
        # Verify it handled success
        assert len(result["inventory"]) == 1
        assert result["inventory"][0]["finding"] == "Low inventory on SKU 123"
        
        assert len(result["suppliers"]) == 1
        
        # Verify it gracefully handled failure via return_exceptions=True
        assert result["costs"] == []

@pytest.mark.asyncio
async def test_analyze_business_impact_node():
    with patch('workflows.autonomous_orchestrator.business_impact_analyzer.calculate_scores') as mock_calc:
        mock_calc.return_value = {"crisis_severity": "Critical", "business_impact_score": 85}
        
        state: SupplyChainGlobalState = {
            "trigger_event": "Test",
            "inventory": [],
            "shortages": [{"sku": "TEST", "revenue_impact_estimate": 10000}]
        }
        
        result = await analyze_business_impact_node(state)
        assert "raw_impact_scores" in result
        assert result["raw_impact_scores"]["crisis_severity"] == "Critical"

@pytest.mark.asyncio
async def test_decision_engine_node():
    with patch('workflows.autonomous_orchestrator.decision_engine.process_telemetry') as mock_proc:
        mock_proc.return_value = {"critical_actions": ["Reroute shipment"]}
        
        state: SupplyChainGlobalState = {"trigger_event": "Test"}
        result = await decision_engine_node(state)
        
        assert "decision_payload" in result
        assert "Reroute shipment" in result["decision_payload"]["critical_actions"]

@pytest.mark.asyncio
async def test_notify_coordinator_node():
    with patch('workflows.autonomous_orchestrator.memory_engine.log_coordinator_interaction', new_callable=AsyncMock) as mock_log, \
         patch('workflows.autonomous_orchestrator.manager.broadcast', new_callable=AsyncMock) as mock_broad:
        
        state: SupplyChainGlobalState = {
            "trigger_event": "Test",
            "gemini_reasoning": {"executive_summary": "All good", "confidence": 0.99},
            "raw_impact_scores": {"crisis_severity": "Low", "revenue_loss": 0},
            "decision_payload": {"critical_actions": []},
            "context": {}
        }
        
        result = await notify_coordinator_node(state)
        
        assert "coordinator_payload" in result
        payload = result["coordinator_payload"]
        assert payload["agent"] == "Supply Chain Agent"
        assert payload["severity"] == "Low"
        assert payload["confidence"] == 0.99
        
        # Verify broadcast
        mock_broad.assert_called_once()
        mock_log.assert_called_once()
