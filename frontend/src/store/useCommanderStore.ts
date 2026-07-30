import { create } from 'zustand';
import { api } from '../services/api';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: string;
  latency: string;
  cpu: string;
  mem: string;
  task: string;
  output?: any;
}

interface Task {
  id: string;
  description: string;
}

interface SystemHealth {
  status: string;
  commander: string;
  agents_registered: number;
}

interface CommanderStore {
  agents: Agent[];
  activeTasks: Task[];
  health: SystemHealth | null;
  metrics: any;
  revenueChart: any[];
  sentimentChart: any[];
  commandCenter: any;
  wsConnected: boolean;
  
  // Actions
  fetchAgents: () => Promise<void>;
  fetchActiveTasks: () => Promise<void>;
  fetchHealth: () => Promise<void>;
  fetchDashboardData: () => Promise<void>;
  fetchCommandCenter: () => Promise<void>;
  connectWebSocket: () => void;
  declareCrisis: (description: string) => Promise<void>;
}

export const useCommanderStore = create<CommanderStore>((set) => ({
  agents: [],
  activeTasks: [],
  health: null,
  metrics: null,
  revenueChart: [],
  sentimentChart: [],
  commandCenter: null,
  wsConnected: false,

  fetchAgents: async () => {
    try {
      const res = await api.get('/agents');
      set({ agents: res.data.agents || [] });
    } catch (e) {
      console.error('Failed to fetch agents', e);
    }
  },

  fetchActiveTasks: async () => {
    try {
      const res = await api.get('/workflows/active');
      set({ activeTasks: res.data.tasks || [] });
    } catch (e) {
      console.error('Failed to fetch tasks', e);
    }
  },

  fetchHealth: async () => {
    try {
      const res = await api.get('/health');
      set({ health: res.data });
    } catch (e) {
      console.error('Failed to fetch health', e);
    }
  },

  fetchDashboardData: async () => {
    try {
      const [metricsRes, revenueRes, sentimentRes] = await Promise.all([
        api.get('/dashboard/metrics'),
        api.get('/dashboard/charts/revenue'),
        api.get('/dashboard/charts/sentiment')
      ]);
      set({ 
        metrics: metricsRes.data,
        revenueChart: revenueRes.data,
        sentimentChart: sentimentRes.data
      });
    } catch (e) {
      console.error('Failed to fetch dashboard data', e);
    }
  },

  fetchCommandCenter: async () => {
    try {
      const res = await api.get('/dashboard/command-center');
      if (res.data.status === "success") {
        set({ commandCenter: res.data });
      }
    } catch (e) {
      console.error('Failed to fetch command center data', e);
    }
  },

  declareCrisis: async (description: string) => {
    try {
      await api.post('/workflow/start', { title: "Generated Crisis", description, severity: "Critical" });
      // Fetch tasks immediately after declaring
      useCommanderStore.getState().fetchActiveTasks();
    } catch (e) {
      console.error('Failed to declare crisis', e);
    }
  },

  connectWebSocket: () => {
    const wsUrl = `ws://localhost:8000/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      set({ wsConnected: true });
      console.log('Commander WebSocket Connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Commander WS Message:', data);
        
        if (data.event === 'agent_running') {
          set((state) => ({
            agents: state.agents.map(a => a.name === data.agent ? { ...a, status: 'running' } : a)
          }));
        } else if (data.event === 'agent_completed') {
          set((state) => ({
            agents: state.agents.map(a => a.name === data.agent ? { ...a, status: 'completed', output: data.output } : a)
          }));
        } else if (data.event === 'workflow_started') {
          // Reset all agents to idle when a new workflow starts
          set((state) => ({
            agents: state.agents.map(a => ({ ...a, status: 'idle' }))
          }));
        }
      } catch (e) {
        console.error('Failed to parse WS message', e);
      }
    };

    ws.onclose = () => {
      set({ wsConnected: false });
      console.log('Commander WebSocket Disconnected');
      // Simple reconnect logic
      setTimeout(() => {
        useCommanderStore.getState().connectWebSocket();
      }, 5000);
    };

    ws.onerror = (err) => {
      console.error('WebSocket error', err);
      ws.close();
    };
  }
}));
