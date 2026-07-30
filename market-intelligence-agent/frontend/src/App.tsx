import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { CompetitorAnalysis } from './pages/CompetitorAnalysis';
import { MarketTrends } from './pages/MarketTrends';
import { DemandForecast } from './pages/DemandForecast';
import { RiskAnalysis } from './pages/RiskAnalysis';
import { Reports } from './pages/Reports';
import { CrisisSimulation } from './pages/CrisisSimulation';

// Create TanStack Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/competitors" element={<CompetitorAnalysis />} />
            <Route path="/trends" element={<MarketTrends />} />
            <Route path="/forecast" element={<DemandForecast />} />
            <Route path="/risk" element={<RiskAnalysis />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/crisis" element={<CrisisSimulation />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
};

export default App;
