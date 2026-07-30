import logging
import json
from typing import Dict, Any
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class DemandAIEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=settings.GEMINI_API_KEY,
            max_retries=2
        )
        
    async def analyze_forecast(
        self, 
        sku: str, 
        trend: str, 
        seasonality: Dict[str, Any], 
        demand_pattern: str, 
        forecast_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates AI analysis and recommendations based on forecast data."""
        
        prompt = PromptTemplate.from_template(
            """
            You are an expert AI Supply Chain Demand Forecaster. Analyze the following demand data and provide a detailed business analysis and recommendation.
            
            Product SKU: {sku}
            
            Metrics:
            - Trend: {trend}
            - Seasonality: {seasonality}
            - Demand Pattern: {demand_pattern}
            - Expected Demand: {expected_demand}
            - Confidence Score: {confidence}
            - Forecast Algorithm: {algorithm}
            
            Generate a JSON object strictly adhering to the following schema. Do not include markdown formatting like ```json, just the raw JSON:
            {{
                "root_cause": "Explanation of what might be driving this demand trend.",
                "demand_explanation": "Detailed explanation of the forecast.",
                "business_reason": "Why this matters to the business.",
                "forecast_summary": "Short summary of the forecast.",
                "potential_risks": "Risks if this forecast is inaccurate or if no action is taken.",
                "suggested_actions": ["List", "of", "actions"],
                "business_opportunities": "Opportunities presented by this trend.",
                "recommendation": {{
                    "action_type": "Increase inventory | Reduce inventory | Delay procurement | Emergency procurement | Move inventory",
                    "reason": "Why this action is needed",
                    "priority": "Critical | High | Medium | Low",
                    "expected_impact": "Impact of taking this action"
                }}
            }}
            """
        )
        
        formatted_prompt = prompt.format(
            sku=sku,
            trend=trend,
            seasonality=seasonality.get('seasonality', 'None'),
            demand_pattern=demand_pattern,
            expected_demand=forecast_metrics.get("expected_demand"),
            confidence=forecast_metrics.get("confidence_score"),
            algorithm=forecast_metrics.get("algorithm_used")
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
            logger.error(f"Error generating AI analysis for {sku}: {e}")
            return {
                "root_cause": "Unable to determine",
                "demand_explanation": "Error analyzing demand.",
                "business_reason": "N/A",
                "forecast_summary": f"Forecast generated using {forecast_metrics.get('algorithm_used')}.",
                "potential_risks": "Unmonitored demand changes.",
                "suggested_actions": ["Review manually"],
                "business_opportunities": "N/A",
                "recommendation": {
                    "action_type": "Review manually",
                    "reason": "AI analysis failed",
                    "priority": "Medium",
                    "expected_impact": "Risk mitigation"
                }
            }

demand_ai_engine = DemandAIEngine()
