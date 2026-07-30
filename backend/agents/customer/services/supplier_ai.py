import logging
import json
from typing import Dict, Any, List
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class SupplierAIEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=settings.GEMINI_API_KEY,
            max_retries=2
        )
        
    async def analyze_supplier_risk(
        self,
        supplier_id: str,
        name: str,
        performance_metrics: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        failure_prediction: Dict[str, Any],
        alternatives: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generates AI analysis and recommendations based on supplier risk data."""
        
        prompt = PromptTemplate.from_template(
            """
            You are an expert AI Supply Chain Risk Analyst. Analyze the following supplier profile and generate a comprehensive risk mitigation and business continuity plan.
            
            Supplier: {name} (ID: {supplier_id})
            
            Performance Metrics:
            - Overall Performance Score: {performance_score}/100
            - On-Time Delivery: {otd}%
            - Quality Acceptance: {quality}%
            
            Risk Metrics:
            - Overall Risk Score: {risk_score}/100 (Category: {risk_category})
            - Key Risks: Financial ({financial_risk}), Country ({country_risk}), Single-Source Dependency ({dependency})
            
            Failure Prediction:
            - Probability of Failure: {failure_prob}
            - Expected Impact: {impact}
            
            Number of Alternative Suppliers Found: {alt_count}
            
            Generate a JSON object strictly adhering to the following schema. Do not include markdown formatting like ```json, just the raw JSON:
            {{
                "health_score": <float 0-100>,
                "reliability_score": <float 0-100>,
                "stability_score": <float 0-100>,
                "business_continuity_score": <float 0-100>,
                "root_cause": "Explanation of what might be driving the current risk/performance profile.",
                "business_impact": "Detailed explanation of how this affects the broader supply chain.",
                "recommended_actions": ["List", "of", "immediate", "actions"],
                "procurement_advice": "Strategic advice for procurement teams regarding this supplier.",
                "risk_mitigation_strategy": "Long term strategy to reduce dependency or risk.",
                "confidence_score": <float 0.0-1.0>
            }}
            """
        )
        
        formatted_prompt = prompt.format(
            supplier_id=supplier_id,
            name=name,
            performance_score=performance_metrics.get("overall_performance_score", 100),
            otd=performance_metrics.get("on_time_delivery_pct", 100),
            quality=performance_metrics.get("quality_acceptance_rate", 100),
            risk_score=risk_metrics.get("overall_risk_score", 0),
            risk_category=risk_metrics.get("risk_category", "Low"),
            financial_risk=risk_metrics.get("financial_risk", 0),
            country_risk=risk_metrics.get("country_risk", 0),
            dependency=risk_metrics.get("single_source_dependency", 0),
            failure_prob=failure_prediction.get("failure_probability", 0),
            impact=failure_prediction.get("estimated_business_impact", "Low"),
            alt_count=len(alternatives)
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
            logger.error(f"Error generating AI analysis for supplier {supplier_id}: {e}")
            return {
                "health_score": 50.0,
                "reliability_score": 50.0,
                "stability_score": 50.0,
                "business_continuity_score": 50.0,
                "root_cause": "Unable to determine due to AI error.",
                "business_impact": "Unknown impact.",
                "recommended_actions": ["Manual review required."],
                "procurement_advice": "Proceed with caution, manual review recommended.",
                "risk_mitigation_strategy": "Diversify supplier base.",
                "confidence_score": 0.1
            }

supplier_ai_engine = SupplierAIEngine()
