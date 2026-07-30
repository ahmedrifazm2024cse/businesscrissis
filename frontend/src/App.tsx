import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { AIAssistantPanel } from './components/layout/AIAssistantPanel';

function DashboardLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-900 font-sans text-slate-900 dark:text-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 relative">
        <Navbar />
        <main className="flex-1 overflow-auto p-6 relative">
          <Outlet />
        </main>
        <AIAssistantPanel />
      </div>
    </div>
  );
}

import { HomeDashboard } from './pages/HomeDashboard';
import { ExecutiveDashboard } from './pages/ExecutiveDashboard';
import { WorkflowMonitor } from './pages/WorkflowMonitor';
import { AgentMonitor } from './pages/AgentMonitor';
import PresentationMode from './pages/PresentationMode';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { Reports } from './pages/Reports';
import { Notifications } from './pages/Notifications';
import { Analytics } from './pages/Analytics';
import { Settings } from './pages/Settings';
import { KnowledgeBase } from './pages/KnowledgeBase';
import { MemoryMonitor } from './pages/MemoryMonitor';

function App() {
  return (
    <WebSocketProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<div>Login Page</div>} />
          
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<HomeDashboard />} />
            <Route path="/executive" element={<ExecutiveDashboard />} />
            <Route path="/system/workflow" element={<WorkflowMonitor />} />
            <Route path="/system/monitor" element={<AgentMonitor />} />
            <Route path="/presentation" element={<PresentationMode />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/knowledge" element={<KnowledgeBase />} />
            <Route path="/system/memory" element={<MemoryMonitor />} />
            <Route path="/agent/:agentName" element={<AgentMonitor />} />
            <Route path="/system/health" element={<AgentMonitor />} />
            <Route path="*" element={<div>Page under construction.</div>} />
          </Route>
        </Routes>
      </Router>
    </WebSocketProvider>
  );
}

export default App;
