import logging
from datetime import datetime, timezone, timedelta
import json
import random
from models.shipment_intelligence import (
    ShipmentTracking, ShipmentETA, ShipmentPrediction,
    ShipmentRisk, ShipmentRoute, ShipmentAlert,
    ShipmentHistory, ShipmentAIAnalysis
)
from models.domain import CoordinatorMessage, Shipment
from services.shipment_engine import shipment_engine
from services.shipment_ai import shipment_ai_engine
from api.routers.websockets import manager

logger = logging.getLogger(__name__)

def generate_mock_routes():
    return [
        {"route_name": "I-95 North", "distance_km": random.uniform(200, 500), "estimated_time_hours": random.uniform(3, 8), "risk_score": random.uniform(10, 80)},
        {"route_name": "US-1 Coastal", "distance_km": random.uniform(250, 600), "estimated_time_hours": random.uniform(4, 10), "risk_score": random.uniform(5, 50)}
    ]

async def run_shipment_monitor():
    """Autonomous Background Monitor - evaluates shipments, predicts delays, and generates AI advice."""
    logger.info("Running autonomous shipment intelligence monitor...")
    
    try:
        results = []
        # Get all shipments (we assume some exist in domain)
        shipments = await Shipment.find_all().to_list()
        
        for shipment in shipments:
            sid = shipment.shipment_id
            
            # 1. Update Tracking
            tracking = await ShipmentTracking.find(ShipmentTracking.shipment_id == sid).sort("-last_updated").first_or_none()
            if not tracking:
                tracking = ShipmentTracking(
                    shipment_id=sid,
                    current_location=f"Location {random.randint(1, 100)}",
                    distance_remaining_km=random.uniform(50, 1000),
                    travel_time_remaining_hours=random.uniform(1, 24),
                    progress_percentage=random.uniform(0, 100)
                )
            else:
                # Simulate movement
                tracking.distance_remaining_km = max(0, tracking.distance_remaining_km - random.uniform(10, 50))
                tracking.progress_percentage = min(100.0, tracking.progress_percentage + random.uniform(1, 5))
                tracking.travel_time_remaining_hours = max(0.1, tracking.distance_remaining_km / max(1, tracking.speed_kmh))
            
            await tracking.save()
            
            # 2. Update Risk
            risk = await ShipmentRisk.find(ShipmentRisk.shipment_id == sid).sort("-assessed_at").first_or_none()
            if not risk:
                risk = ShipmentRisk(
                    shipment_id=sid,
                    traffic_risk=random.uniform(0, 100),
                    weather_risk=random.uniform(0, 100),
                    port_congestion_risk=random.uniform(0, 100),
                    border_delay_risk=random.uniform(0, 50),
                    political_risk=random.uniform(0, 20),
                    overall_risk_score=0.0,
                    risk_category="Low",
                    health_score=100.0
                )
            
            risk_result = shipment_engine.calculate_risk(risk.dict(), tracking.progress_percentage)
            risk.overall_risk_score = risk_result["overall_risk_score"]
            risk.risk_category = risk_result["risk_category"]
            risk.health_score = risk_result["health_score"]
            await risk.save()
            
            # 3. History Tracking
            history = ShipmentHistory(
                shipment_id=sid,
                status=shipment.status,
                event_summary=f"Progress: {tracking.progress_percentage:.1f}%, Risk: {risk.risk_category}"
            )
            await history.insert()
            
            # 4. ETA Calculation
            eta = await ShipmentETA.find(ShipmentETA.shipment_id == sid).sort("-calculated_at").first_or_none()
            original_eta_val = shipment.estimated_arrival
            
            eta_result = shipment_engine.calculate_eta(
                original_eta=original_eta_val,
                travel_time_hours=tracking.travel_time_remaining_hours,
                risk_score=risk.overall_risk_score
            )
            
            eta_doc = ShipmentETA(
                shipment_id=sid,
                original_eta=eta_result["original_eta"],
                updated_eta=eta_result["updated_eta"],
                best_case_eta=eta_result["best_case_eta"],
                worst_case_eta=eta_result["worst_case_eta"],
                most_probable_eta=eta_result["most_probable_eta"]
            )
            await eta_doc.insert()
            
            # 5. Delay Prediction
            pred_data = shipment_engine.predict_delay(
                original_eta=original_eta_val,
                updated_eta=eta_doc.most_probable_eta,
                risk_score=risk.overall_risk_score
            )
            
            prediction = ShipmentPrediction(
                shipment_id=sid,
                expected_delay_hours=pred_data["expected_delay_hours"],
                delay_probability=pred_data["delay_probability"],
                confidence_score=pred_data["confidence_score"],
                root_cause=pred_data["root_cause"]
            )
            await prediction.insert()
            
            # 6. AI Analysis & Alternative Routes (only if Risk is High/Critical or Delay > 12h)
            ai_data = None
            if risk.risk_category in ["High", "Critical"] or prediction.expected_delay_hours > 12:
                logger.info(f"High risk/delay detected for shipment {sid}. Generating AI analysis...")
                
                # Rank alternatives
                mock_routes = generate_mock_routes()
                ranked_routes = shipment_engine.rank_routes(mock_routes)
                
                route_doc = ShipmentRoute(
                    shipment_id=sid,
                    target_destination=shipment.destination,
                    recommended_routes=ranked_routes
                )
                await route_doc.insert()
                
                # Run Gemini
                ai_result = await shipment_ai_engine.analyze_shipment_delay(
                    shipment_id=sid,
                    current_location=tracking.current_location,
                    distance_remaining=tracking.distance_remaining_km,
                    eta_data=eta_doc.dict(),
                    prediction_data=prediction.dict(),
                    risk_data=risk.dict(),
                    routes=ranked_routes
                )
                
                ai_analysis = ShipmentAIAnalysis(
                    shipment_id=sid,
                    root_cause_explanation=ai_result.get("root_cause_explanation", ""),
                    business_impact=ai_result.get("business_impact", ""),
                    recommended_action=ai_result.get("recommended_action", ""),
                    recovery_strategy=ai_result.get("recovery_strategy", ""),
                    priority=ai_result.get("priority", "High"),
                    confidence_score=ai_result.get("confidence_score", 0.5)
                )
                await ai_analysis.insert()
                ai_data = ai_analysis.dict()
                
                # Create Alert
                alert = ShipmentAlert(
                    shipment_id=sid,
                    title=f"Shipment Delay Escalation: {risk.risk_category}",
                    message=f"Shipment {sid} is delayed by {prediction.expected_delay_hours:.1f} hours.",
                    severity=risk.risk_category,
                    event_type="Delay Escalation"
                )
                await alert.insert()
                
                # Send to Coordinator
                coord_payload = {
                    "agent": "Shipment Intelligence Agent",
                    "finding": f"Shipment {sid} faces a critical {prediction.expected_delay_hours:.1f}h delay.",
                    "severity": risk.risk_category,
                    "confidence": prediction.confidence_score,
                    "recommendations": [ai_result.get("recommended_action", "")],
                    "metadata": {
                        "shipment_id": sid,
                        "risk_score": risk.overall_risk_score,
                        "delay_hours": prediction.expected_delay_hours
                    },
                    "contributing_evidence": [ai_result.get("root_cause_explanation", "")]
                }
                
                coord_msg = CoordinatorMessage(
                    message_id=f"msg_shp_{sid}_{int(datetime.now().timestamp())}",
                    direction="outbound",
                    payload=coord_payload,
                    status="Pending"
                )
                await coord_msg.insert()
                
                results.append({
                    "shipment_id": sid,
                    "risk_category": risk.risk_category,
                    "finding": coord_payload["finding"],
                    "recommendations": ai_result.get("recommended_action", "")
                })
                
            # Broadcast update
            await manager.broadcast(json.dumps({
                "type": "SHIPMENT_UPDATE",
                "data": {
                    "shipment_id": sid,
                    "progress": tracking.progress_percentage,
                    "delay_hours": prediction.expected_delay_hours,
                    "risk_category": risk.risk_category,
                    "ai_analysis": ai_data
                }
            }))
            
        logger.info("Shipment monitor completed successfully.")
        return results
        
    except Exception as e:
        logger.error(f"Shipment monitor failed: {e}")
        return []
