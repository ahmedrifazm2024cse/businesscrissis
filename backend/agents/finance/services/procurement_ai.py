import logging
import json
from typing import Dict, Any
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class ProcurementAIEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=settings.GEMINI_API_KEY,
            max_retries=2
        )
        
    async def analyze_procurement_plan(
        self,
        plan_id: str,
        sku: str,
        plan_data: Dict[str, Any],
        risk_data: Dict[str, Any],
        prediction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates AI analysis for procurement planning, negotiation, and risk mitigation."""
        
        prompt = PromptTemplate.from_template(
            """
            You are an expert AI Chief Procurement Officer. Analyze the following procurement plan telemetry and generate a strategic purchase and negotiation plan.
            
            Plan: {plan_id} for SKU: {sku}
            
            Order Details:
            - Order Quantity (EOQ): {eoq} units
            - Timing Strategy: {timing_strategy}
            - Estimated Cost: ${estimated_cost}
            
            Predictions:
            - Predicted Price Change: {price_change}%
            - Market Trend: {market_trend}
            
            Risks:
            - Overall Risk Score: {overall_risk}/100
            - Supplier Risk: {supplier_risk}
            - Currency Risk: {currency_risk}
            
            Generate a JSON object strictly adhering to the following schema. Do not include markdown formatting like ```json, just the raw JSON:
            {{
                "purchase_strategy": "High-level strategic approach (e.g., lock in long-term contract now due to rising prices).",
                "negotiation_strategy": "Specific tactics to use with the supplier to lower costs.",
                "supplier_recommendation": "Advice on whether to stick with the primary supplier or diversify.",
                "expected_savings_explanation": "Explanation of how this strategy saves money.",
                "business_impact": "Impact on production, sales, or cash flow.",
                "risk_mitigation": "How to mitigate the identified risks.",
                "confidence_score": <float 0.0-1.0>
            }}
            """
        )
        
        formatted_prompt = prompt.format(
            plan_id=plan_id,
            sku=sku,
            eoq=plan_data.get("eoq", 0),
            timing_strategy=plan_data.get("timing_strategy", "Unknown"),
            estimated_cost=plan_data.get("estimated_cost", 0),
            price_change=prediction_data.get("predicted_price_change", 0),
            market_trend=prediction_data.get("market_trend", "Stable"),
            overall_risk=risk_data.get("overall_risk_score", 0),
            supplier_risk=risk_data.get("supplier_risk", 0),
            currency_risk=risk_data.get("currency_risk", 0)
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
            logger.error(f"Error generating AI analysis for procurement plan {plan_id}: {e}")
            return {
                "purchase_strategy": "Unable to determine due to AI error.",
                "negotiation_strategy": "Standard negotiation.",
                "supplier_recommendation": "Review manually.",
                "expected_savings_explanation": "Unknown.",
                "business_impact": "Potential cost overruns.",
                "risk_mitigation": "Review risks manually.",
                "confidence_score": 0.1
            }

procurement_ai_engine = ProcurementAIEngine()
