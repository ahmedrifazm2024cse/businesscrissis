import logging
import json
import random
import uuid
from google import genai
from core.config import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

class BusinessCrisisImpactAnalyzer:
    def __init__(self):
        self.max_score = 100.0

    def calculate_scores(self, telemetry: dict):
        """
        Takes in telemetry from all 9 modules and calculates raw business impact.
        """
        revenue_loss = 0.0
        profit_loss = 0.0
        inventory_loss = 0.0
        recovery_cost = 0.0
        recovery_time_days = 0.0
        customer_impact = 0.0
        production_delay_days = 0.0
        continuity_risk_score = 0.0

        # Extract shortage impact
        shortages = telemetry.get("shortages", [])
        for short in shortages:
            revenue_loss += short.get("revenue_impact_estimate", 0.0)
            profit_loss += short.get("revenue_impact_estimate", 0.0) * 0.3 # assumed 30% margin
            recovery_cost += 5000.0 # flat cost to expedite
            customer_impact += 10.0
            production_delay_days += 1.0

        # Extract supplier impact
        suppliers = telemetry.get("suppliers", [])
        for sup in suppliers:
            if sup.get("risk_category") in ["High", "Critical"] or sup.get("classification") in ["High Risk", "Critical", "Emergency"]:
                revenue_loss += 50000.0
                recovery_cost += 20000.0
                recovery_time_days = max(recovery_time_days, 14.0)
                continuity_risk_score += 25.0

        # Extract shipment impact
        shipments = telemetry.get("shipments", [])
        for ship in shipments:
            if ship.get("delay_probability", 0.0) > 0.7 or ship.get("delay_hours", 0) > 24:
                inventory_loss += 10000.0
                recovery_time_days = max(recovery_time_days, 5.0)
                production_delay_days += 2.0

        # Normalize Risk Scores
        total_risk = sum([s.get("risk_score", 0) for s in shortages]) + sum([s.get("risk_score", 0) for s in suppliers])
        business_risk_score = min(total_risk / max(len(shortages) + len(suppliers), 1), 100.0)
        
        continuity_risk_score = min(continuity_risk_score + business_risk_score * 0.3, 100.0)
        customer_impact = min(customer_impact, 100.0)
        
        # Determine Severity based on risk and loss
        business_impact_score = min((revenue_loss / 100000.0) * 50 + business_risk_score * 0.5, 100.0)
        business_health_score = max(0.0, 100.0 - business_impact_score)

        severity = "Low"
        if business_impact_score > 80 or continuity_risk_score > 80:
            severity = "Critical"
        elif business_impact_score > 60 or continuity_risk_score > 60:
            severity = "High"
        elif business_impact_score > 30:
            severity = "Medium"

        # Special emergency override
        if any(s.get("classification") == "Emergency" or s.get("risk_level") == "Emergency" for s in shortages):
            severity = "Critical"
            business_impact_score = max(business_impact_score, 90.0)
            business_health_score = 100.0 - business_impact_score

        return {
            "revenue_loss": revenue_loss,
            "profit_loss": profit_loss,
            "inventory_loss": inventory_loss,
            "recovery_cost": recovery_cost,
            "recovery_time_days": recovery_time_days,
            "customer_impact": customer_impact,
            "production_delay_days": production_delay_days,
            "continuity_risk_score": continuity_risk_score,
            "business_impact_score": business_impact_score,
            "business_risk_score": business_risk_score,
            "business_health_score": business_health_score,
            "crisis_severity": severity
        }

    async def analyze_with_ai(self, telemetry: dict, scores: dict) -> dict:
        """
        Uses Gemini to generate Executive Summary, Root Cause, Business Explanation, etc.
        """
        prompt = f"""
        You are the 'Business Crisis Impact Analyzer', the final intelligence layer of an autonomous Supply Chain Agent.
        Analyze the following telemetry from 9 distinct supply chain modules and the calculated business impact scores.

        Telemetry Data:
        {json.dumps(telemetry, indent=2)}

        Calculated Scores:
        {json.dumps(scores, indent=2)}

        Generate a structured JSON response containing:
        - "executive_summary": High-level summary of the overall business situation (max 2 sentences).
        - "root_cause": The primary driving force behind the most critical issues.
        - "business_explanation": Deep explanation of how the revenue, profit, and inventory losses are occurring.
        - "risk_explanation": Explanation of the overall business risk and health score.
        - "recovery_plan": Step-by-step strategic recovery plan across all domains (Inventory, Supplier, Shipment).
        - "business_recommendation": The single most important executive action to take right now.
        - "priority": "Low", "Medium", "High", "Critical".
        - "expected_business_outcome": What happens if the recommendation is followed.
        - "confidence": Float between 0.0 and 1.0.

        IMPORTANT: RETURN ONLY VALID JSON without markdown block formatting. Do not wrap in ```json ... ```.
        """

        try:
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
                
            result = json.loads(text.strip())
            return result
        except Exception as e:
            logger.error(f"Gemini API failure in Business Impact Analyzer: {e}")
            return {
                "executive_summary": "Failed to generate AI analysis.",
                "root_cause": "Unknown",
                "business_explanation": "Error connecting to AI.",
                "risk_explanation": "Error connecting to AI.",
                "recovery_plan": "Awaiting manual review.",
                "business_recommendation": "Investigate immediately.",
                "priority": scores.get("crisis_severity", "High"),
                "expected_business_outcome": "Unknown",
                "confidence": 0.0
            }

business_impact_analyzer = BusinessCrisisImpactAnalyzer()
