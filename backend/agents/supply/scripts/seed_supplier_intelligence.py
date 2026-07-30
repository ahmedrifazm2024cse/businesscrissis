import asyncio
import os
import sys
import random
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.database import init_db
from models.domain import Supplier
from models.supplier_intelligence import SupplierProfile, SupplierRisk

def utc_now():
    return datetime.now(timezone.utc)

async def main():
    settings.MONGODB_URI = 'mongodb://localhost:27017/abcc_db'
    await init_db()
    
    print('Seeding Supplier Profiles and Risks...')
    suppliers = await Supplier.find_all().to_list()
    if not suppliers:
        print('No suppliers found in domain models. Run seed_database.py first.')
        return
        
    print('Deleting old Supplier Profiles and Risks...')
    await SupplierProfile.delete_all()
    await SupplierRisk.delete_all()
        
    profiles = []
    risks = []
    
    categories = ['Electronics', 'Raw Materials', 'Packaging', 'Logistics', 'Hardware', 'Software']
    products = ['Microchips', 'Steel', 'Plastic', 'Circuit Boards', 'Batteries', 'Sensors']
    
    for s in suppliers:
        profile = SupplierProfile(
            supplier_id=s.supplier_id,
            name=s.name,
            categories=random.sample(categories, k=random.randint(1, 3)),
            products_supplied=random.sample(products, k=random.randint(1, 4)),
            location=f"Industrial Zone, {s.country}",
            country=s.country,
            is_primary=random.choice([True, False]),
            capacity_per_month=random.randint(10000, 500000),
            contract_status=random.choice(["Active", "Active", "Pending", "Expired"]),
            contact_email=f"contact@{s.name.replace(' ', '').lower()}.com",
            preferred_status=random.choice([True, False])
        )
        profiles.append(profile)
        
        # Base risk from domain model risk_level
        base_risk = 50.0
        risk_cat = s.risk_level
        if risk_cat == "Low": base_risk = random.uniform(10, 30)
        elif risk_cat == "Medium": base_risk = random.uniform(30, 60)
        elif risk_cat == "High": base_risk = random.uniform(60, 85)
        elif risk_cat == "Critical": base_risk = random.uniform(85, 100)
        
        risk = SupplierRisk(
            supplier_id=s.supplier_id,
            financial_risk=random.uniform(0, 100),
            delivery_risk=base_risk,
            country_risk=random.uniform(10, 90),
            political_risk=random.uniform(10, 80),
            natural_disaster_risk=random.uniform(5, 75),
            weather_impact=random.uniform(0, 60),
            currency_risk=random.uniform(10, 85),
            single_source_dependency=random.uniform(0, 100),
            capacity_risk=random.uniform(20, 90),
            quality_risk=random.uniform(5, 50),
            compliance_risk=random.uniform(0, 40),
            contract_expiration_risk=random.uniform(0, 100),
            overall_risk_score=base_risk,
            risk_category=risk_cat
        )
        risks.append(risk)
        
    print(f'Inserting {len(profiles)} supplier profiles and {len(risks)} risks...')
    await SupplierProfile.insert_many(profiles)
    await SupplierRisk.insert_many(risks)
    
    print('Supplier intelligence seeding complete.')

if __name__ == '__main__':
    asyncio.run(main())
