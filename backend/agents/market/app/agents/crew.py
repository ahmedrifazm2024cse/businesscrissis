import os
import json
import time
from collections import deque
from typing import Dict, Any, List
from app.config.settings import settings
from app.utils.data_loader import (
    load_competitors, load_market_news, load_pricing,
    load_industry_trends, load_demand, load_economic_data
)

# ---------------------------------------------------------------------------
# Global in-memory agent log queue (thread-safe deque, max 200 entries)
# ---------------------------------------------------------------------------
_agent_log_queue: deque = deque(maxlen=200)
_agent_is_running: bool = False

def push_log(source: str, message: str, log_type: str = "thought") -> None:
    """Append a timestamped log entry to the shared queue."""
    entry = {
        "ts": time.time(),
        "source": source,
        "message": str(message),
        "type": log_type,   # thought | action | result | system
    }
    _agent_log_queue.append(entry)

def get_logs() -> List[Dict[str, Any]]:
    """Return all current log entries as a list."""
    return list(_agent_log_queue)

def clear_logs() -> None:
    """Clear the log queue before a new run."""
    _agent_log_queue.clear()

def is_agent_running() -> bool:
    return _agent_is_running

def run_market_intelligence_crew(scores: Dict[str, Any], demand_forecast_msg: str) -> Dict[str, Any]:
    """
    Orchestrates the CrewAI agents. Falls back to a deterministic semantic generator
    if no OpenAI API Key is provided in the configuration.
    """
    global _agent_is_running
    _agent_is_running = True
    clear_logs()
    push_log("System", "Market Intelligence Crew initializing...", "system")
    
    api_key = settings.OPENAI_API_KEY
    
    if not api_key:
        push_log("System", "No OpenAI key detected — activating rule-based intelligence engine.", "system")
        result = generate_mock_crew_output(scores, demand_forecast_msg)
        _agent_is_running = False
        return result
        
    # Set environment variables for CrewAI / LangChain
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_MODEL_NAME"] = settings.OPENAI_MODEL_NAME

    try:
        from crewai import Agent, Task, Crew, Process
        from langchain_openai import ChatOpenAI
        
        # Load datasets for context
        competitors = load_competitors().to_json(orient="records")
        news = load_market_news().to_json(orient="records")
        trends = load_industry_trends().to_json(orient="records")
        
        # Initialize LLM
        llm = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, temperature=0.7)
        
        # Step callback to forward agent thoughts to SSE queue
        def _step_callback(step_output):
            try:
                push_log("Agent", str(step_output), "thought")
            except Exception:
                pass

        # Define Agents
        researcher = Agent(
            role="Senior Market Intelligence Analyst",
            goal="Analyze external industry trends, competitor activities, and news to extract risk areas and strategic opportunities.",
            backstory="You are an expert market analyst with 15+ years of experience scanning industry bulletins, news feeds, competitor price catalogs, and technological shifts.",
            verbose=True,
            llm=llm,
            step_callback=_step_callback
        )
        
        assessor = Agent(
            role="Corporate Risk Assessment Officer",
            goal="Compute business crisis vulnerability metrics, compile strategic executive findings, and generate immediate recommended actions.",
            backstory="You are a seasoned crisis manager who specializes in translating market risks, high competitor pressure, and economic fluctuations into clear defense recommendations.",
            verbose=True,
            llm=llm,
            step_callback=_step_callback
        )
        
        # Define Tasks
        task1 = Task(
            description=f"""
            Analyze the following market news and trends data:
            News: {news}
            Trends: {trends}
            Competitors: {competitors}
            
            Identify the top 3 critical risks (competitor moves, regulation changes, or market shifts) and top 2 opportunities.
            """,
            expected_output="A structured list containing details on key risk factors and opportunities.",
            agent=researcher
        )
        
        task2 = Task(
            description=f"""
            Given the analysis from the researcher, the calculated scores:
            - Market Risk Score: {scores['marketRiskScore']}
            - Competitor Threat: {scores['competitorThreat']}
            - Opportunity Score: {scores['opportunityScore']}
            - Demand Forecast Summary: {demand_forecast_msg}
            
            Generate a JSON response conforming EXACTLY to the following structure:
            {{
                "keyFindings": [
                    "Point 1 highlighting critical competitor risk or market shift",
                    "Point 2 highlighting regulatory or economic pressure details",
                    "Point 3 highlighting demand or technology adoption trends"
                ],
                "recommendations": [
                    "Actionable executive directive 1 (e.g. adjust pricing, release edge capability)",
                    "Actionable executive directive 2 (e.g. enhance secure storage, target high growth sector)",
                    "Actionable executive directive 3 (e.g. monitor supply chain disruptions)"
                ]
            }}
            Ensure it is output as valid JSON only, without markdown wrapping.
            """,
            expected_output="JSON representation of key findings and recommendations.",
            agent=assessor
        )
        
        # Run Crew
        crew = Crew(
            agents=[researcher, assessor],
            tasks=[task1, task2],
            process=Process.sequential
        )
        
        push_log("System", "Launching CrewAI sequential process...", "system")
        result_str = crew.kickoff()
        push_log("System", "Crew run complete. Parsing output...", "system")
        
        # Clean markdown formatting if present
        if hasattr(result_str, 'raw'):
            result_str = result_str.raw
        result_str = str(result_str)
        if "```json" in result_str:
            result_str = result_str.split("```json")[1].split("```")[0].strip()
        elif "```" in result_str:
            result_str = result_str.split("```")[1].split("```")[0].strip()
            
        data = json.loads(result_str)
        _agent_is_running = False
        push_log("System", "Analysis complete. Results saved to database.", "result")
        return {
            "keyFindings": data.get("keyFindings", []),
            "recommendations": data.get("recommendations", []),
            "confidence": 95
        }
        
    except Exception as e:
        push_log("System", f"CrewAI error: {e}. Activating fallback engine.", "system")
        _agent_is_running = False
        print(f"Error running CrewAI: {e}. Falling back to rule-based generation.")
        return generate_mock_crew_output(scores, demand_forecast_msg)

