import logging
import json
from typing import Dict, Any, List
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class CostAIEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=settings.GEMINI_API_KEY,
            max_retries=2
        )
        
    async def analyze_costs(
        self,
        analysis_id: str,
        cost_data: Dict[str, float],
        trend_data: Dict[str, float],
        waste_flags: List[str]
    ) -> Dict[str, Any]:
        """Generates AI analysis for cost optimization, root causes, and long-term savings."""
        
        prompt = PromptTemplate.from_template(
            """
            You are an expert Supply Chain Chief Financial Officer (CFO). Analyze the following total supply chain cost breakdown, trends, and identified waste. Generate a strategic cost optimization and savings plan.
            
            Analysis ID: {analysis_id}
            
            Cost Breakdown:
            - Total Cost: ${total_cost}
            - Inventory Holding Cost: ${inv_cost}
            - Warehouse Cost: ${wh_cost}
            - Transportation Cost: ${trans_cost}
            - Procurement/Supplier Cost: ${proc_cost}
            - Fuel Cost: ${fuel_cost}
            - Emergency Shipping: ${emerg_cost}
            
            Trends:
            - Growth vs Last Period: {growth}%
            - Reduction vs Last Period: {reduction}%
            
            Identified Waste / Flags:
            {waste_flags}
            
            Generate a JSON object strictly adhering to the following schema. Do not include markdown formatting like ```json, just the raw JSON:
            {{
                "root_cause": "Primary reason for high costs or cost growth based on the data.",
                "cost_summary": "High-level summary of the financial health of the supply chain.",
                "cost_drivers": ["Driver 1", "Driver 2"],
                "business_impact": "Impact of these costs on margins and profitability.",
                "optimization_strategy": "Specific immediate steps to cut costs.",
                "long_term_savings_plan": "Strategic plan for sustainable cost reduction over 6-12 months.",
                "confidence_score": <float 0.0-1.0>
            }}
            """
        )
        
        formatted_prompt = prompt.format(
            analysis_id=analysis_id,
            total_cost=cost_data.get("total_cost", 0),
            inv_cost=cost_data.get("inventory_holding_cost", 0),
            wh_cost=cost_data.get("warehouse_cost", 0),
            trans_cost=cost_data.get("transportation_cost", 0),
            proc_cost=cost_data.get("procurement_cost", 0),
            fuel_cost=cost_data.get("fuel_cost", 0),
            emerg_cost=cost_data.get("emergency_shipping_cost", 0),
            growth=trend_data.get("growth_percentage", 0),
            reduction=trend_data.get("reduction_percentage", 0),
            waste_flags="\n".join([f"- {f}" for f in waste_flags]) if waste_flags else "None identified."
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
            logger.error(f"Error generating AI analysis for cost {analysis_id}: {e}")
            return {
                "root_cause": "Unable to determine due to AI error.",
                "cost_summary": "Cost evaluation pending.",
                "cost_drivers": ["Unknown"],
                "business_impact": "Potential margin degradation.",
                "optimization_strategy": "Review spending manually.",
                "long_term_savings_plan": "N/A",
                "confidence_score": 0.1
            }

cost_ai_engine = CostAIEngine()
