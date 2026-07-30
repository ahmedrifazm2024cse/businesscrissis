// The single point of contact for the entire frontend
// Never calls agents directly.

const BASE_URL = "/api"; // Proxied by Vite or NGINX to Commander API Gateway

export const CommanderAPI = {
  getSystemHealth: async () => {
    const res = await fetch(`${BASE_URL}/commander/health`);
    return res.json();
  },
  triggerCrisis: async (description: string, severity: string) => {
    const res = await fetch(`${BASE_URL}/commander/crisis`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description, severity })
    });
    return res.json();
  },
  getWorkflowStatus: async (workflow_id: string) => {
    const res = await fetch(`${BASE_URL}/commander/status/${workflow_id}`);
    return res.json();
  },
  getSharedMemory: async (crisis_id: string) => {
    const res = await fetch(`${BASE_URL}/commander/status/${crisis_id}`);
    return res.json();
  },
  getOnlineAgents: async () => {
    const res = await fetch(`${BASE_URL}/commander/agents`);
    return res.json();
  }
};