def generate_mock_crew_output(scores: Dict[str, Any], demand_forecast_msg: str) -> Dict[str, Any]:
    """
    A smart rule-based generator that uses actual loaded data to generate realistic,
    context-aware findings and recommendations when OpenAI API is disabled.
    """
    push_log("Market Analyst", "Loading competitor dataset for analysis...", "thought")
    competitors_df = load_competitors()
    push_log("Market Analyst", "Scanning market news feed for high-impact events...", "thought")
    news_df = load_market_news()
    push_log("Market Analyst", "Analyzing industry growth trends and adoption curves...", "thought")
    trends_df = load_industry_trends()
    
    # 1. Base key findings based on data
    key_findings = []
    
    # Competitor Finding
    if not competitors_df.empty:
        top_comp = competitors_df.sort_values(by="market_share", ascending=False).iloc[0]
        key_findings.append(
            f"Competitor '{top_comp['name']}' dominates with a {top_comp['market_share']}% market share and is actively positioning their '{top_comp['product_name']}' solution."
        )
    else:
        key_findings.append("High competitive pressure detected from multiple premium tier SaaS offerings.")
        
    # News Finding
    if not news_df.empty:
        top_news = news_df.sort_values(by="impact_score", ascending=False).iloc[0]
        key_findings.append(
            f"Regulatory & Industry News: '{top_news['title']}' (Impact: {top_news['impact_score']}/10) poses immediate business implications."
        )
    else:
        key_findings.append("New compliance mandates and data privacy guidelines create localized market friction.")
        
    # Trend & Demand Finding
    if not trends_df.empty:
        top_trend = trends_df.sort_values(by="growth_rate", ascending=False).iloc[0]
        key_findings.append(
            f"Emerging Tech: {top_trend['trend_name']} is growing at {top_trend['growth_rate']}% quarterly, driven primarily by '{top_trend['primary_driver']}'."
        )
    else:
        key_findings.append(f"Market Forecast indicator: {demand_forecast_msg}.")
        
    # 2. Recommendations based on scores
    push_log("Risk Officer", f"Evaluating scores — Risk: {scores['marketRiskScore']}, Threat: {scores['competitorThreat']}, Opportunity: {scores.get('opportunityScore', 'N/A')}", "thought")
    recommendations = []
    
    # Competitor threat recommendations
    if scores["competitorThreat"] == "High":
        recommendations.append("Execute defensive pricing: introduce value-focused service tiers to combat Competitor Alpha's recent enterprise launches.")
    else:
        recommendations.append("Leverage pricing advantages: capture mid-market customers with aggressive bundled plan configurations.")
        
    # Opportunity recommendations
    if scores["opportunityScore"] > 50:
        recommendations.append("Direct R&D funding toward high-adoption trends (such as Edge Computing and Zero-Trust cloud integrations).")
    else:
        recommendations.append("Invest in core CRM/BI features to bridge capability gaps relative to primary competitors.")
        
    # Risk/Security recommendations
    recommendations.append("Hedge supply-chain risks: diversify hosting and software component vendors to protect against shipment disruptions.")
    recommendations.append("Implement proactive customer retention campaigns to support the predicted quarterly demand fluctuations.")

    push_log("Risk Officer", "Compiling executive directives and strategic action plan...", "thought")
    push_log("System", "Rule-based analysis complete. Findings ready.", "result")
    _agent_is_running = False
    return {
        "keyFindings": key_findings,
        "recommendations": recommendations,
        "confidence": 88
    }

