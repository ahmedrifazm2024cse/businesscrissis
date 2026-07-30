import logging
from datetime import datetime
import json
import random
from models.warehouse_intelligence import (
    WarehouseCapacity, WarehousePerformance, WarehousePrediction,
    WarehouseRisk, WarehouseRecommendation, WarehouseAlert,
    WarehouseHistory, WarehouseAIAnalysis
)
from models.domain import CoordinatorMessage, Warehouse
from services.warehouse_engine import warehouse_engine
from services.warehouse_ai import warehouse_ai_engine
from api.routers.websockets import manager

logger = logging.getLogger(__name__)

async def run_warehouse_monitor():
    """Autonomous Background Monitor - evaluates warehouses, predicts capacity, and generates AI advice."""
    logger.info("Running autonomous warehouse intelligence monitor...")
    
    try:
        results = []
        # Get all warehouses (we assume some exist in domain)
        warehouses = await Warehouse.find_all().to_list()
        
        for wh in warehouses:
            wid = wh.warehouse_id
            
            # 1. Update Capacity
            cap = await WarehouseCapacity.find(WarehouseCapacity.warehouse_id == wid).sort("-recorded_at").first_or_none()
            if not cap:
                total_cap = random.uniform(5000, 50000)
                used = total_cap * random.uniform(0.6, 0.95)
                cap = WarehouseCapacity(
                    warehouse_id=wid,
                    total_capacity=total_cap,
                    used_capacity=used,
                    available_capacity=total_cap - used,
                    utilization_percentage=(used / total_cap) * 100,
                    rack_utilization=0, shelf_utilization=0,
                    cold_storage_used=0, cold_storage_capacity=0,
                    zone_utilization={}
                )
            else:
                # Simulate movement
                cap.used_capacity += random.uniform(-500, 1000)
                cap.used_capacity = max(0, min(cap.total_capacity, cap.used_capacity))
                
            cap_result = warehouse_engine.calculate_utilization(
                total_capacity=cap.total_capacity,
                used_capacity=cap.used_capacity,
                zone_data={"A": 80, "B": 60}
            )
            cap.available_capacity = cap_result["available_capacity"]
            cap.utilization_percentage = cap_result["utilization_percentage"]
            cap.rack_utilization = cap_result["rack_utilization"]
            cap.shelf_utilization = cap_result["shelf_utilization"]
            await cap.save()
            
            # 2. Performance Tracking (Mock)
            perf = await WarehousePerformance.find(WarehousePerformance.warehouse_id == wid).sort("-recorded_at").first_or_none()
            if not perf:
                perf = WarehousePerformance(
                    warehouse_id=wid,
                    inventory_turnover_rate=random.uniform(5, 20),
                    picking_efficiency=random.uniform(80, 100),
                    receiving_efficiency=random.uniform(80, 100),
                    shipping_efficiency=random.uniform(80, 100),
                    avg_order_processing_time_hours=random.uniform(1, 10),
                    avg_loading_time_hours=random.uniform(1, 5),
                    avg_unloading_time_hours=random.uniform(1, 5)
                )
                await perf.insert()
            
            # 3. Predict Capacity
            inbound = random.uniform(100, 500)
            outbound = random.uniform(50, 450)
            pred_data = warehouse_engine.predict_capacity(
                current_utilization=cap.utilization_percentage,
                inbound_velocity_daily=inbound,
                outbound_velocity_daily=outbound,
                total_capacity=cap.total_capacity
            )
            
            prediction = WarehousePrediction(
                warehouse_id=wid,
                predicted_full_date=pred_data["predicted_full_date"],
                capacity_remaining_days=pred_data["capacity_remaining_days"],
                storage_growth_trend=pred_data["storage_growth_trend"],
                overflow_risk_score=pred_data["overflow_risk_score"],
                expansion_requirement=pred_data["expansion_requirement"],
                confidence_score=pred_data["confidence_score"]
            )
            await prediction.insert()
            
            # 4. Risk & Bottlenecks
            risk_factors = {
                "fire_risk": random.uniform(0, 10),
                "equipment_risk": random.uniform(0, 50) if perf.avg_loading_time_hours < 4 else random.uniform(50, 100)
            }
            risk_res = warehouse_engine.analyze_risk_and_bottlenecks(risk_factors, perf.dict(), cap.utilization_percentage)
            
            risk = WarehouseRisk(
                warehouse_id=wid,
                fire_risk=risk_factors.get("fire_risk", 0),
                flood_risk=0, equipment_risk=risk_factors.get("equipment_risk", 0),
                power_outage_risk=0, temperature_risk=0, inventory_damage_risk=0, security_risk=0,
                overall_risk_score=risk_res["overall_risk_score"],
                health_score=risk_res["health_score"],
                bottlenecks_detected=risk_res["bottlenecks_detected"]
            )
            await risk.insert()
            
            # 5. History
            history = WarehouseHistory(
                warehouse_id=wid,
                utilization_percentage=cap.utilization_percentage,
                health_score=risk.health_score,
                event_summary=f"Bottlenecks: {len(risk.bottlenecks_detected)}"
            )
            await history.insert()
            
            # 6. AI Analysis & Recommendations (only if Util > 90% or Health < 50)
            ai_data = None
            if cap.utilization_percentage > 90 or risk.health_score < 50:
                logger.info(f"Critical conditions at warehouse {wid}. Generating AI analysis...")
                
                # Run Gemini
                ai_result = await warehouse_ai_engine.analyze_warehouse_bottlenecks(
                    warehouse_id=wid,
                    name=wh.name,
                    capacity_data=cap.dict(),
                    prediction_data=prediction.dict(),
                    risk_data=risk.dict()
                )
                
                ai_analysis = WarehouseAIAnalysis(
                    warehouse_id=wid,
                    root_cause=ai_result.get("root_cause", ""),
                    warehouse_summary=ai_result.get("warehouse_summary", ""),
                    operational_risks=ai_result.get("operational_risks", ""),
                    business_impact=ai_result.get("business_impact", ""),
                    optimization_strategy=ai_result.get("optimization_strategy", ""),
                    recovery_plan=ai_result.get("recovery_plan", ""),
                    confidence_score=ai_result.get("confidence_score", 0.5)
                )
                await ai_analysis.insert()
                ai_data = ai_analysis.dict()
                
                rec = WarehouseRecommendation(
                    warehouse_id=wid,
                    action_type="Optimization Strategy",
                    reason=ai_analysis.root_cause,
                    priority="High",
                    expected_business_impact=ai_analysis.business_impact,
                    confidence=ai_analysis.confidence_score
                )
                await rec.insert()
                
                # Create Alert
                alert = WarehouseAlert(
                    warehouse_id=wid,
                    title="Warehouse Capacity/Health Escalation",
                    message=f"Warehouse {wh.name} utilization is at {cap.utilization_percentage:.1f}%. Health is {risk.health_score:.1f}.",
                    severity="Critical" if cap.utilization_percentage > 95 else "High",
                    event_type="Capacity Breach"
                )
                await alert.insert()
                
                # Send to Coordinator
                coord_payload = {
                    "agent": "Warehouse Intelligence Agent",
                    "finding": f"Warehouse {wh.name} critical situation: Util {cap.utilization_percentage:.1f}%.",
                    "severity": alert.severity,
                    "confidence": prediction.confidence_score,
                    "recommendations": [ai_result.get("optimization_strategy", "")],
                    "metadata": {
                        "warehouse_id": wid,
                        "utilization": cap.utilization_percentage,
                        "health": risk.health_score
                    },
                    "contributing_evidence": risk.bottlenecks_detected
                }
                
                coord_msg = CoordinatorMessage(
                    message_id=f"msg_wh_{wid}_{int(datetime.now().timestamp())}",
                    direction="outbound",
                    payload=coord_payload,
                    status="Pending"
                )
                await coord_msg.insert()
                
                results.append({
                    "warehouse_id": wid,
                    "severity": alert.severity,
                    "finding": coord_payload["finding"],
                    "recommendation": ai_result.get("optimization_strategy", "")
                })
                
            # Broadcast update
            await manager.broadcast(json.dumps({
                "type": "WAREHOUSE_UPDATE",
                "data": {
                    "warehouse_id": wid,
                    "utilization_percentage": cap.utilization_percentage,
                    "health_score": risk.health_score,
                    "bottlenecks": risk.bottlenecks_detected,
                    "ai_analysis": ai_data
                }
            }))
            
        logger.info("Warehouse monitor completed successfully.")
        return results
        
    except Exception as e:
        logger.error(f"Warehouse monitor failed: {e}")
        return []
