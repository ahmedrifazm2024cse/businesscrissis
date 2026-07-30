export interface CompetitorData {
  competitor_id: number;
  name: string;
  product_name: string;
  feature_set: string;
  market_share: number;
  pricing_tier: string;
  sentiment_score: number;
  last_launch_date: string;
  status: string;
}

export interface NewsItem {
  date: string;
  title: string;
  summary: string;
  source: string;
  sentiment: string;
  impact_score: number;
}

export interface PricingCompare {
  competitor_name: string;
  plan_name: string;
  price_monthly: number;
  features_included: string;
}

export interface TrendItem {
  quarter: string;
  trend_name: string;
  adoption_rate: number;
  growth_rate: number;
  sentiment: string;
  primary_driver: string;
}

export interface DemandPoint {
  month: string;
  sales_units: number;
  nps: number;
  lead_conversion_rate: number;
}

export interface DemandForecast {
  historical: DemandPoint[];
  forecast: DemandPoint[];
  message: string;
}

export interface DashboardData {
  marketRiskScore: number;
  competitorThreat: string;
  marketOpportunity: string;
  demandForecastSummary: string;
  confidence: number;
  competitors: CompetitorData[];
  news: NewsItem[];
  pricing: PricingCompare[];
  trends: TrendItem[];
  demandForecast: DemandForecast;
  recommendations: string[];
}

export interface RiskFactor {
  factor: string;
  description: string;
  severity: string;
}

export interface RiskDetails {
  overallScore: number;
  competitorThreatScore: number;
  economicRiskScore: number;
  demandRiskScore: number;
  riskFactors: RiskFactor[];
}

export interface OpportunityItem {
  opportunity: string;
  description: string;
  impact: string;
}

export interface OpportunityDetails {
  overallOpportunityScore: number;
  opportunities: OpportunityItem[];
}

export interface ReportDetails {
  id: number;
  timestamp: string;
  agent: string;
  marketRiskScore: number;
  competitorThreat: string;
  marketOpportunity: string;
  demandForecast: string;
  confidence: number;
  keyFindings: string[];
  recommendations: string[];
}

export interface CrisisAnalysisRequest {
  company_name: string;
  industry: string;
  crisis_type: string;
  crisis_description: string;
  current_market_trend: string;
  competitor_information: string;
  customer_demand: string;
  location: string;
}

export interface CrisisAnalysisResponse {
  market_summary: string;
  market_impact: string;
  competitor_analysis: string;
  customer_demand_prediction: string;
  business_opportunities: string[];
  market_risk_score: string;
  recommendations: string[];
}

