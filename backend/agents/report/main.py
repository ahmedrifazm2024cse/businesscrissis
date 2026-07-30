import sys
import os
import httpx
import datetime
from fastapi import FastAPI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from packages.agent_adapter.wrapper import AgentverseWrapper

app = FastAPI(title="Report Generator Agent")

AGENT_NAME = "report_generator"
PORT = 8017
CAPABILITIES = ["Executive Summary Generation", "PDF Formatting", "Final Audit Logging"]
MEMORY_URL = os.getenv("MEMORY_URL", "http://localhost:8102/api/memory")

async def report_logic(payload):
    crisis_id = payload.crisis_id
    
    # Read Shared Memory
    agent_outputs = {}
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{MEMORY_URL}/{crisis_id}")
            if resp.status_code == 200:
                agent_outputs = resp.json().get("agent_outputs", {})
    except Exception as e:
        print(f"Failed to read memory: {e}")
        
    report_md = f"# Executive Crisis Report: {crisis_id}\n"
    report_md += f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report_md += f"**Severity:** {payload.severity}\n\n"
    
    if "executive_decision" in agent_outputs:
        dec = agent_outputs["executive_decision"]
        report_md += "## Executive Strategy\n"
        for rec in dec.get("recommendations", []):
            report_md += f"- {rec}\n"
            
    report_md += "\n## Departmental Impact\n"
    for agent, data in agent_outputs.items():
        if agent != "executive_decision":
            report_md += f"### {agent.replace('_', ' ').title()}\n"
            for finding in data.get("findings", [])[:3]:
                report_md += f"- {finding}\n"
            for rec in data.get("recommendations", [])[:2]:
                report_md += f"  - Action: {rec}\n"
                
    return (
        ["Generated final PDF-ready Markdown report."],
        [report_md],
        1.0, # Confidence
        0 # Risk Score
    )

try:
    AgentverseWrapper(app).register(
        agent_name=AGENT_NAME,
        port=PORT,
        capabilities=CAPABILITIES,
        dependencies=[],
        legacy_handler=report_logic
    )
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
