"""
Data Loader
===========
Central access layer for all market data.
Priority order:
  1. Live API  (realtime_fetcher)
  2. CSV seed  (sample-data/)
  3. Inline fallback
"""
import os
import pandas as pd
from functools import lru_cache
from typing import Optional
from app.config.settings import settings

# ── File helpers ─────────────────────────────────────────────────────────────

def _csv(filename: str) -> Optional[str]:
    """Return path to a sample-data CSV, or None."""
    candidates = [
        os.path.join(settings.SAMPLE_DATA_DIR, filename),
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sample-data', filename),
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None

def _read_csv(filename: str) -> pd.DataFrame:
    path = _csv(filename)
    if path:
        return pd.read_csv(path)
    return pd.DataFrame()

# ── Loaders ──────────────────────────────────────────────────────────────────

def load_competitors() -> pd.DataFrame:
    """Live stock prices for tracked SaaS competitors (Yahoo Finance)."""
    try:
        from app.services.realtime_fetcher import fetch_all_realtime_competitors
        rows = fetch_all_realtime_competitors()
        if rows:
            return pd.DataFrame(rows)
    except Exception as e:
        print(f'[loader] competitors live fetch failed: {e}')
    df = _read_csv('competitors.csv')
    if not df.empty:
        return df
    return pd.DataFrame([{
        'competitor_id': 1, 'name': 'Salesforce (CRM)', 'product_name': 'Customer 360',
        'feature_set': 'Enterprise CRM', 'market_share': 22.5, 'pricing_tier': 'Enterprise',
        'sentiment_score': 0.75, 'last_launch_date': '2026-01-01', 'status': 'Active',
    }])


def load_market_news() -> pd.DataFrame:
    """Live news from TechCrunch, Reuters, BBC, CNBC, FT RSS feeds."""
    try:
        from app.services.realtime_fetcher import fetch_live_news
        rows = fetch_live_news()
        if rows:
            return pd.DataFrame(rows)
    except Exception as e:
        print(f'[loader] news live fetch failed: {e}')
    df = _read_csv('market_news.csv')
    if not df.empty:
        return df
    return pd.DataFrame([{
        'date': '2026-07-28', 'title': 'Market Update',
        'summary': 'Live feed unavailable.', 'source': 'System',
        'sentiment': 'Neutral', 'impact_score': 5,
    }])


def load_pricing() -> pd.DataFrame:
    """Pricing stays static (no live API available)."""
    df = _read_csv('pricing.csv')
    if not df.empty:
        return df
    return pd.DataFrame([
        {'competitor_name': 'Salesforce', 'plan_name': 'Starter Suite', 'price_monthly': 25.0,   'features_included': 'CRM, Email'},
        {'competitor_name': 'Salesforce', 'plan_name': 'Pro Suite',     'price_monthly': 100.0,  'features_included': 'CRM, Analytics, AI'},
        {'competitor_name': 'HubSpot',    'plan_name': 'Starter',       'price_monthly': 20.0,   'features_included': 'Marketing Hub'},
        {'competitor_name': 'HubSpot',    'plan_name': 'Professional',  'price_monthly': 890.0,  'features_included': 'Full Suite'},
        {'competitor_name': 'Microsoft',  'plan_name': 'Dynamics 365',  'price_monthly': 65.0,   'features_included': 'ERP + CRM'},
        {'competitor_name': 'ServiceNow', 'plan_name': 'Enterprise',    'price_monthly': 200.0,  'features_included': 'ITSM + HR + Finance'},
    ])


def load_industry_trends() -> pd.DataFrame:
    """Live sector ETF performance as industry trend proxy."""
    try:
        from app.services.realtime_fetcher import fetch_industry_trends
        rows = fetch_industry_trends()
        if rows:
            return pd.DataFrame(rows)
    except Exception as e:
        print(f'[loader] trends live fetch failed: {e}')
    df = _read_csv('industry_trends.csv')
    if not df.empty:
        return df
    return pd.DataFrame([
        {'quarter': '2026-Q3', 'trend_name': 'AI & Machine Learning', 'adoption_rate': 58.0,
         'growth_rate': 24.5, 'sentiment': 'Positive', 'primary_driver': 'Enterprise AI'},
    ])


def load_demand() -> pd.DataFrame:
    """S&P 500 monthly closes as demand health proxy."""
    try:
        from app.services.realtime_fetcher import fetch_demand_data
        rows = fetch_demand_data()
        if rows:
            return pd.DataFrame(rows)
    except Exception as e:
        print(f'[loader] demand live fetch failed: {e}')
    df = _read_csv('demand.csv')
    if not df.empty:
        return df
    from datetime import date
    today = date.today()
    return pd.DataFrame([
        {'month': f'{today.year}-{i:02d}', 'sales_units': 1000 + i * 40,
         'nps': 72, 'lead_conversion_rate': 0.06}
        for i in range(1, 13)
    ])


def load_economic_data() -> pd.DataFrame:
    """Live FRED data: Fed rate, CPI, unemployment, GDP, consumer confidence."""
    try:
        from app.services.realtime_fetcher import fetch_live_economic_row
        row = fetch_live_economic_row()
        if row:
            return pd.DataFrame([row])
    except Exception as e:
        print(f'[loader] economic live fetch failed: {e}')
    df = _read_csv('economic_data.csv')
    if not df.empty:
        return df
    from datetime import date
    return pd.DataFrame([{
        'month': date.today().strftime('%Y-%m'),
        'gdp_growth_rate': 2.4, 'inflation_rate': 3.2,
        'interest_rate': 5.33, 'consumer_confidence': 68.0,
        'market_index_change': 0.01,
    }])
