import httpx
import asyncio
import json
import random

COMMANDER_API = "http://localhost:8000/api/crisis/report"

SCENARIOS = {
    "1_cyber": {
        "name": "Cyber Attack",
        "query": "A massive ransomware attack has encrypted our core customer databases in the EU region. The attackers are demanding $5M in Bitcoin within 24 hours.",
    },
    "2_supply": {
        "name": "Supply Chain Failure",
        "query": "A major hurricane has completely wiped out our primary semiconductor manufacturing plant in Taiwan, halting 40% of our global supply.",
    },
    "3_customer": {
        "name": "Customer Reputation Crisis",
        "query": "A viral TikTok video showing our flagship product catching fire has reached 50 million views, causing massive brand damage.",
    },
    "4_financial": {
        "name": "Financial Loss",
        "query": "Our Q3 earnings missed estimates by 30%, causing a 15% drop in stock price. Investors are panicking and demanding immediate restructuring.",
    },
    "5_legal": {
        "name": "Legal Compliance Violation",
        "query": "The EU Commission has officially charged us with violating GDPR, threatening a fine of up to 4% of our global annual revenue.",
    },
    "6_market": {
        "name": "Market Collapse",
        "query": "A major competitor just released a revolutionary AI product that completely makes our primary software suite obsolete. Our churn rate spiked by 500% today.",
    },
    "7_multi_crisis": {
        "name": "Combined Multi-Crisis Event",
        "query": "A coordinated cyber attack breached our payment systems (Cyber), leaking 1M credit cards (Legal). The PR backlash is massive (Customer), and our stock is plunging (Finance).",
    }
}

async def trigger_crisis(scenario_id: str):
    print(f"🚀 Injecting Scenario: {SCENARIOS[scenario_id]['name']}")
    
    payload = {
        "query": SCENARIOS[scenario_id]["query"],
        "priority": "CRITICAL"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(COMMANDER_API, json=payload, timeout=60.0)
            print(f"✅ Commander Accepted Payload: {response.json()}")
        except Exception as e:
            print(f"❌ Failed to inject payload: {e}")

if __name__ == "__main__":
    print("Agentverse Demo Simulation Engine")
    print("Available Scenarios:")
    for k, v in SCENARIOS.items():
        print(f"- {k}: {v['name']}")
    
    choice = input("\nEnter scenario ID to launch: ")
    if choice in SCENARIOS:
        asyncio.run(trigger_crisis(choice))
    else:
        print("Invalid choice.")
