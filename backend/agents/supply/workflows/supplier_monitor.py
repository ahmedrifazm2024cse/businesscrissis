import logging
from datetime import datetime, timezone
import json
from models.supplier_intelligence import (
    SupplierProfile, SupplierPerformance, SupplierRisk,
    SupplierPrediction, SupplierRecommendation, SupplierAlert,
    SupplierHistory, SupplierAIAnalysis
)
from models.domain import CoordinatorMessage
from services.supplier_engine import supplier_engine
from services.supplier_ai import supplier_ai_engine
from api.routers.websockets import manager

logger = logging.getLogger(__name__)

async def run_supplier_monitor():
    """Autonomous Background Monitor - evaluates suppliers, predicts risks, and generates AI advice."""
    logger.info("Running autonomous supplier intelligence monitor...")
    
    try:
        results = []
        # Get all suppliers
        suppliers = await SupplierProfile.find_all().to_list()
        
        for supplier in suppliers:
            sid = supplier.supplier_id
            
            # 1. Fetch current metrics (in a real system, these would be aggregated from ERP/logs)
            # For this architecture, we will fetch the latest recorded metrics or generate baseline if missing
            perf = await SupplierPerformance.find(SupplierPerformance.supplier_id == sid).sort("-recorded_at").first_or_none()
            if not perf:
                import random
                perf = SupplierPerformance(
                    supplier_id=sid,
                    on_time_delivery_pct=random.uniform(70, 99),
                    avg_delivery_delay_days=random.uniform(0, 10),
                    order_fulfillment_rate=random.uniform(80, 100),
                    quality_acceptance_rate=random.uniform(85, 100),
                    defect_rate=random.uniform(0, 5),
                    cancellation_rate=random.uniform(0, 5),
                    return_rate=random.uniform(0, 3),
                    sla_compliance=random.uniform(80, 100),
                    overall_performance_score=0.0
                )
            
            perf.overall_performance_score = supplier_engine.calculate_performance_score(perf.dict())
            await perf.save()
            
            # 2. Risk Engine
            risk = await SupplierRisk.find(SupplierRisk.supplier_id == sid).sort("-calculated_at").first_or_none()
            if not risk:
                import random
                risk = SupplierRisk(
                    supplier_id=sid,
                    financial_risk=random.uniform(10, 80),
                    delivery_risk=random.uniform(10, 50),
                    country_risk=random.uniform(5, 60),
                    political_risk=random.uniform(5, 70),
                    natural_disaster_risk=random.uniform(5, 40),
                    weather_impact=random.uniform(0, 20),
                    currency_risk=random.uniform(5, 30),
                    single_source_dependency=80 if supplier.is_primary else 20,
                    capacity_risk=random.uniform(10, 60),
                    quality_risk=random.uniform(5, 30),
                    compliance_risk=random.uniform(0, 20),
                    contract_expiration_risk=random.uniform(0, 50),
                    overall_risk_score=0.0,
                    risk_category="Low"
                )
            
            risk_result = supplier_engine.calculate_risk_score(risk.dict())
            risk.overall_risk_score = risk_result["overall_risk_score"]
            risk.risk_category = risk_result["risk_category"]
            await risk.save()
            
            # 3. History Tracking
            history = SupplierHistory(
                supplier_id=sid,
                performance_score=perf.overall_performance_score,
                risk_score=risk.overall_risk_score,
                event_summary=f"Risk: {risk.risk_category}"
            )
            await history.insert()
            
            # 4. Failure Prediction
            pred_data = supplier_engine.predict_failure(
                performance=perf.overall_performance_score,
                risk_score=risk.overall_risk_score,
                delay_days=perf.avg_delivery_delay_days
            )
            
            prediction = SupplierPrediction(
                supplier_id=sid,
                failure_probability=pred_data["failure_probability"],
                expected_disruption_date=pred_data["expected_disruption_date"],
                expected_delivery_delays_days=pred_data["expected_delivery_delays_days"],
                potential_inventory_shortages=supplier.products_supplied,
                estimated_business_impact=pred_data["estimated_business_impact"],
                confidence_score=pred_data["confidence_score"]
            )
            await prediction.insert()
            
            # 5. AI Analysis & Alternative Ranking (only if Risk is High/Critical or Failure Prob > 0.5)
            ai_data = None
            if risk.risk_category in ["High", "Critical"] or prediction.failure_probability > 0.5:
                logger.info(f"High risk detected for supplier {sid}. Generating AI analysis...")
                
                # Rank alternatives (Find other suppliers that supply the same categories)
                all_sups = await SupplierProfile.find_all().to_list()
                alt_list = []
                for s in all_sups:
                    if s.supplier_id != sid and any(cat in supplier.categories for cat in s.categories):
                        alt_list.append({
                            "id": s.supplier_id,
                            "cost_multiplier": 1.1, # Mock data
                            "distance_km": 500, # Mock data
                            "risk_score": 30, # Mock data
                            "capacity_pct": s.capacity_per_month / max(1, supplier.capacity_per_month) * 100
                        })
                        
                ranked_alts = supplier_engine.rank_alternatives(supplier.dict(), alt_list)
                
                if ranked_alts:
                    rec = SupplierRecommendation(
                        target_supplier_id=sid,
                        alternative_supplier_ids=[a["supplier_id"] for a in ranked_alts[:5]],
                        ranked_alternatives=ranked_alts[:5]
                    )
                    await rec.insert()
                
                # Run Gemini
                ai_result = await supplier_ai_engine.analyze_supplier_risk(
                    supplier_id=sid,
                    name=supplier.name,
                    performance_metrics=perf.dict(),
                    risk_metrics=risk.dict(),
                    failure_prediction=prediction.dict(),
                    alternatives=ranked_alts
                )
                
                ai_analysis = SupplierAIAnalysis(
                    supplier_id=sid,
                    health_score=ai_result.get("health_score", 50.0),
                    reliability_score=ai_result.get("reliability_score", 50.0),
                    stability_score=ai_result.get("stability_score", 50.0),
                    business_continuity_score=ai_result.get("business_continuity_score", 50.0),
                    root_cause=ai_result.get("root_cause", ""),
                    business_impact=ai_result.get("business_impact", ""),
                    recommended_actions=ai_result.get("recommended_actions", []),
                    procurement_advice=ai_result.get("procurement_advice", ""),
                    risk_mitigation_strategy=ai_result.get("risk_mitigation_strategy", ""),
                    confidence_score=ai_result.get("confidence_score", 0.5)
                )
                await ai_analysis.insert()
                ai_data = ai_analysis.dict()
                
                # Create Alert
                alert = SupplierAlert(
                    supplier_id=sid,
                    title=f"Supplier Risk Escalation: {risk.risk_category}",
                    message=f"Supplier {supplier.name} has reached {risk.risk_category} risk level. Failure prob: {prediction.failure_probability*100:.1f}%.",
                    severity=risk.risk_category,
                    event_type="Risk Escalation"
                )
                await alert.insert()
                
                # Send to Coordinator
                coord_payload = {
                    "agent": "Supplier Intelligence Agent",
                    "finding": f"Supplier {supplier.name} poses a {risk.risk_category} risk.",
                    "severity": risk.risk_category,
                    "confidence": prediction.confidence_score,
                    "recommendations": ai_result.get("recommended_actions", []),
                    "metadata": {
                        "supplier_id": sid,
                        "risk_score": risk.overall_risk_score,
                        "failure_probability": prediction.failure_probability
                    },
                    "contributing_evidence": [ai_result.get("root_cause", "")]
                }
                
                coord_msg = CoordinatorMessage(
                    message_id=f"msg_sup_{sid}_{int(datetime.now().timestamp())}",
                    direction="outbound",
                    payload=coord_payload,
                    status="Pending"
                )
                await coord_msg.insert()
                
                results.append({
                    "supplier_id": sid,
                    "risk_category": risk.risk_category,
                    "finding": coord_payload["finding"],
                    "recommendations": ai_result.get("recommended_actions", [])
                })
                
            # Broadcast update
            await manager.broadcast(json.dumps({
                "type": "SUPPLIER_UPDATE",
                "data": {
                    "supplier_id": sid,
                    "performance_score": perf.overall_performance_score,
                    "risk_score": risk.overall_risk_score,
                    "risk_category": risk.risk_category,
                    "ai_analysis": ai_data
                }
            }))
            
        logger.info("Supplier monitor completed successfully.")
        return results
        
    except Exception as e:
        logger.error(f"Supplier monitor failed: {e}")
        return []
