import logging
from datetime import datetime
import json
import random
from models.cost_intelligence import (
    CostAnalysis, CostTrend, CostPrediction, BudgetMonitoring,
    CostRecommendation, CostAlert, CostHistory, CostAIAnalysis
)
from models.domain import CoordinatorMessage, Inventory, Supplier, Warehouse, Shipment
from models.procurement_intelligence import PurchasePlan
from services.cost_engine import cost_engine
from services.cost_ai import cost_ai_engine
from api.routers.websockets import manager

logger = logging.getLogger(__name__)

async def run_cost_monitor():
    """Autonomous Background Monitor - evaluates supply chain costs, budgets, and AI optimization."""
    logger.info("Running autonomous cost intelligence monitor...")
    
    try:
        results = []
        analysis_id = f"cost_{int(datetime.now().timestamp())}"
        
        # 1. Fetch live cross-domain data
        inv_data = await Inventory.find_all().to_list()
        wh_data = await Warehouse.find_all().to_list()
        proc_data = await PurchasePlan.find(PurchasePlan.status != "Executed").to_list()
        ship_data = await Shipment.find_all().to_list()
        
        # 2. Aggregate Costs
        costs = cost_engine.aggregate_costs(inv_data, wh_data, proc_data, ship_data)
        
        analysis = CostAnalysis(
            analysis_id=analysis_id,
            inventory_holding_cost=costs["inventory_holding_cost"],
            warehouse_cost=costs["warehouse_cost"],
            transportation_cost=costs["transportation_cost"],
            procurement_cost=costs["procurement_cost"],
            supplier_cost=costs["supplier_cost"],
            fuel_cost=costs["fuel_cost"],
            emergency_shipping_cost=costs["emergency_shipping_cost"],
            total_cost=costs["total_cost"]
        )
        await analysis.insert()
        
        # 3. Analyze Trend
        # Mock historical data: assume last period was slightly lower
        hist_total = costs["total_cost"] * random.uniform(0.85, 1.1)
        trend_res = cost_engine.analyze_trend(costs["total_cost"], hist_total)
        
        trend = CostTrend(
            period="Weekly",
            total_cost=costs["total_cost"],
            growth_percentage=trend_res["growth_percentage"],
            reduction_percentage=trend_res["reduction_percentage"]
        )
        await trend.insert()
        
        # 4. Check Budgets
        budgets = {
            "Inventory": 100000.0,
            "Warehouse": 150000.0,
            "Transportation": 80000.0,
            "Procurement": 300000.0
        }
        
        budget_results = cost_engine.check_budgets(costs, budgets)
        
        for br in budget_results:
            bm = BudgetMonitoring(
                department=br["department"],
                allocated_budget=br["allocated_budget"],
                actual_spend=br["actual_spend"],
                variance=br["variance"],
                status=br["status"]
            )
            await bm.insert()
            
            # Fire Alert if Over Budget
            if br["status"] == "Over Budget":
                alert = CostAlert(
                    alert_id=f"alert_{br['department']}_{analysis_id}",
                    title=f"{br['department']} Budget Exceeded",
                    message=f"Spend: ${br['actual_spend']} vs Budget: ${br['allocated_budget']}",
                    severity="Critical",
                    department=br["department"]
                )
                await alert.insert()
                
                # Coordinator Escalation
                coord_payload = {
                    "agent": "Cost Optimization Agent",
                    "finding": f"{br['department']} budget exceeded by ${abs(br['variance'])}.",
                    "severity": "High",
                    "confidence": 0.95,
                    "recommendations": ["Trigger emergency cost freeze", "Run AI optimization"],
                    "metadata": {
                        "department": br['department'],
                        "variance": br['variance']
                    },
                    "contributing_evidence": [f"Actual Spend: ${br['actual_spend']}"]
                }
                
                coord_msg = CoordinatorMessage(
                    message_id=f"msg_budget_{analysis_id}",
                    direction="outbound",
                    payload=coord_payload,
                    status="Pending"
                )
                await coord_msg.insert()
                
                results.append({
                    "department": br['department'],
                    "variance": br['variance'],
                    "finding": coord_payload["finding"],
                    "recommendations": coord_payload["recommendations"]
                })
                
        # 5. Predictions
        pred = CostPrediction(
            predicted_future_cost=costs["total_cost"] * (1 + (trend.growth_percentage / 100)),
            predicted_inventory_cost=costs["inventory_holding_cost"] * 1.05,
            predicted_warehouse_cost=costs["warehouse_cost"] * 1.02,
            predicted_transportation_cost=costs["transportation_cost"] * 1.1,
            predicted_procurement_cost=costs["procurement_cost"] * 1.0,
            confidence_score=0.85
        )
        await pred.insert()
        
        # 6. Identify Waste & AI Optimization
        waste_flags = cost_engine.identify_waste(costs, trend_res)
        ai_data = None
        
        if waste_flags or trend.growth_percentage > 5.0:
            logger.info(f"Cost waste or growth detected. Generating AI optimization plan...")
            
            ai_result = await cost_ai_engine.analyze_costs(
                analysis_id=analysis_id,
                cost_data=costs,
                trend_data=trend_res,
                waste_flags=waste_flags
            )
            
            ai_analysis = CostAIAnalysis(
                analysis_id=analysis_id,
                root_cause=ai_result.get("root_cause", ""),
                cost_summary=ai_result.get("cost_summary", ""),
                cost_drivers=ai_result.get("cost_drivers", []),
                business_impact=ai_result.get("business_impact", ""),
                optimization_strategy=ai_result.get("optimization_strategy", ""),
                long_term_savings_plan=ai_result.get("long_term_savings_plan", ""),
                confidence_score=ai_result.get("confidence_score", 0.5)
            )
            await ai_analysis.insert()
            ai_data = ai_analysis.dict()
            
            # Auto-generate a Recommendation document based on AI
            rec = CostRecommendation(
                recommendation_id=f"rec_{analysis_id}",
                action_type="AI Optimization",
                reason=ai_analysis.optimization_strategy,
                estimated_savings=costs["total_cost"] * 0.1, # Estimate 10% savings
                priority="High",
                business_impact=ai_analysis.business_impact,
                confidence=ai_analysis.confidence_score
            )
            await rec.insert()
                
        # Broadcast
        await manager.broadcast(json.dumps({
            "type": "COST_UPDATE",
            "data": {
                "analysis_id": analysis_id,
                "total_cost": costs["total_cost"],
                "growth": trend.growth_percentage,
                "ai_analysis": ai_data
            }
        }))
            
        logger.info("Cost monitor completed successfully.")
        return results
        
    except Exception as e:
        logger.error(f"Cost monitor failed: {e}")
        return []
