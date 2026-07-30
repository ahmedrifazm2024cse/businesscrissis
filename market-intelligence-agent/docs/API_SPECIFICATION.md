# API Specifications: Market Intelligence Agent

Base URL: `http://localhost:8000/api/market`

All endpoints return and accept JSON content type.

---

## Endpoints

### 1. GET `/dashboard`
Fetches a high-level summary of all monitored metrics, datasets, forecasts, and recommendations to render the main overview screen.

- **Response Schema (`DashboardDataResponse`)**:
```json
{
  "marketRiskScore": 82,
  "competitorThreat": "High",
  "marketOpportunity": "Medium",
  "demandForecastSummary": "Demand expected to increase by 12.0% over the next quarter",
  "confidence": 95,
  "competitors": [
    {
      "competitor_id": 1,
      "name": "Competitor Alpha",
      "product_name": "AlphaFlow",
      "feature_set": "Cloud integrations, Real-time sync, Advanced AI insights",
      "market_share": 22.5,
      "pricing_tier": "Premium",
      "sentiment_score": 0.85,
      "last_launch_date": "2026-03-15",
      "status": "Active"
    }
  ],
  "news": [
    {
      "date": "2026-07-28",
      "title": "Customer demand for edge computing architectures rises sharply",
      "summary": "Recent market research highlights that over 60% of enterprise buyers prefer edge deployment capabilities.",
      "source": "ZDNet",
      "sentiment": "Positive",
      "impact_score": 9
    }
  ],
  "pricing": [
    {
      "competitor_name": "Competitor Alpha",
      "plan_name": "Pro",
      "price_monthly": 149.00,
      "features_included": "Advanced CRM, 20 Users, Priority Support"
    }
  ],
  "trends": [
    {
      "quarter": "2026-Q2",
      "trend_name": "Sovereign Cloud Deployments",
      "adoption_rate": 38.1,
      "growth_rate": 30.5,
      "sentiment": "Positive",
      "primary_driver": "Geopolitical data residency concerns"
    }
  ],
  "demandForecast": {
    "historical": [
      {
        "month": "2026-06",
        "sales_units": 2100,
        "nps": 83,
        "lead_conversion_rate": 0.081
      }
    ],
    "forecast": [
      {
        "month": "2026-08",
        "sales_units": 2145,
        "nps": 75,
        "lead_conversion_rate": 0.061
      }
    ],
    "message": "Demand expected to increase by 12.0% over the next quarter"
  },
  "recommendations": [
    "Adjust pricing models",
    "Target sovereign cloud niches"
  ]
}
```

### 2. GET `/report`
Retrieves the latest compiled Markdown-rich report text, narrative analysis, and confidence weights.

- **Response Body**:
```json
{
  "id": 1,
  "timestamp": "2026-07-28T04:10:00Z",
  "agent": "Market Intelligence",
  "marketRiskScore": 82,
  "competitorThreat": "High",
  "marketOpportunity": "Medium",
  "demandForecast": "Demand expected to increase by 12%",
  "confidence": 95,
  "keyFindings": ["...", "..."],
  "recommendations": ["...", "..."]
}
```

### 3. GET `/risk`
Returns a detailed breakdown of risk scoring matrices and raw threat indicators.

- **Response Body**:
```json
{
  "overallScore": 82,
  "competitorThreatScore": 75,
  "economicRiskScore": 55,
  "demandRiskScore": 45,
  "riskFactors": [
    {
      "factor": "Aggressive Competitor Movement",
      "description": "Competitors are highly active with strong sentiment scores.",
      "severity": "High"
    }
  ]
}
```

### 4. GET `/opportunities`
Returns all identified opportunities with adoption vectors and impact scores.

- **Response Body**:
```json
{
  "overallOpportunityScore": 68,
  "opportunities": [
    {
      "opportunity": "Capitalize on Sovereign Cloud Deployments",
      "description": "Targeting high-growth trend (30.5% YoY growth) driven by residency concerns.",
      "impact": "High"
    }
  ]
}
```

### 5. POST `/analyze`
Triggers an immediate live extraction, invokes the CrewAI agent workspace, updates prediction models, and saves the new output run to the database.
- **Response Body**: Conforms exactly to the `/report` layout.
