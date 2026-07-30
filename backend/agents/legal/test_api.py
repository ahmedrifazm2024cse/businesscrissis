import asyncio
import httpx

async def test():
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            'http://localhost:8000/analyze',
            json={
                'description': 'A customer database with names and emails was exposed publicly for 6 hours.',
                'jurisdiction': 'EU / GDPR'
            }
        )
        d = r.json()
        print(f"Status: {r.status_code}")
        print(f"Report ID: {d['id']}")
        print(f"Risk Level: {d['risk_level']}")
        print(f"Overall Score: {d['compliance_scores']['overall']}")
        print(f"Regulations triggered: {len(d['regulations_triggered'])}")
        print(f"Legal findings: {len(d['legal_findings'])}")
        print(f"Penalties: {len(d['penalty_estimates'])}")
        print(f"Notices: {len(d['disclosure_notices'])}")
        print("TEST PASSED")

asyncio.run(test())
