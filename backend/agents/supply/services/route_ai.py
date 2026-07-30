import logging
import json
from typing import Dict, Any
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class RouteAIEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=settings.GEMINI_API_KEY,
            max_retries=2
        )
        
    async def analyze_route(
        self,
        route_id: str,
        origin: str,
        destination: str,
        traffic_data: Dict[str, Any],
        weather_data: Dict[str, Any],
        fuel_data: Dict[str, Any],
        risk_score: float,
        risk_level: str
    ) -> Dict[str, Any]:
        """Generates AI routing strategy based on traffic, weather, fuel, and risk telemetry."""
        
        prompt = PromptTemplate.from_template(
            """
            You are an expert Logistics Route Optimization AI. Analyze the following route telemetry and generate the optimal routing strategy.
            
            Route ID: {route_id}
            Origin: {origin}
            Destination: {destination}
            
            Traffic Data:
            - Congestion: {congestion}
            - Accidents: {accidents}
            - Closures: {closures}
            
            Weather Data:
            - Conditions: {conditions}
            - Visibility: {visibility} km
            - Wind Speed: {wind_speed} km/h
            
            Fuel / Emissions:
            - Total Fuel Cost: ${fuel_cost}
            - Carbon Emissions: {emissions} kg
            
            Overall Route Risk:
            - Score: {risk_score} (Level: {risk_level})
            
            Generate a JSON object strictly adhering to the following schema. Do not include markdown formatting like ```json, just the raw JSON:
            {{
                "best_route_description": "Description of the primary recommended path.",
                "alternative_route_description": "Description of an emergency alternative path if conditions worsen.",
                "reason_for_selection": "Why this route is optimal based on balancing speed, cost, and safety.",
                "business_impact": "Impact on customer satisfaction or supply chain timing.",
                "risk_analysis": "Summary of primary threats (e.g. weather, traffic) and mitigation.",
                "expected_savings": <float representing estimated USD saved by avoiding congestion/accidents>,
                "confidence_score": <float 0.0-1.0>
            }}
            """
        )
        
        formatted_prompt = prompt.format(
            route_id=route_id,
            origin=origin,
            destination=destination,
            congestion=traffic_data.get("congestion_level", "Unknown"),
            accidents=traffic_data.get("accidents_reported", 0),
            closures=traffic_data.get("road_closures", 0),
            conditions=", ".join(weather_data.get("conditions", [])),
            visibility=weather_data.get("visibility_km", "Unknown"),
            wind_speed=weather_data.get("wind_speed_kmh", "Unknown"),
            fuel_cost=fuel_data.get("total_fuel_cost", 0),
            emissions=fuel_data.get("carbon_emissions_kg", 0),
            risk_score=risk_score,
            risk_level=risk_level
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
            logger.error(f"Error generating AI routing for {route_id}: {e}")
            return {
                "best_route_description": "Proceed on standard route.",
                "alternative_route_description": "Hold in place if conditions degrade.",
                "reason_for_selection": "Unable to generate AI analysis.",
                "business_impact": "Standard delivery timing.",
                "risk_analysis": "Unknown - API Error.",
                "expected_savings": 0.0,
                "confidence_score": 0.1
            }

route_ai_engine = RouteAIEngine()
