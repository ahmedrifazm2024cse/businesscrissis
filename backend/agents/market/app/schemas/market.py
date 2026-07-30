from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class MarketAnalysisResponse(BaseModel):
    agent: str = "Market Intelligence"
    marketRiskScore: int = Field(..., alias="marketRiskScore")
    competitorThreat: str = Field(..., alias="competitorThreat")
    marketOpportunity: str = Field(..., alias="marketOpportunity")
    demandForecast: str = Field(..., alias="demandForecast")
    confidence: int
    keyFindings: List[str] = Field(..., alias="keyFindings")
    recommendations: List[str] = Field(..., alias="recommendations")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "agent": "Market Intelligence",
                "marketRiskScore": 82,
                "competitorThreat": "High",
                "marketOpportunity": "Medium",
                "demandForecast": "Demand expected to increase by 12%",
                "confidence": 95,
                "keyFindings": ["Competitor Alpha launched a premium tier feature", "Economic inflation dropping slightly"],
                "recommendations": ["Optimize standard tier pricing", "Target edge computing niche market"]
            }
        }

class CompetitorDataSchema(BaseModel):
    competitor_id: int
    name: str
    product_name: str
    feature_set: str
    market_share: float
    pricing_tier: str
    sentiment_score: float
    last_launch_date: str
    status: str

class NewsItemSchema(BaseModel):
    date: str
    title: str
    summary: str
    source: str
    sentiment: str
    impact_score: int

class PricingCompareSchema(BaseModel):
    competitor_name: str
    plan_name: str
    price_monthly: float
    features_included: str

class TrendItemSchema(BaseModel):
    quarter: str
    trend_name: str
    adoption_rate: float
    growth_rate: float
    sentiment: str
    primary_driver: str

class DemandPointSchema(BaseModel):
    month: str
    sales_units: int
    nps: int
    lead_conversion_rate: float

class DemandForecastSchema(BaseModel):
    historical: List[DemandPointSchema]
    forecast: List[DemandPointSchema]
    message: str

class DashboardDataResponse(BaseModel):
    marketRiskScore: int
    competitorThreat: str
    marketOpportunity: str
    demandForecastSummary: str
    confidence: int
    competitors: List[CompetitorDataSchema]
    news: List[NewsItemSchema]
    pricing: List[PricingCompareSchema]
    trends: List[TrendItemSchema]
    demandForecast: DemandForecastSchema
    recommendations: List[str]

class RiskDetailsResponse(BaseModel):
    overallScore: int
    competitorThreatScore: int
    economicRiskScore: int
    demandRiskScore: int
    riskFactors: List[Dict[str, Any]]

class OpportunityDetailsResponse(BaseModel):
    overallOpportunityScore: int
    opportunities: List[Dict[str, Any]]

class CrisisAnalysisRequest(BaseModel):
    company_name: str
    industry: str
    crisis_type: str
    crisis_description: str
    current_market_trend: str
    competitor_information: str
    customer_demand: str
    location: str

class CrisisAnalysisResponse(BaseModel):
    market_summary: str
    market_impact: str
    competitor_analysis: str
    customer_demand_prediction: str
    business_opportunities: List[str]
    market_risk_score: str
    recommendations: List[str]

