import axios from 'axios';
import { DashboardData, RiskDetails, OpportunityDetails, ReportDetails, CrisisAnalysisRequest, CrisisAnalysisResponse } from '../types/market';

const API_BASE_URL = 'http://localhost:8000/api/market';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const marketApi = {
  getDashboard: async (): Promise<DashboardData> => {
    const response = await api.get<DashboardData>('/dashboard');
    return response.data;
  },
  
  getRisk: async (): Promise<RiskDetails> => {
    const response = await api.get<RiskDetails>('/risk');
    return response.data;
  },
  
  getOpportunities: async (): Promise<OpportunityDetails> => {
    const response = await api.get<OpportunityDetails>('/opportunities');
    return response.data;
  },
  
  getReport: async (): Promise<ReportDetails> => {
    const response = await api.get<ReportDetails>('/report');
    return response.data;
  },
  
  triggerAnalysis: async (): Promise<ReportDetails> => {
    const response = await api.post<ReportDetails>('/analyze');
    return response.data;
  },

  crisisAnalyze: async (data: CrisisAnalysisRequest): Promise<CrisisAnalysisResponse> => {
    const response = await api.post<CrisisAnalysisResponse>('/crisis-analyze', data);
    return response.data;
  },
};
