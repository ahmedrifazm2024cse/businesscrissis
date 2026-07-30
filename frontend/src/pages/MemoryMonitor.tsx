import { Typography } from '@mui/material';
import { Database, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

export function MemoryMonitor() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="p-6">
      <Typography variant="h4" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
        Global Shared Memory
      </Typography>
      <p className="text-slate-400 mb-8">Live data streams from the inter-agent state cache.</p>

      <div className="grid gap-6 max-w-4xl">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="flex items-center gap-3 mb-4">
            <Database className="text-blue-400 w-6 h-6" />
            <h3 className="text-xl font-semibold text-white">Active Workflow State</h3>
          </div>
          <div className="bg-black/50 p-4 rounded-lg font-mono text-sm text-green-400 overflow-x-auto">
            {`{
  "workflow_id": "live-demo-1234",
  "status": "executing_executive_decision",
  "execution_plan": ["cyber", "finance", "legal"],
  "cyber_analysis": "Critical breach in partition 7.",
  "finance_analysis": "Projected $1.2M exposure.",
  "legal_analysis": "SLA breach imminent within 24h."
}`}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
