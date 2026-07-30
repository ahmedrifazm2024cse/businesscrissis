import asyncio
import os
import sys
import uuid
import random
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.database import init_db
from models.final_intelligence import BusinessImpactAssessment

def utc_now():
    return datetime.now(timezone.utc)

async def main():
    settings.MONGODB_URI = 'mongodb://localhost:27017/abcc_db'
    await init_db()
    
    print('Seeding BusinessImpactAssessment historical records for Executive Dashboard chart...')
    
    # Do not delete existing, just append historical ones so the chart has a timeline
    assessments = []
    
    # We want 20 records spanning the last 20 hours
    for i in range(20, 0, -1):
        bia = BusinessImpactAssessment(
            assessment_id=str(uuid.uuid4()),
            revenue_loss=random.uniform(10000, 1000000),
            profit_loss=random.uniform(5000, 500000),
            inventory_loss=random.uniform(2000, 100000),
            recovery_cost=random.uniform(10000, 500000),
            recovery_time_days=random.uniform(2, 30),
            business_impact_score=random.uniform(30, 90),
            business_risk_score=random.uniform(20, 80),
            business_health_score=random.uniform(40, 95),
            crisis_severity=random.choice(["Low", "Medium", "High"]),
            executive_summary="Historical assessment.",
            root_cause="Historical data",
            business_explanation="N/A",
            risk_explanation="N/A",
            recovery_plan="N/A",
            business_recommendation="N/A",
            priority="Medium",
            expected_business_outcome="N/A",
            confidence=random.uniform(0.7, 0.99),
            generated_at=utc_now() - timedelta(hours=i)
        )
        assessments.append(bia)
        
    await BusinessImpactAssessment.insert_many(assessments)
    print(f'Inserted {len(assessments)} records.')

if __name__ == '__main__':
    asyncio.run(main())
