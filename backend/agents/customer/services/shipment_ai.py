import logging
import json
from typing import Dict, Any, List
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class ShipmentAIEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=settings.GEMINI_API_KEY,
            max_retries=2
        )
        
    async def analyze_shipment_delay(
        self,
        shipment_id: str,
        current_location: str,
        distance_remaining: float,
        eta_data: Dict[str, Any],
        prediction_data: Dict[str, Any],
        risk_data: Dict[str, Any],
        routes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generates AI analysis for delayed or high-risk shipments."""
        
        prompt = PromptTemplate.from_template(
            """
            You are an expert AI Supply Chain Logistics Analyst. Analyze the following in-transit shipment that is facing delays or high risks. Generate a comprehensive recovery and business impact plan.
            
            Shipment ID: {shipment_id}
            Current Location: {current_location}
            Distance Remaining: {distance_remaining} km
            
            ETA Projections:
            - Original ETA: {original_eta}
            - Most Probable Updated ETA: {updated_eta}
            - Worst Case ETA: {worst_case}
            
            Delay & Risk Data:
            - Delay Probability: {delay_prob}
            - Expected Delay Duration: {delay_hours} hours
            - Overall Risk Score: {risk_score}/100 (Category: {risk_category})
            - Key Risks: Weather ({weather_risk}), Traffic ({traffic_risk}), Port/Border ({port_risk})
            - Root Cause: {root_cause}
            
            Number of Alternative Routes Available: {alt_count}
            
            Generate a JSON object strictly adhering to the following schema. Do not include markdown formatting like ```json, just the raw JSON:
            {{
                "root_cause_explanation": "Detailed explanation of what is causing the delay.",
                "business_impact": "How this delay impacts downstream inventory, production, or customer satisfaction.",
                "recommended_action": "Immediate action the logistics team should take.",
                "recovery_strategy": "Long term strategy or rerouting logic to recover lost time.",
                "priority": "High, Medium, or Low",
                "confidence_score": <float 0.0-1.0>
            }}
            """
        )
        
        formatted_prompt = prompt.format(
            shipment_id=shipment_id,
            current_location=current_location,
            distance_remaining=distance_remaining,
            original_eta=eta_data.get("original_eta"),
            updated_eta=eta_data.get("most_probable_eta"),
            worst_case=eta_data.get("worst_case_eta"),
            delay_prob=prediction_data.get("delay_probability", 0),
            delay_hours=prediction_data.get("expected_delay_hours", 0),
            risk_score=risk_data.get("overall_risk_score", 0),
            risk_category=risk_data.get("risk_category", "Low"),
            weather_risk=risk_data.get("weather_risk", 0),
            traffic_risk=risk_data.get("traffic_risk", 0),
            port_risk=risk_data.get("port_congestion_risk", 0),
            root_cause=prediction_data.get("root_cause", "Unknown"),
            alt_count=len(routes)
        )

        try:
            response = await self.llm.ainvoke(formatted_prompt)
            response_text = response.content.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            data = json.loads(response_text)
            return data
            
        except Exception as e:
            logger.error(f"Error generating AI analysis for shipment {shipment_id}: {e}")
            return {
                "root_cause_explanation": "Unable to determine due to AI error.",
                "business_impact": "Unknown impact.",
                "recommended_action": "Manual review required.",
                "recovery_strategy": "Contact carrier directly.",
                "priority": "High",
                "confidence_score": 0.1
            }

shipment_ai_engine = ShipmentAIEngine()
