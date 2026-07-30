import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from typing import Dict, List, Any
from app.utils.data_loader import load_demand

def forecast_demand() -> Dict[str, Any]:
    df = load_demand()
    
    # Ensure sorted by month
    df = df.sort_values(by="month").reset_index(drop=True)
    
    # We will use indices as feature X for regression
    df['time_index'] = np.arange(len(df))
    
    X = df[['time_index']].values
    y = df['sales_units'].values
    
    # Train simple linear regression
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next 6 months
    last_index = len(df) - 1
    next_indices = np.arange(last_index + 1, last_index + 7).reshape(-1, 1)
    predictions = model.predict(next_indices)
    
    # Parse last month to calculate next month strings
    last_month_str = df['month'].iloc[-1]
    year, month = map(int, last_month_str.split('-'))
    
    forecast_points = []
    current_year = year
    current_month = month
    
    # Assume NPS and lead conversion remains around average
    avg_nps = int(df['nps'].mean())
    avg_conversion = float(df['lead_conversion_rate'].mean())
    
    for pred in predictions:
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
        
        month_str = f"{current_year}-{current_month:02d}"
        forecast_points.append({
            "month": month_str,
            "sales_units": int(max(0, round(pred))),
            "nps": avg_nps,
            "lead_conversion_rate": round(avg_conversion, 4)
        })
        
    # Calculate percentage change between average of last 3 months and first 3 forecasted months
    last_3_avg = df['sales_units'].iloc[-3:].mean()
    next_3_avg = np.mean(predictions[:3])
    pct_change = ((next_3_avg - last_3_avg) / last_3_avg) * 100
    
    direction = "increase" if pct_change >= 0 else "decrease"
    message = f"Demand expected to {direction} by {abs(pct_change):.1f}% over the next quarter"
    
    # Convert historical to dictionary list
    historical_points = df[["month", "sales_units", "nps", "lead_conversion_rate"]].to_dict(orient="records")
    
    return {
        "historical": historical_points,
        "forecast": forecast_points,
        "message": message,
        "pct_change": round(pct_change, 2)
    }
