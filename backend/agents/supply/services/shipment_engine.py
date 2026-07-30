import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ShipmentEngine:
    def __init__(self):
        pass

    def calculate_risk(self, risks: Dict[str, float], tracking_progress: float) -> Dict[str, Any]:
        """
        Calculates shipment transportation risk.
        Progress reduces risk as it gets closer to destination.
        """
        weights = {
            "traffic_risk": 0.25,
            "weather_risk": 0.25,
            "port_congestion_risk": 0.20,
            "border_delay_risk": 0.20,
            "political_risk": 0.10
        }
        
        overall_risk = sum(risks.get(k, 0.0) * w for k, w in weights.items())
        
        # Risk theoretically drops as we get closer to destination, 
        # unless it's a specific port delay at the end
        progress_factor = 1.0 - (tracking_progress / 100.0 * 0.3) 
        overall_risk = overall_risk * progress_factor
        
        category = "Low"
        if overall_risk > 75:
            category = "Critical"
        elif overall_risk > 50:
            category = "High"
        elif overall_risk > 25:
            category = "Medium"
            
        health_score = max(0.0, 100.0 - overall_risk)
        
        return {
            "overall_risk_score": round(overall_risk, 2),
            "risk_category": category,
            "health_score": round(health_score, 2)
        }

    def calculate_eta(self, original_eta: datetime, travel_time_hours: float, risk_score: float) -> Dict[str, Any]:
        """
        Calculates Best, Worst, and Most Probable ETAs.
        """
        base_time = datetime.now()
        most_probable = base_time + timedelta(hours=travel_time_hours)
        
        # Best case: Traffic clears up, weather is perfect, travel time reduces by 10%
        best_case = base_time + timedelta(hours=travel_time_hours * 0.9)
        
        # Worst case: Risk score heavily impacts delay
        # Every 10 points of risk adds 5% extra travel time
        worst_case_multiplier = 1.0 + (risk_score / 10.0 * 0.05)
        worst_case = base_time + timedelta(hours=travel_time_hours * worst_case_multiplier)
        
        # Most probable ETA adjusts based on risk slightly
        probable_multiplier = 1.0 + (risk_score / 10.0 * 0.02)
        updated_eta = base_time + timedelta(hours=travel_time_hours * probable_multiplier)
        
        return {
            "original_eta": original_eta,
            "updated_eta": updated_eta,
            "best_case_eta": best_case,
            "worst_case_eta": worst_case,
            "most_probable_eta": updated_eta
        }

    def predict_delay(self, original_eta: datetime, updated_eta: datetime, risk_score: float) -> Dict[str, Any]:
        """
        Calculates delay probability and duration.
        """
        delay_delta = updated_eta - original_eta
        delay_hours = delay_delta.total_seconds() / 3600.0
        
        if delay_hours <= 0:
            return {
                "expected_delay_hours": 0.0,
                "delay_probability": 0.0,
                "confidence_score": 0.9,
                "root_cause": "None"
            }
            
        # Probability scales with risk
        prob = min(1.0, (risk_score / 100.0) + (delay_hours / 48.0))
        
        # Confidence is higher if we have a lot of risk data
        confidence = min(0.95, 0.5 + (risk_score / 200.0))
        
        root_cause = "Traffic & Weather"
        if risk_score > 70:
            root_cause = "Severe Transportation Disruption"
            
        return {
            "expected_delay_hours": round(delay_hours, 1),
            "delay_probability": round(prob, 2),
            "confidence_score": round(confidence, 2),
            "root_cause": root_cause
        }

    def rank_routes(self, routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks alternative routes based on distance, time, and risk.
        Assumes route has: route_name, distance_km, estimated_time_hours, risk_score
        """
        ranked = []
        for r in routes:
            dist = r.get("distance_km", 100)
            time = r.get("estimated_time_hours", 10)
            risk = r.get("risk_score", 50)
            
            # Lower is better. Let's normalize around standard values
            dist_score = max(0, 100 - (dist / 1000 * 100))
            time_score = max(0, 100 - (time / 24 * 100))
            risk_score = 100 - risk
            
            match = (time_score * 0.5) + (risk_score * 0.3) + (dist_score * 0.2)
            
            r["rank_score"] = round(match, 2)
            ranked.append(r)
            
        ranked.sort(key=lambda x: x["rank_score"], reverse=True)
        
        for idx, item in enumerate(ranked):
            item["rank"] = idx + 1
            
        return ranked

shipment_engine = ShipmentEngine()
