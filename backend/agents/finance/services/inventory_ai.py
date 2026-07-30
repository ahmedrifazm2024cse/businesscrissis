import logging
import json
from typing import Dict, Any, List
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class RecommendationResponse(BaseModel):
    root_cause: str = Field(description="The predicted root cause of this inventory issue")
    business_impact: str = Field(description="The business impact if this issue is not resolved")
    recommended_action: str = Field(description="The recommended action to take")
    expected_outcome: str = Field(description="The expected outcome of the recommended action")
    priority: str = Field(description="Priority of the action: Low, Medium, High, or Critical")
    confidence: float = Field(description="Confidence score of this recommendation (0.0 to 1.0)")

class InventoryAIEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=settings.GEMINI_API_KEY,
            max_retries=2
        )
        
    async def generate_recommendation(
        self, 
        sku: str, 
        product_name: str, 
        health_metrics: Dict[str, Any], 
        prediction_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates AI recommendation for a critical inventory item."""
        
        prompt = PromptTemplate.from_template(
            """
            You are an expert AI Supply Chain Agent. Analyze the following inventory data and provide a detailed recommendation.
            
            Product: {sku} - {product_name}
            
            Health Metrics:
            - Available Stock: {available_stock}
            - Days Remaining: {days_remaining}
            - Health Score: {health_score}
            - Risk Score: {risk_score}
            - Status: {stock_status}
            - Overstock: {is_overstock}
            - Understock: {is_understock}
            - Dead Stock: {is_dead_stock}
            
            Prediction Metrics:
            - Expected Stockout Date: {stockout_date}
            - Stockout Probability: {probability}
            - Days Until Stockout: {days_until_stockout}
            - Forecast Method: {forecast_method}
            
            Generate a JSON object strictly adhering to the following schema, and do not include any markdown formatting or markdown code blocks (like ```json ... ```) in your output, just the raw JSON:
            {{
                "root_cause": "string",
                "business_impact": "string",
                "recommended_action": "string",
                "expected_outcome": "string",
                "priority": "High | Critical | Medium | Low",
                "confidence": float
            }}
            """
        )
        
        formatted_prompt = prompt.format(
            sku=sku,
            product_name=product_name,
            available_stock=health_metrics.get("available_stock"),
            days_remaining=health_metrics.get("days_remaining"),
            health_score=health_metrics.get("health_score"),
            risk_score=health_metrics.get("risk_score"),
            stock_status=health_metrics.get("stock_status"),
            is_overstock=health_metrics.get("is_overstock"),
            is_understock=health_metrics.get("is_understock"),
            is_dead_stock=health_metrics.get("is_dead_stock"),
            stockout_date=prediction_metrics.get("stockout_date"),
            probability=prediction_metrics.get("probability"),
            days_until_stockout=prediction_metrics.get("days_until_stockout"),
            forecast_method=prediction_metrics.get("forecast_method")
        )

        try:
            # Using structured output via Gemini model
            response = await self.llm.ainvoke(formatted_prompt)
            # Clean response text if it contains markdown formatting
            response_text = response.content.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            data = json.loads(response_text)
            return data
            
        except Exception as e:
            logger.error(f"Error generating AI recommendation for {sku}: {e}")
            return {
                "root_cause": "Unable to determine (AI Service Error)",
                "business_impact": "Potential revenue loss or overstock costs",
                "recommended_action": "Manually review stock levels",
                "expected_outcome": "Risk mitigation",
                "priority": "Medium",
                "confidence": 0.0
            }

inventory_ai_engine = InventoryAIEngine()