def run_crisis_intelligence_crew(crisis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes crisis telemetry payload. Conforms exactly to the required output format.
    Falls back to a structured engine if no OpenAI key is configured.
    """
    push_log("Crisis Commander", f"Receiving crisis briefing for: {crisis_data.get('company_name', 'Unknown')} ({crisis_data.get('crisis_type', 'Unknown')})", "system")
    api_key = settings.OPENAI_API_KEY
    
    if not api_key:
        push_log("Crisis Commander", "Running rule-based crisis simulation engine...", "system")
        return generate_mock_crisis_output(crisis_data)
        
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_MODEL_NAME"] = settings.OPENAI_MODEL_NAME

    try:
        from crewai import Agent, Task, Crew, Process
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, temperature=0.5)
        
        def _crisis_step_callback(step_output):
            try:
                push_log("Crisis Commander", str(step_output), "thought")
            except Exception:
                pass

        officer = Agent(
            role="Sovereign Crisis Intelligence Commander",
            goal="Analyze external business environment risks during a crisis and provide strategic market positioning advice.",
            backstory="You are an elite corporate war-room officer specialized in diagnosing market vulnerabilities and competitor reactions during live crises.",
            verbose=True,
            llm=llm,
            step_callback=_crisis_step_callback
        )
        
        task = Task(
            description=f"""
            Analyze the following crisis data:
            Company: {crisis_data.get('company_name')}
            Industry: {crisis_data.get('industry')}
            Crisis Type: {crisis_data.get('crisis_type')}
            Description: {crisis_data.get('crisis_description')}
            Market Trend: {crisis_data.get('current_market_trend')}
            Competitors: {crisis_data.get('competitor_information')}
            Customer Demand: {crisis_data.get('customer_demand')}
            Location: {crisis_data.get('location')}
            
            Return a JSON object matching this schema exactly:
            {{
              "market_summary": "High-level summary of the market situation",
              "market_impact": "How this crisis affects the company's market position",
              "competitor_analysis": "Predicted competitor reactions",
              "customer_demand_prediction": "Estimated customer demand changes",
              "business_opportunities": [
                "Opportunity 1",
                "Opportunity 2"
              ],
              "market_risk_score": "Score from 1 to 10 (as a string)",
              "recommendations": [
                "Strategic recommendation 1",
                "Strategic recommendation 2",
                "Strategic recommendation 3"
              ]
            }}
            Return ONLY raw JSON, with no markdown code blocks or additional text.
            """,
            expected_output="Valid raw JSON representing the crisis analysis.",
            agent=officer
        )
        
        crew = Crew(
            agents=[officer],
            tasks=[task],
            process=Process.sequential
        )
        
        push_log("Crisis Commander", "Launching crisis assessment crew...", "system")
        result_str = crew.kickoff()
        push_log("Crisis Commander", "Crisis assessment complete. Parsing results...", "result")
        
        if hasattr(result_str, 'raw'):
            result_str = result_str.raw
        result_str = str(result_str)
        if "```json" in result_str:
            result_str = result_str.split("```json")[1].split("```")[0].strip()
        elif "```" in result_str:
            result_str = result_str.split("```")[1].split("```")[0].strip()
            
        return json.loads(result_str)
        
    except Exception as e:
        push_log("System", f"Crisis crew error: {e}. Using fallback.", "system")
        print(f"Error running Crisis Crew: {e}. Falling back.")
        return generate_mock_crisis_output(crisis_data)

def generate_mock_crisis_output(crisis_data: Dict[str, Any]) -> Dict[str, Any]:
    c_name = crisis_data.get("company_name", "the Company")
    industry = crisis_data.get("industry", "the sector")
    c_type = crisis_data.get("crisis_type", "Operational disruption")
    desc = crisis_data.get("crisis_description", "unexpected events")
    trend = crisis_data.get("current_market_trend", "stagnation")
    comps = crisis_data.get("competitor_information", "other active peers")
    demand = crisis_data.get("customer_demand", "unstable levels")
    loc = crisis_data.get("location", "global markets")
    
    # Simple risk score logic
    risk_score = "7"
    if "severe" in desc.lower() or "critical" in desc.lower() or "shutdown" in desc.lower():
        risk_score = "9"
    elif "minor" in desc.lower() or "brief" in desc.lower():
        risk_score = "4"

    return {
        "market_summary": f"{c_name} is navigating a {c_type} crisis within the {industry} industry in {loc}, amidst a general trend of '{trend}'.",
        "market_impact": f"The crisis '{desc}' creates near-term vulnerability, potentially eroding brand equity and customer confidence in {loc}.",
        "competitor_analysis": f"Competitors ('{comps}') are expected to capitalize on this disruption by launching target retention discounts and aggressive customer acquisition campaigns.",
        "customer_demand_prediction": f"Overall customer demand, originally described as '{demand}', is predicted to shift toward highly-flexible alternative service agreements.",
        "business_opportunities": [
          f"Pivot branding to showcase security and operational resilience relative to competitors.",
          f"Leverage current market trends ('{trend}') to capture compliance-minded customer segments."
        ],
        "market_risk_score": risk_score,
        "recommendations": [
          "Establish an immediate client outreach initiative to transparently explain mitigation steps.",
          "Hedge retention risks by offering standard plan credits or value-tier additions.",
          "Monitor competitor marketing campaigns closely to respond with matching service guarantees."
        ]
    }

