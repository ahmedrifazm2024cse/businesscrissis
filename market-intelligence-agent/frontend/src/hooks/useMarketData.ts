import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { marketApi } from '../services/api';

export const useMarketDashboard = () => {
  return useQuery({
    queryKey: ['marketDashboard'],
    queryFn: marketApi.getDashboard,
    refetchInterval: 60000, // Refetch every minute
  });
};

export const useMarketRisk = () => {
  return useQuery({
    queryKey: ['marketRisk'],
    queryFn: marketApi.getRisk,
  });
};

export const useMarketOpportunities = () => {
  return useQuery({
    queryKey: ['marketOpportunities'],
    queryFn: marketApi.getOpportunities,
  });
};

export const useMarketReport = () => {
  return useQuery({
    queryKey: ['marketReport'],
    queryFn: marketApi.getReport,
  });
};

export const useTriggerAnalysis = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: marketApi.triggerAnalysis,
    onSuccess: () => {
      // Invalidate all queries to trigger refresh of dashboard data
      queryClient.invalidateQueries({ queryKey: ['marketDashboard'] });
      queryClient.invalidateQueries({ queryKey: ['marketRisk'] });
      queryClient.invalidateQueries({ queryKey: ['marketOpportunities'] });
      queryClient.invalidateQueries({ queryKey: ['marketReport'] });
    },
  });
};

export const useCrisisAnalyze = () => {
  return useMutation({
    mutationFn: marketApi.crisisAnalyze,
  });
};

