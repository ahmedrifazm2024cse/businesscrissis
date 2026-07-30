import logging
from datetime import datetime
import json
import random
from models.procurement_intelligence import (
    PurchasePlan, ProcurementRisk, ProcurementPrediction,
    ProcurementRecommendation, ProcurementAlert, ProcurementHistory,
    ProcurementAIAnalysis
)
from models.domain import CoordinatorMessage, Inventory, Supplier
from services.procurement_engine import procurement_engine
from services.procurement_ai import procurement_ai_engine
from api.routers.websockets import manager

logger = logging.getLogger(__name__)

async def run_procurement_monitor():
    """Autonomous Background Monitor - evaluates procurement needs, generates EOQ plans, and AI strategies."""
    logger.info("Running autonomous procurement intelligence monitor...")
    
    try:
        results = []
        # Get all low inventory items
        low_inventory = await Inventory.find(Inventory.current_stock < Inventory.reorder_point).to_list()
        
        # Get all suppliers
        suppliers_raw = await Supplier.find_all().to_list()
        suppliers = []
        for s in suppliers_raw:
            suppliers.append({
                "supplier_id": s.supplier_id,
                "price_per_unit": random.uniform(10, 100),
                "lead_time_days": s.lead_time_days,
                "risk_score": s.risk_score,
                "capacity": random.uniform(1000, 10000)
            })
            
        for item in low_inventory:
            plan_id = f"plan_{item.sku}_{int(datetime.now().timestamp())}"
            
            # 1. Prediction (Price Trends)
            pred = ProcurementPrediction(
                sku=item.sku,
                predicted_price_change=random.uniform(-5.0, 15.0),
                market_trend="Bullish" if random.random() > 0.5 else "Bearish"
            )
            await pred.insert()
            
            # 2. EOQ Calculation
            annual_demand = 12000 # mock
            order_cost = 50.0 # mock per order
            holding_cost = 2.0 # mock per unit/year
            
            eoq = procurement_engine.calculate_eoq(annual_demand, order_cost, holding_cost)
            
            # 3. Timing Strategy
            timing = procurement_engine.determine_timing_strategy(item.current_stock, item.reorder_point, pred.predicted_price_change)
            
            # 4. Supplier Selection
            ranked_suppliers = procurement_engine.rank_suppliers(suppliers, eoq)
            best_supplier = ranked_suppliers[0] if ranked_suppliers else {"supplier_id": "UNKNOWN", "price": 0}
            
            # 5. Create Plan
            plan = PurchasePlan(
                plan_id=plan_id,
                sku=item.sku,
                supplier_id=best_supplier["supplier_id"],
                warehouse_id=item.warehouse_id,
                order_quantity=eoq,
                eoq=eoq,
                safety_stock_requirement=item.safety_stock,
                buffer_stock=item.safety_stock * 1.5,
                min_stock=item.reorder_point,
                max_stock=item.reorder_point * 3,
                timing_strategy=timing,
                priority_level="Critical" if timing == "Emergency Purchase" else "High",
                estimated_cost=eoq * best_supplier["price"],
                status="Draft"
            )
            await plan.insert()
            
            # 6. Risk Calculation
            risk_factors = {
                "supplier_risk": best_supplier.get("risk_score", 50),
                "transportation_risk": random.uniform(10, 80),
                "political_risk": random.uniform(5, 40)
            }
            overall_risk = procurement_engine.calculate_risk(risk_factors)
            
            risk = ProcurementRisk(
                plan_id=plan_id,
                supplier_risk=risk_factors["supplier_risk"],
                inventory_risk=100 if timing == "Emergency Purchase" else 40,
                demand_risk=50,
                transportation_risk=risk_factors["transportation_risk"],
                currency_risk=20,
                political_risk=risk_factors["political_risk"],
                weather_risk=10,
                contract_risk=10,
                overall_risk_score=overall_risk,
                confidence_score=0.9
            )
            await risk.insert()
            
            # 7. AI Analysis (only for Critical or High Risk)
            ai_data = None
            if plan.priority_level == "Critical" or risk.overall_risk_score > 70:
                logger.info(f"Critical procurement needed for {item.sku}. Generating AI strategy...")
                
                ai_result = await procurement_ai_engine.analyze_procurement_plan(
                    plan_id=plan_id,
                    sku=item.sku,
                    plan_data=plan.dict(),
                    risk_data=risk.dict(),
                    prediction_data=pred.dict()
                )
                
                ai_analysis = ProcurementAIAnalysis(
                    plan_id=plan_id,
                    purchase_strategy=ai_result.get("purchase_strategy", ""),
                    negotiation_strategy=ai_result.get("negotiation_strategy", ""),
                    supplier_recommendation=ai_result.get("supplier_recommendation", ""),
                    expected_savings_explanation=ai_result.get("expected_savings_explanation", ""),
                    business_impact=ai_result.get("business_impact", ""),
                    risk_mitigation=ai_result.get("risk_mitigation", ""),
                    confidence_score=ai_result.get("confidence_score", 0.5)
                )
                await ai_analysis.insert()
                ai_data = ai_analysis.dict()
                
                # Alert
                alert = ProcurementAlert(
                    alert_id=f"alert_{plan_id}",
                    title="Emergency Procurement Required",
                    message=f"Critical shortage of {item.sku}. Initiating Emergency Purchase of {eoq} units.",
                    severity="Critical",
                    event_type="Shortage"
                )
                await alert.insert()
                
                # Coordinator Escalation
                coord_payload = {
                    "agent": "Procurement Intelligence Agent",
                    "finding": f"Critical shortage of {item.sku}. Action: {plan.timing_strategy} from {plan.supplier_id}.",
                    "severity": alert.severity,
                    "confidence": risk.confidence_score,
                    "recommendations": [ai_result.get("purchase_strategy", "")],
                    "metadata": {
                        "plan_id": plan_id,
                        "sku": item.sku,
                        "cost": plan.estimated_cost
                    },
                    "contributing_evidence": [f"Risk score: {risk.overall_risk_score}"]
                }
                
                coord_msg = CoordinatorMessage(
                    message_id=f"msg_proc_{plan_id}",
                    direction="outbound",
                    payload=coord_payload,
                    status="Pending"
                )
                await coord_msg.insert()
                
                results.append({
                    "plan_id": plan_id,
                    "sku": item.sku,
                    "priority": plan.priority_level,
                    "finding": coord_payload["finding"],
                    "recommendation": ai_result.get("purchase_strategy", "")
                })
                
            # Broadcast
            await manager.broadcast(json.dumps({
                "type": "PROCUREMENT_UPDATE",
                "data": {
                    "plan_id": plan_id,
                    "sku": item.sku,
                    "priority": plan.priority_level,
                    "cost": plan.estimated_cost,
                    "ai_analysis": ai_data
                }
            }))
            
        logger.info("Procurement monitor completed successfully.")
        return results
        
    except Exception as e:
        logger.error(f"Procurement monitor failed: {e}")
        return []
