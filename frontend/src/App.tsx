import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { LandingPage } from './pages/LandingPage';
import { ExecutiveDashboard } from './pages/dashboard/ExecutiveDashboard';
import { MultiAgentWorkspace } from './pages/agents/MultiAgentWorkspace';
import { WorkflowVisualization } from './pages/dashboard/WorkflowVisualization';
import { CrisisCommandCenter } from './pages/dashboard/CrisisCommandCenter';
import { Analytics } from './pages/analytics/Analytics';
import { Reports } from './pages/reports/Reports';
import { AIChat } from './pages/chat/AIChat';
import { Notifications } from './pages/notifications/Notifications';
import { Settings } from './pages/settings/Settings';
import { AdminPanel } from './pages/admin/AdminPanel';
import { useEffect } from 'react';
import { useCommanderStore } from './store/useCommanderStore';

function App() {
  const { connectWebSocket } = useCommanderStore();

  useEffect(() => {
    // Initiate WebSocket connection on app load
    connectWebSocket();
  }, [connectWebSocket]);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        
        <Route path="/dashboard" element={<MainLayout />}>
          <Route index element={<ExecutiveDashboard />} />
          <Route path="agents" element={<MultiAgentWorkspace />} />
          <Route path="crisis" element={<CrisisCommandCenter />} />
          <Route path="workflow" element={<WorkflowVisualization />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="reports" element={<Reports />} />
          <Route path="chat" element={<AIChat />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="settings" element={<Settings />} />
          <Route path="admin" element={<AdminPanel />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
