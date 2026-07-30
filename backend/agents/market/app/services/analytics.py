from typing import Dict, List, Any
import pandas as pd
from app.utils.data_loader import (
    load_competitors, load_market_news, load_pricing,
    load_industry_trends, load_demand, load_economic_data
)
from app.services.forecasting import forecast_demand

def calculate_market_scores() -> Dict[str, Any]:
    # Load all inputs
    competitors_df = load_competitors()
    news_df = load_market_news()
    trends_df = load_industry_trends()
    economic_df = load_economic_data()
    demand_df = load_demand()
    
    # 1. Competitor Threat Assessment
    # Formula: Average of (Sentiment score inverted * 100) + weight on Highly Active competitors
    active_count = len(competitors_df[competitors_df['status'] == 'Highly Active'])
    total_competitors = len(competitors_df)
    active_ratio = active_count / total_competitors if total_competitors > 0 else 0
    
    # Higher competitor sentiment score means they are performing better, representing a higher threat to us
    avg_comp_sentiment = competitors_df['sentiment_score'].mean() if not competitors_df.empty else 0.5
    competitor_threat_score = int((avg_comp_sentiment * 70) + (active_ratio * 30))
    competitor_threat_score = min(100, max(0, competitor_threat_score))
    
    if competitor_threat_score > 70:
        competitor_threat = "High"
    elif competitor_threat_score > 40:
        competitor_threat = "Medium"
    else:
        competitor_threat = "Low"
        
    # 2. Economic Risk Calculation
    # Based on inflation_rate and interest_rate from economic_data.csv (latest row)
    economic_risk_score = 50 # Default middle
    if not economic_df.empty:
        latest_econ = economic_df.sort_values(by="month").iloc[-1]
        inflation = float(latest_econ.get("inflation_rate", 2.5))
        interest = float(latest_econ.get("interest_rate", 4.0))
        consumer_conf = float(latest_econ.get("consumer_confidence", 100))
        
        # Risk factors: High inflation (>3%) + High interest (>5%) + Low consumer confidence (<100)
        risk_from_inflation = min(35, max(0, int((inflation - 1.5) * 15)))
        risk_from_interest = min(35, max(0, int((interest - 2.5) * 10)))
        risk_from_confidence = min(30, max(0, int((110 - consumer_conf) * 2)))
        
        economic_risk_score = int(risk_from_inflation + risk_from_interest + risk_from_confidence)
        economic_risk_score = min(100, max(0, economic_risk_score))
        
    # 3. Demand Risk Calculation
    # Based on forecast trend
    forecast_results = forecast_demand()
    pct_change = forecast_results["pct_change"]
    
    # Positive growth decreases demand risk; negative growth increases demand risk
    # Default demand risk base is 50
    demand_risk_score = int(50 - (pct_change * 2))
    demand_risk_score = min(100, max(0, demand_risk_score))
    
    # 4. Overall Market Risk Score
    # Weighted average of components
    market_risk_score = int(
        (competitor_threat_score * 0.4) + 
        (economic_risk_score * 0.3) + 
        (demand_risk_score * 0.3)
    )
    market_risk_score = min(100, max(0, market_risk_score))
    
    # 5. Opportunity Score Calculation
    # Based on positive sentiment trends and market growth rates
    opportunity_score = 50
    if not trends_df.empty:
        positive_trends = trends_df[trends_df['sentiment'] == 'Positive']
        avg_growth = positive_trends['growth_rate'].mean() if not positive_trends.empty else 10
        avg_adoption = positive_trends['adoption_rate'].mean() if not positive_trends.empty else 30
        
        opportunity_score = int((avg_growth * 2) + (avg_adoption * 0.5))
        opportunity_score = min(100, max(0, opportunity_score))
        
    if opportunity_score > 70:
        market_opportunity = "High"
    elif opportunity_score > 40:
        market_opportunity = "Medium"
    else:
        market_opportunity = "Low"
        
    # Build list of specific risk factors
    risk_factors = []
    if competitor_threat == "High":
        risk_factors.append({
            "factor": "Aggressive Competitor Movement",
            "description": f"Competitors are highly active (active ratio: {active_ratio:.0%}) with strong sentiment scores.",
            "severity": "High"
        })
    if economic_risk_score > 60:
        risk_factors.append({
            "factor": "Unfavorable Macroeconomic Indicators",
            "description": "Rising inflation and elevated interest rates are compressing business margin opportunities.",
            "severity": "Medium"
        })
    if demand_risk_score > 60:
        risk_factors.append({
            "factor": "Softening Near-Term Demand",
            "description": "Historical sales and lead conversion indicators suggest cooling market demand.",
            "severity": "Medium"
        })
    if not risk_factors:
        risk_factors.append({
            "factor": "Standard Market Dynamics",
            "description": "Normal competitor movements and minor price competition detected.",
            "severity": "Low"
        })

    # Build opportunity list
    opportunities = []
    if not trends_df.empty:
        top_growth_trends = trends_df.sort_values(by="growth_rate", ascending=False).head(2)
        for _, row in top_growth_trends.iterrows():
            opportunities.append({
                "opportunity": f"Capitalize on {row['trend_name']}",
                "description": f"Targeting high-growth trend ({row['growth_rate']}% YoY growth) driven by {row['primary_driver']}.",
                "impact": "High" if row['growth_rate'] > 20 else "Medium"
            })
            
    return {
        "marketRiskScore": market_risk_score,
        "competitorThreatScore": competitor_threat_score,
        "competitorThreat": competitor_threat,
        "economicRiskScore": economic_risk_score,
        "demandRiskScore": demand_risk_score,
        "marketOpportunity": market_opportunity,
        "opportunityScore": opportunity_score,
        "riskFactors": risk_factors,
        "opportunities": opportunities
    }
