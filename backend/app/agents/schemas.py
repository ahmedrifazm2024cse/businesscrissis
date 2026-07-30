from pydantic import BaseModel, Field
from typing import List, Optional

class CybersecurityOutput(BaseModel):
    threat_score: int = Field(description="Score from 1 to 10 indicating threat level")
    severity: str = Field(description="Critical, High, Medium, or Low")
    attack_type: str = Field(description="Description of the suspected attack")
    compromised_assets: List[str] = Field(description="List of potentially compromised assets")
    containment_steps: List[str] = Field(description="Recommended steps to contain the threat")
    confidence_score: float = Field(description="Confidence from 0.0 to 1.0")

class MarketIntelligenceOutput(BaseModel):
    strengths: List[str] = Field(description="Strengths of the business in the current situation")
    weaknesses: List[str] = Field(description="Weaknesses")
    opportunities: List[str] = Field(description="Market opportunities")
    threats: List[str] = Field(description="Market threats (competitors, etc.)")
    market_risk: str = Field(description="High, Medium, or Low")
    competitor_activity: str = Field(description="Observed competitor actions")
    business_opportunity: str = Field(description="Potential to capitalize on the crisis")

class CustomerReputationOutput(BaseModel):
    sentiment_score: int = Field(description="Score from 0 (very negative) to 100 (very positive)")
    customer_satisfaction: str = Field(description="Excellent, Good, Poor, or Critical")
    negative_topics: List[str] = Field(description="Trending negative topics among customers")
    brand_health: str = Field(description="Stable, Deteriorating, or Critical")

class OperationsOutput(BaseModel):
    operational_health: int = Field(description="Score from 0 to 100")
    downtime: str = Field(description="Estimated downtime in hours/mins")
    bottlenecks: List[str] = Field(description="Current operational bottlenecks")
    suggestions: List[str] = Field(description="Steps to restore operations")

class HROutput(BaseModel):
    employee_risk: str = Field(description="High, Medium, Low")
    attrition_score: int = Field(description="Predicted risk of employee loss (0-100)")
    morale: str = Field(description="High, Normal, Stressed, Poor")
    recommendations: List[str] = Field(description="Steps to protect and reassure staff")

class LegalComplianceOutput(BaseModel):
    compliance_score: int = Field(description="Score from 0 (breach) to 100 (compliant)")
    legal_risks: List[str] = Field(description="Specific legal and compliance risks")
    violated_regulations: List[str] = Field(description="Regulations potentially breached")
    mandatory_actions: List[str] = Field(description="Immediate legally required actions")

class FinancialRiskOutput(BaseModel):
    revenue_loss: str = Field(description="Estimated lost revenue (e.g., $1.2M)")
    projected_cost: str = Field(description="Estimated incident response cost")
    financial_risk: str = Field(description="Severe, High, Medium, Low")
    forecast: str = Field(description="Impact on quarterly targets")

class SupplyChainOutput(BaseModel):
    supply_chain_risk: str = Field(description="High, Medium, Low")
    affected_vendors: List[str] = Field(description="Suppliers impacted by the event")
    inventory_health: str = Field(description="Status of inventory")
    delay_prediction: str = Field(description="Estimated delays")

class PredictiveAnalyticsOutput(BaseModel):
    predictions: List[str] = Field(description="Future events predicted based on the crisis")
    probability: str = Field(description="High, Medium, Low")
    confidence: float = Field(description="Confidence score (0.0 to 1.0)")

class StrategyOutput(BaseModel):
    action_plan: List[str] = Field(description="High-level business continuity steps")
    priority_matrix: str = Field(description="Key priorities (P0, P1, etc.)")
    business_continuity_plan: str = Field(description="BCP status or recommendation")

class ExecutiveDecisionOutput(BaseModel):
    executive_summary: str = Field(description="Summary for the board")
    final_decision: str = Field(description="Final authorized business decision")
    recommended_action: str = Field(description="Key recommended action")
    priority: str = Field(description="P0, P1, P2")
    risk_score: int = Field(description="Overall enterprise risk (0-100)")
    confidence: float = Field(description="Confidence in the decision (0.0-1.0)")

class CommunicationPROutput(BaseModel):
    press_release: str = Field(description="Draft PR statement")
    customer_email: str = Field(description="Draft customer notification")
    internal_memo: str = Field(description="Draft staff memo")
    ceo_statement: str = Field(description="Draft CEO statement")

class ReportGeneratorOutput(BaseModel):
    report_url: str = Field(description="Link to generated report")
    status: str = Field(description="Generated or Failed")
