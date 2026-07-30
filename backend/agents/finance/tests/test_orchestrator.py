import pytest
from services.business_impact import business_impact_analyzer

def test_business_impact_calculation():
    # Setup mock telemetry
    mock_telemetry = {
        "shortages": [
            {"revenue_impact_estimate": 10000.0, "risk_score": 80.0, "classification": "High Risk"}
        ],
        "suppliers": [
            {"classification": "Critical", "risk_score": 95.0}
        ],
        "shipments": [
            {"delay_probability": 0.8}
        ]
    }
    
    # Calculate
    scores = business_impact_analyzer.calculate_scores(mock_telemetry)
    
    # Verify exact loss aggregations
    # Shortage revenue = 10000. Supplier critical = +50000 -> 60000
    assert scores["revenue_loss"] == 60000.0
    
    # Shortage profit = 10000 * 0.3 = 3000
    assert scores["profit_loss"] == 3000.0
    
    # Shipment delay > 0.7 = 10000
    assert scores["inventory_loss"] == 10000.0
    
    # Recovery cost: shortage=5000, supplier=20000 -> 25000
    assert scores["recovery_cost"] == 25000.0
    
    # Recovery time: supplier=14, shipment=5 -> max = 14
    assert scores["recovery_time_days"] == 14.0
    
    # Risk Score: (80 + 95) / 2 = 87.5
    assert scores["business_risk_score"] == 87.5
    
    # Impact Score: min((60000/100000)*50 + 87.5*0.5, 100)
    # (0.6)*50 + 43.75 = 30 + 43.75 = 73.75
    assert scores["business_impact_score"] == 73.75
    
    # Severity > 60 -> High
    assert scores["crisis_severity"] == "High"

def test_emergency_override():
    mock_telemetry = {
        "shortages": [
            {"revenue_impact_estimate": 5000.0, "risk_score": 50.0, "classification": "Emergency"}
        ],
        "suppliers": [],
        "shipments": []
    }
    
    scores = business_impact_analyzer.calculate_scores(mock_telemetry)
    
    # Overrides to critical
    assert scores["crisis_severity"] == "Critical"
    assert scores["business_impact_score"] >= 90.0
