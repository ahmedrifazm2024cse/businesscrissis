import logging
import json
from typing import Dict, Any, List
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class WarehouseAIEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=settings.GEMINI_API_KEY,
            max_retries=2
        )
        
    async def analyze_warehouse_bottlenecks(
        self,
        warehouse_id: str,
        name: str,
        capacity_data: Dict[str, Any],
        prediction_data: Dict[str, Any],
        risk_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates AI analysis for warehouse capacity breaches and bottlenecks."""
        
        prompt = PromptTemplate.from_template(
            """
            You are an expert AI Warehouse Operations Manager. Analyze the following warehouse telemetry and generate an optimization and recovery plan.
            
            Warehouse: {name} (ID: {warehouse_id})
            
            Capacity & Utilization:
            - Overall Utilization: {utilization}%
            - Available Capacity: {available_capacity} units
            - Cold Storage Used: {cold_storage}
            
            Predictions:
            - Capacity Remaining Days: {capacity_remaining_days}
            - Overflow Risk Score: {overflow_risk}/100
            
            Health & Bottlenecks:
            - Overall Health Score: {health_score}/100
            - Active Bottlenecks: {bottlenecks}
            - Safety/Environmental Risks: Fire ({fire_risk}), Equipment ({equipment_risk})
            
            Generate a JSON object strictly adhering to the following schema. Do not include markdown formatting like ```json, just the raw JSON:
            {{
                "root_cause": "Detailed explanation of the primary bottleneck or capacity issue.",
                "warehouse_summary": "High-level summary of operational status.",
                "operational_risks": "Description of safety, equipment, or throughput risks.",
                "business_impact": "Impact on fulfillment, shipping times, or spoiled goods.",
                "optimization_strategy": "Strategic actions to clear bottlenecks or free up capacity.",
                "recovery_plan": "Immediate next steps for the local warehouse manager.",
                "confidence_score": <float 0.0-1.0>
            }}
            """
        )
        
        formatted_prompt = prompt.format(
            warehouse_id=warehouse_id,
            name=name,
            utilization=capacity_data.get("utilization_percentage", 0),
            available_capacity=capacity_data.get("available_capacity", 0),
            cold_storage=capacity_data.get("cold_storage_used", 0),
            capacity_remaining_days=prediction_data.get("capacity_remaining_days", "N/A"),
            overflow_risk=prediction_data.get("overflow_risk_score", 0),
            health_score=risk_data.get("health_score", 100),
            bottlenecks=", ".join(risk_data.get("bottlenecks_detected", [])),
            fire_risk=risk_data.get("fire_risk", 0),
            equipment_risk=risk_data.get("equipment_risk", 0)
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
            logger.error(f"Error generating AI analysis for warehouse {warehouse_id}: {e}")
            return {
                "root_cause": "Unable to determine due to AI error.",
                "warehouse_summary": "Status unknown.",
                "operational_risks": "Unknown risks.",
                "business_impact": "Potential fulfillment delays.",
                "optimization_strategy": "Manual review required.",
                "recovery_plan": "Inspect facility physically.",
                "confidence_score": 0.1
            }

warehouse_ai_engine = WarehouseAIEngine()
