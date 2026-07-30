import logging
from datetime import datetime
import json
import random
from models.route_intelligence import (
    Route, TrafficAnalysis, WeatherAnalysis, FuelAnalysis, RouteRisk,
    RoutePrediction, RouteRecommendation, RouteAlert, RouteHistory, RouteAIAnalysis
)
from models.domain import CoordinatorMessage
from services.route_engine import route_engine
from services.route_ai import route_ai_engine
from api.routers.websockets import manager

logger = logging.getLogger(__name__)

async def run_route_monitor():
    """Autonomous Background Monitor - evaluates all active logistics routes."""
    logger.info("Running autonomous route intelligence monitor...")
    
    try:
        results = []
        active_routes = await Route.find(Route.status == "Active").to_list()
        
        # If no active routes, mock one for demonstration
        if not active_routes:
            logger.info("No active routes found. Mocking an active route for analysis.")
            mock_route = Route(
                route_id=f"RT-{random.randint(1000,9999)}",
                origin="WH-CHICAGO",
                destination="HUB-DALLAS",
                distance_km=1500.0,
                estimated_travel_time_hours=15.0,
                vehicle_type="Truck",
                shipment_priority="Critical",
                status="Active"
            )
            await mock_route.insert()
            active_routes = [mock_route]

        for route in active_routes:
            # 1. Fetch Traffic & Weather
            traffic = route_engine.get_traffic_data(route.origin, route.destination)
            ta = TrafficAnalysis(route_id=route.route_id, **traffic)
            await ta.insert()
            
            weather = route_engine.get_weather_data(route.destination)
            wa = WeatherAnalysis(route_id=route.route_id, **weather)
            await wa.insert()
            
            # 2. Risk & Fuel
            overall_risk_score, risk_level = route_engine.calculate_overall_risk(
                traffic["traffic_risk_score"], 
                weather["weather_risk_score"]
            )
            rr = RouteRisk(
                route_id=route.route_id,
                traffic_risk=traffic["traffic_risk_score"],
                weather_risk=weather["weather_risk_score"],
                political_risk=10,
                security_risk=10,
                road_quality_risk=20,
                vehicle_risk=5,
                overall_risk_score=overall_risk_score,
                risk_level=risk_level
            )
            await rr.insert()
            
            fuel = route_engine.calculate_fuel(route.distance_km, route.vehicle_type, traffic["traffic_risk_score"])
            fa = FuelAnalysis(route_id=route.route_id, **fuel)
            await fa.insert()
            
            # 3. ETA Prediction
            etas = route_engine.predict_eta(
                route.estimated_travel_time_hours, 
                traffic["traffic_risk_score"], 
                weather["weather_risk_score"]
            )
            rp = RoutePrediction(route_id=route.route_id, **etas)
            await rp.insert()

            # 4. Trigger AI & Coordinator if Risk is High/Critical
            ai_data = None
            if risk_level in ["High", "Critical"] or etas["delay_probability"] > 0.4:
                logger.info(f"High risk detected on route {route.route_id}. Running AI analysis...")
                
                # Alert
                alert = RouteAlert(
                    route_id=route.route_id,
                    title=f"{risk_level} Route Risk Detected",
                    message=f"Traffic/Weather conditions have elevated risk to {overall_risk_score}/100.",
                    severity="Critical" if risk_level == "Critical" else "Warning"
                )
                await alert.insert()
                
                # AI
                ai_result = await route_ai_engine.analyze_route(
                    route_id=route.route_id,
                    origin=route.origin,
                    destination=route.destination,
                    traffic_data=traffic,
                    weather_data=weather,
                    fuel_data=fuel,
                    risk_score=overall_risk_score,
                    risk_level=risk_level
                )
                
                ai_analysis = RouteAIAnalysis(
                    route_id=route.route_id,
                    **ai_result
                )
                await ai_analysis.insert()
                ai_data = ai_analysis.dict()
                
                # Recommendation
                rec = RouteRecommendation(
                    route_id=route.route_id,
                    recommendation_type="Emergency Reroute" if risk_level == "Critical" else "Alternative Route",
                    reason=ai_result.get("reason_for_selection", "Mitigate risk."),
                    estimated_savings_usd=ai_result.get("expected_savings", 0.0),
                    time_saved_hours=route.estimated_travel_time_hours * 0.2, # mock save 20%
                    priority="High",
                    confidence=ai_result.get("confidence_score", 0.8)
                )
                await rec.insert()

                # Coordinator Escalation
                coord_payload = {
                    "agent": "Route Optimization Agent",
                    "finding": f"Severe routing risk ({risk_level}) on route {route.route_id} due to traffic/weather.",
                    "severity": "High",
                    "confidence": ai_result.get("confidence_score", 0.9),
                    "recommendations": [ai_result.get("alternative_route_description", "Reroute immediately.")],
                    "metadata": {
                        "route_id": route.route_id,
                        "delay_probability": etas["delay_probability"]
                    },
                    "contributing_evidence": [
                        f"Congestion: {traffic['congestion_level']}",
                        f"Weather: {', '.join(weather['conditions'])}"
                    ]
                }
                
                coord_msg = CoordinatorMessage(
                    message_id=f"msg_route_{route.route_id}_{int(datetime.now().timestamp())}",
                    direction="outbound",
                    payload=coord_payload,
                    status="Pending"
                )
                await coord_msg.insert()
                
                results.append({
                    "route_id": route.route_id,
                    "risk_level": risk_level,
                    "finding": coord_payload["finding"],
                    "recommendation": ai_result.get("alternative_route_description", "Reroute immediately.")
                })

            # Broadcast
            await manager.broadcast(json.dumps({
                "type": "ROUTE_UPDATE",
                "data": {
                    "route_id": route.route_id,
                    "risk_level": risk_level,
                    "delay_prob": etas["delay_probability"],
                    "ai_analysis": ai_data
                }
            }))
            
        logger.info(f"Route monitor completed successfully. Analyzed {len(active_routes)} routes.")
        return results
        
    except Exception as e:
        logger.error(f"Route monitor failed: {e}")
        return []
