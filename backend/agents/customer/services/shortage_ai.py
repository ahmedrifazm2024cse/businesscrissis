import logging
import json
from typing import Dict, Any, List
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class ShortageAIEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=settings.GEMINI_API_KEY,
            max_retries=2
        )
        
    async def analyze_shortage(
        self,
        product_id: str,
        sku: str,
        probability: float,
        days_remaining: float,
        root_causes: List[str],
        risk_classification: str,
        revenue_impact: float
    ) -> Dict[str, Any]:
        """Generates AI analysis for a predicted shortage."""
        
        prompt = PromptTemplate.from_template(
            """
            You are an expert Supply Chain Crisis Manager. Analyze the following predicted product shortage and generate a recovery strategy.
            
            Product ID: {product_id}
            SKU: {sku}
            
            Shortage Telemetry:
            - Probability of Shortage: {probability}%
            - Days Remaining of Stock: {days_remaining}
            - Engine-Detected Root Causes: {root_causes}
            - Risk Classification: {risk_classification}
            - Estimated Revenue Impact: ${revenue_impact}
            
            Generate a JSON object strictly adhering to the following schema. Do not include markdown formatting like ```json, just the raw JSON:
            {{
                "root_cause": "Detailed synthesis of why this shortage is happening.",
                "business_explanation": "A high-level explanation of the business impact if unmitigated.",
                "shortage_summary": "A 1-sentence summary of the crisis.",
                "recommended_actions": [
                    "Action 1 (e.g. Emergency Procurement)",
                    "Action 2"
                ],
                "recovery_strategy": "A step-by-step tactical plan to prevent or mitigate the shortage over the next 7 days.",
                "long_term_prevention_strategy": "Strategic changes to prevent recurrence (e.g. adjust safety stock, diversify suppliers).",
                "confidence_score": <float 0.0-1.0>
            }}
            """
        )
        
        formatted_prompt = prompt.format(
            product_id=product_id,
            sku=sku,
            probability=probability * 100,
            days_remaining=days_remaining,
            root_causes=", ".join(root_causes),
            risk_classification=risk_classification,
            revenue_impact=revenue_impact
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
            logger.error(f"Error generating AI shortage analysis for {sku}: {e}")
            return {
                "root_cause": "Unable to determine due to AI service error.",
                "business_explanation": "Potential revenue loss if inventory drops to zero.",
                "shortage_summary": f"Predicted shortage for {sku}.",
                "recommended_actions": ["Review inventory levels manually."],
                "recovery_strategy": "Expedite incoming orders.",
                "long_term_prevention_strategy": "Increase safety stock.",
                "confidence_score": 0.1
            }

shortage_ai_engine = ShortageAIEngine()
