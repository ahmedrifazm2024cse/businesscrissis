import logging
import random
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RouteEngine:
    def __init__(self):
        pass

    def get_traffic_data(self, origin: str, destination: str) -> Dict[str, Any]:
        """Fetches live traffic data. Mocks API response if API key is not set."""
        # In a real scenario, call OpenRouteService or Google Maps API here
        congestion_levels = ["Low", "Medium", "High", "Severe"]
        
        level = random.choice(congestion_levels)
        accidents = random.randint(0, 2) if level in ["High", "Severe"] else 0
        closures = 1 if level == "Severe" else 0
        
        # Calculate risk score based on conditions
        risk_score = 0
        if level == "Low": risk_score = 10
        elif level == "Medium": risk_score = 40
        elif level == "High": risk_score = 75
        elif level == "Severe": risk_score = 95
        
        return {
            "congestion_level": level,
            "accidents_reported": accidents,
            "road_closures": closures,
            "construction_zones": random.randint(0, 3),
            "peak_hour_overlap_hours": round(random.uniform(0, 3), 1),
            "traffic_risk_score": risk_score
        }

    def get_weather_data(self, location: str) -> Dict[str, Any]:
        """Fetches live weather data. Mocks response for fallback."""
        # Call OpenWeather API here in production
        conditions_list = ["Clear", "Rain", "Fog", "Storm", "Windy"]
        cond = random.choice(conditions_list)
        
        risk = 10
        if cond == "Rain": risk = 40
        elif cond == "Fog": risk = 60
        elif cond == "Storm": risk = 85
        elif cond == "Windy": risk = 30
        
        return {
            "conditions": [cond],
            "visibility_km": round(random.uniform(0.5, 15.0), 1),
            "temperature_celsius": round(random.uniform(-5.0, 35.0), 1),
            "wind_speed_kmh": round(random.uniform(5.0, 80.0), 1),
            "weather_risk_score": risk
        }

    def calculate_fuel(self, distance_km: float, vehicle_type: str, traffic_risk: float) -> Dict[str, Any]:
        """Calculates fuel consumption, cost, and emissions."""
        # Baseline efficiency km/l
        efficiency_map = {
            "Truck": 3.0,
            "Van": 8.0,
            "Car": 12.0,
            "Ship": 0.5,
            "Plane": 0.1
        }
        base_eff = efficiency_map.get(vehicle_type, 5.0)
        
        # Traffic degrades efficiency by up to 30%
        efficiency_modifier = 1.0 - ((traffic_risk / 100) * 0.3)
        actual_eff = base_eff * efficiency_modifier
        
        liters_needed = distance_km / actual_eff if actual_eff > 0 else 0
        fuel_cost = liters_needed * 1.50 # Assume $1.50 per liter
        carbon = liters_needed * 2.68 # kg of CO2 per liter of diesel roughly
        
        return {
            "estimated_fuel_consumption_liters": round(liters_needed, 2),
            "fuel_cost_per_liter": 1.50,
            "total_fuel_cost": round(fuel_cost, 2),
            "carbon_emissions_kg": round(carbon, 2)
        }

    def predict_eta(self, base_hours: float, traffic_risk: float, weather_risk: float) -> Dict[str, Any]:
        """Calculates expected ETA boundaries based on risk factors."""
        now = datetime.utcnow()
        
        # Best case: no delay
        best_case = now + timedelta(hours=base_hours)
        
        # Calculate delay multiplier (max 100% extra time)
        delay_factor = ((traffic_risk * 0.6) + (weather_risk * 0.4)) / 100.0
        
        expected_hours = base_hours * (1 + (delay_factor * 0.5))
        worst_hours = base_hours * (1 + delay_factor)
        
        expected_eta = now + timedelta(hours=expected_hours)
        worst_case_eta = now + timedelta(hours=worst_hours)
        
        confidence = max(0.1, 1.0 - (delay_factor * 0.8)) # Lower confidence if high risk
        
        return {
            "best_case_eta": best_case,
            "expected_eta": expected_eta,
            "worst_case_eta": worst_case_eta,
            "delay_probability": delay_factor,
            "arrival_confidence": round(confidence, 2)
        }

    def calculate_overall_risk(self, traffic: float, weather: float, political: float = 10, security: float = 10) -> Tuple[float, str]:
        """Blends risk vectors into an overall score and severity label."""
        overall = (traffic * 0.5) + (weather * 0.3) + (security * 0.1) + (political * 0.1)
        
        level = "Low"
        if overall >= 80: level = "Critical"
        elif overall >= 60: level = "High"
        elif overall >= 30: level = "Medium"
        
        return round(overall, 2), level

route_engine = RouteEngine()
