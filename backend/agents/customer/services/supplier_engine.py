import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SupplierEngine:
    def __init__(self):
        pass

    def calculate_performance_score(self, metrics: Dict[str, float]) -> float:
        """
        Calculates a 0-100 score based on supplier metrics.
        Weights:
        - OTD (On Time Delivery): 40%
        - Quality Acceptance: 30%
        - Order Fulfillment: 20%
        - SLA Compliance: 10%
        Penalties:
        - High defect rate reduces score.
        - Cancellations / Returns reduce score.
        """
        otd = metrics.get("on_time_delivery_pct", 100.0)
        quality = metrics.get("quality_acceptance_rate", 100.0)
        fulfillment = metrics.get("order_fulfillment_rate", 100.0)
        sla = metrics.get("sla_compliance", 100.0)
        
        base_score = (otd * 0.4) + (quality * 0.3) + (fulfillment * 0.2) + (sla * 0.1)
        
        defect = metrics.get("defect_rate", 0.0)
        cancellation = metrics.get("cancellation_rate", 0.0)
        returns = metrics.get("return_rate", 0.0)
        
        # Penalties: deduct points based on failure rates
        penalty = (defect * 2.0) + (cancellation * 1.5) + (returns * 1.5)
        
        final_score = max(0.0, min(100.0, base_score - penalty))
        return round(final_score, 2)

    def calculate_risk_score(self, risks: Dict[str, float]) -> Dict[str, Any]:
        """
        Aggregates multiple risk vectors (0-100 scale where 100 is highest risk).
        """
        weights = {
            "financial_risk": 0.2,
            "delivery_risk": 0.2,
            "country_risk": 0.1,
            "political_risk": 0.1,
            "natural_disaster_risk": 0.1,
            "single_source_dependency": 0.15,
            "capacity_risk": 0.1,
            "compliance_risk": 0.05
        }
        
        overall_risk = 0.0
        for key, weight in weights.items():
            overall_risk += risks.get(key, 0.0) * weight
            
        category = "Low"
        if overall_risk > 75:
            category = "Critical"
        elif overall_risk > 50:
            category = "High"
        elif overall_risk > 25:
            category = "Medium"
            
        return {
            "overall_risk_score": round(overall_risk, 2),
            "risk_category": category
        }

    def predict_failure(self, performance: float, risk_score: float, delay_days: float) -> Dict[str, Any]:
        """
        Predicts failure probability (0.0 to 1.0) and expected delay.
        """
        # Baseline probability based on risk (scale 0 to 1)
        prob_risk = risk_score / 100.0
        
        # Performance factor (Low performance increases failure prob)
        prob_perf = max(0.0, (100.0 - performance) / 100.0)
        
        # Delay factor (Exponentially increases risk as delays pile up)
        prob_delay = min(1.0, delay_days / 30.0)
        
        failure_prob = (prob_risk * 0.5) + (prob_perf * 0.3) + (prob_delay * 0.2)
        failure_prob = min(1.0, failure_prob)
        
        expected_disruption = None
        if failure_prob > 0.6:
            days_to_fail = max(1, int((1.0 - failure_prob) * 30))
            expected_disruption = datetime.now() + timedelta(days=days_to_fail)
            
        impact = "Low"
        if failure_prob > 0.8:
            impact = "Critical"
        elif failure_prob > 0.5:
            impact = "High"
            
        return {
            "failure_probability": round(failure_prob, 2),
            "expected_disruption_date": expected_disruption,
            "expected_delivery_delays_days": delay_days * (1.0 + failure_prob),
            "estimated_business_impact": impact,
            "confidence_score": round(min(0.95, failure_prob + 0.1), 2)
        }

    def rank_alternatives(self, target_supplier: Dict, alternatives: List[Dict]) -> List[Dict]:
        """
        Ranks alternative suppliers based on cost, distance, capacity, and risk.
        Assumes each alternative dictionary has: id, cost_multiplier, distance_km, risk_score, capacity_pct
        """
        ranked = []
        for alt in alternatives:
            # Score formula (lower is better for cost/distance/risk, higher is better for capacity)
            # Normalize to 0-100 scale where higher is a better match
            cost_score = max(0, 100 - (alt.get('cost_multiplier', 1.0) - 1.0) * 100)
            distance_score = max(0, 100 - (alt.get('distance_km', 1000) / 100))
            risk_score = 100 - alt.get('risk_score', 50)
            capacity_score = min(100, alt.get('capacity_pct', 50))
            
            total_match = (cost_score * 0.4) + (capacity_score * 0.3) + (risk_score * 0.2) + (distance_score * 0.1)
            
            ranked.append({
                "supplier_id": alt.get('id'),
                "match_score": round(total_match, 2),
                "cost_multiplier": alt.get('cost_multiplier'),
                "lead_time_days": alt.get('distance_km', 100) / 50 # rough estimate
            })
            
        ranked.sort(key=lambda x: x["match_score"], reverse=True)
        
        for idx, item in enumerate(ranked):
            item["rank"] = idx + 1
            
        return ranked

supplier_engine = SupplierEngine()
