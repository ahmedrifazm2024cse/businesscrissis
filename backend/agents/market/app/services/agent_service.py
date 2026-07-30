from sqlalchemy.orm import Session
from app.services.analytics import calculate_market_scores
from app.services.forecasting import forecast_demand
from app.agents.crew import run_market_intelligence_crew
from app.models.market_data import MarketAnalysisReport
from typing import Dict, Any

def execute_market_analysis(db: Session) -> MarketAnalysisReport:
    # 1. Calculate numerical scores
    scores = calculate_market_scores()
    
    # 2. Get demand forecast message
    forecast_results = forecast_demand()
    demand_msg = forecast_results["message"]
    
    # 3. Run CrewAI agents to generate text narrative & actions
    crew_results = run_market_intelligence_crew(scores, demand_msg)
    
    # 4. Save to Database
    report = MarketAnalysisReport(
        market_risk_score=scores["marketRiskScore"],
        competitor_threat=scores["competitorThreat"],
        market_opportunity=scores["marketOpportunity"],
        demand_forecast=demand_msg,
        confidence=crew_results["confidence"]
    )
    
    # Set JSON parameters via properties
    report.key_findings = crew_results["keyFindings"]
    report.recommendations = crew_results["recommendations"]
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report

def get_latest_report(db: Session) -> MarketAnalysisReport:
    report = db.query(MarketAnalysisReport).order_by(MarketAnalysisReport.id.desc()).first()
    if not report:
        # If database is empty, run analysis once to seed it
        report = execute_market_analysis(db)
    return report
