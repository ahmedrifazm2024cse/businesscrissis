from fastapi import APIRouter
from app.models.domain import BusinessMetric, Incident, Workflow, AgentResult
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/metrics")
async def get_dashboard_metrics():
    # Query MongoDB for real data
    active_crises = await Incident.find({"status": "active"}).count()
    resolved_crises = await Incident.find({"status": "resolved"}).count()
    
    # Calculate average risk score from recent executive decisions
    recent_exec_results = await AgentResult.find({"agent_name": "Executive Decision"}).sort("-created_at").limit(5).to_list()
    overall_risk = 85 # Default if no data
    if recent_exec_results:
        scores = [res.output.get("risk_score", 0) for res in recent_exec_results if "risk_score" in res.output]
        if scores:
            overall_risk = sum(scores) / len(scores)

    # Basic system health logic (could be derived from active agents)
    business_health = max(0, 100 - (active_crises * 10))
    
    return {
        "overallRisk": round(overall_risk),
        "businessHealth": business_health,
        "aiConfidence": 94,
        "activeCrises": active_crises,
        "resolvedCrises": resolved_crises,
        "systemUptime": 99.9,
        "threatLevel": "Critical" if active_crises > 0 else "Normal",
        "totalAgents": 13
    }

@router.get("/charts/revenue")
async def get_revenue_chart_data():
    # Attempt to derive revenue data from Financial Risk agent results
    fin_results = await AgentResult.find({"agent_name": "Financial Risk"}).sort("created_at").to_list()
    
    # Base starting revenue
    base_actual = 4000
    base_projected = 4200
    
    chart_data = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    for i in range(min(7, len(fin_results) + 1)):
        if i == 0:
            chart_data.append({"name": months[i], "actual": base_actual, "projected": base_projected})
        else:
            res = fin_results[i-1]
            # Try to extract numbers from string like "-$4.2M" or "$1.2M"
            loss_str = res.output.get("revenue_loss", "0").replace("$", "").replace("M", "").replace("-", "")
            try:
                loss = float(loss_str) * 1000 # Just an arbitrary scale for the chart
            except:
                loss = 500
            
            base_actual = max(0, base_actual - loss)
            base_projected = base_projected + 100 # projected normally grows
            chart_data.append({"name": months[i], "actual": int(base_actual), "projected": int(base_projected)})

    # If no results, provide some empty fallback so the chart doesn't break
    if len(chart_data) == 1:
        chart_data.extend([
            {"name": "Feb", "actual": 4100, "projected": 4300},
            {"name": "Mar", "actual": 4200, "projected": 4400},
        ])

    return chart_data

@router.get("/charts/sentiment")
async def get_sentiment_chart_data():
    cr_results = await AgentResult.find({"agent_name": "Customer Reputation"}).sort("created_at").to_list()
    
    chart_data = []
    # Start with a base sentiment before crises
    chart_data.append({"name": "Baseline", "score": 85})
    
    for i, res in enumerate(cr_results):
        score = res.output.get("sentiment_score", 50)
        chart_data.append({"name": f"Event {i+1}", "score": score})
        
    if len(chart_data) == 1:
         chart_data.extend([
            {"name": "Event 1", "score": 85},
            {"name": "Event 2", "score": 85},
        ])
        
    return chart_data

@router.get("/command-center")
async def get_command_center_data():
    # Fetch latest incident
    incident = await Incident.find().sort("-created_at").first_or_none()
    if not incident:
        return {"status": "no_active_crisis"}
        
    workflow = await Workflow.find({"incident_id": str(incident.id)}).first_or_none()
    
    results = []
    if workflow:
        results = await AgentResult.find({"workflow_id": str(workflow.id)}).sort("created_at").to_list()
        
    # Aggregate data
    severity = 94 if incident.severity == "Critical" else (75 if incident.severity == "High" else 50)
    financial_impact = "-$0"
    recommendations = []
    timeline = []
    
    # Base timeline event
    timeline.append({
        "time": incident.created_at.strftime("%I:%M %p"),
        "text": f"Incident reported: {incident.title}"
    })
    
    # Process agent results
    for res in results:
        # Timeline
        timeline.append({
            "time": res.created_at.strftime("%I:%M %p"),
            "text": f"{res.agent_name} completed analysis."
        })
        
        if res.agent_name == "Financial Risk":
            financial_impact = res.output.get("revenue_loss", "-$1.2M")
            
        if res.agent_name == "Strategy":
            action_plan = res.output.get("action_plan", [])
            for action in action_plan:
                recommendations.append({
                    "title": action,
                    "conf": "85%",
                    "impact": "High",
                    "action": "Review"
                })
                
        if res.agent_name == "Executive Decision":
            final_decision = res.output.get("final_decision", "")
            if final_decision:
                timeline.append({
                    "time": res.created_at.strftime("%I:%M %p"),
                    "text": f"Executive Decision: {final_decision[:50]}..."
                })
                
    # Reverse timeline for newest first
    timeline.reverse()
    
    # If no recommendations yet, provide placeholders based on incident
    if not recommendations:
        recommendations = [
            {"title": "Pending Strategy Agent Analysis", "conf": "--", "impact": "--", "action": "Wait"}
        ]
        
    # Calculate time active
    time_diff = datetime.utcnow() - incident.created_at
    hours, remainder = divmod(time_diff.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    time_active = f"{int(hours):02d}:{int(minutes):02d}:00"
        
    return {
        "status": "success",
        "crisis": {
            "title": incident.title,
            "description": incident.description,
            "severityScore": severity,
            "financialImpact": financial_impact,
            "affectedDepts": min(len(results), 8) or 1,
            "timeActive": time_active
        },
        "recommendations": recommendations,
        "timeline": timeline[:10]
    }

