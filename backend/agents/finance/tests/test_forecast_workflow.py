import pytest
from datetime import datetime, timezone
from services.forecasting_engine import forecasting_engine
from services.trend_analyzer import trend_analyzer
import math

def test_data_cleaning():
    raw = [
        {"date": "2024-01-01T00:00:00Z", "sales_quantity": 10},
        {"date": "2024-01-01T00:00:00Z", "sales_quantity": 12}, # Duplicate day, takes latest
        {"date": "2024-01-02T00:00:00Z", "sales_quantity": float('nan')}, # Missing value
        {"date": "2024-01-03T00:00:00Z", "sales_quantity": 11},
        {"date": "2024-01-04T00:00:00Z", "sales_quantity": 9},
        {"date": "2024-01-05T00:00:00Z", "sales_quantity": 10},
        {"date": "2024-01-06T00:00:00Z", "sales_quantity": 11},
        {"date": "2024-01-07T00:00:00Z", "sales_quantity": 10},
        {"date": "2024-01-08T00:00:00Z", "sales_quantity": 12},
        {"date": "2024-01-09T00:00:00Z", "sales_quantity": 1000}, # Extreme anomaly
        {"date": "2024-01-10T00:00:00Z", "sales_quantity": 15},
    ]

    cleaned = forecasting_engine.clean_data(raw)

    assert len(cleaned) == 10
    assert cleaned[0]['value'] == 12.0 # Took latest of Jan 1
    assert cleaned[1]['value'] == 12.0 # Forward fill of NaN
    assert cleaned[8]['value'] < 1000.0 # Anomaly should be smoothed

def test_sma():
    data = [10, 20, 30, 40]
    result = forecasting_engine.simple_moving_average(data, window=3)
    assert math.isclose(result, 30.0)

def test_linear_regression():
    # Perfect linear: y = 10x + 10 -> (0,10), (1,20), (2,30)
    data = [10, 20, 30]
    result = forecasting_engine.linear_regression(data)
    # Next point should be x=3 -> 40
    assert math.isclose(result, 40.0)

def test_exponential_smoothing():
    data = [10, 10, 10]
    result = forecasting_engine.exponential_smoothing(data, alpha=0.5)
    assert math.isclose(result, 10.0)

def test_trend_detection():
    increasing = [10, 12, 14, 20, 25]
    assert trend_analyzer.detect_trend(increasing) in ["Increasing", "Sudden Spike", "Trending Product"]
    
    spike = [10, 11, 10, 12, 50]
    assert trend_analyzer.detect_trend(spike) == "Sudden Spike"
    
    stable = [10, 11, 10, 11, 10]
    assert trend_analyzer.detect_trend(stable) == "Stable"

def test_seasonality_detection():
    # Create weekly pattern
    weekly = [10, 5, 2, 8, 12, 15, 20] * 3
    result = trend_analyzer.detect_seasonality(weekly)
    assert result["seasonality"] == "Weekly"
    assert result["strength"] > 0.5
