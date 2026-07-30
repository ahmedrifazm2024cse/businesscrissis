import { useEffect, useState } from 'react';
import { Download, FileText, CheckCircle2, AlertOctagon } from 'lucide-react';
import { RiskBadge } from '../components/common/RiskBadge';
import { CommanderAPI } from '../services/commanderAPI';
import { motion } from 'framer-motion';
import { Typography } from '@mui/material';

export function ExecutiveDashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // In a real application, we would listen to WebSocket events
  // or poll the current active workflow. For now, we will poll
  // the latest workflow if it exists.
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        // We assume the workflow_id is stored in localStorage or passed via Context
        const activeWorkflowId = localStorage.getItem('active_workflow_id');
        if (activeWorkflowId) {
          const status = await CommanderAPI.getWorkflowStatus(activeWorkflowId);
          setData(status);
        }
      } catch (err) {
        console.error("Failed to fetch workflow status", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="p-8 text-center animate-pulse">Loading Executive Insights...</div>;
  }

  if (!data) {
    return (
      <div className="p-8 text-center text-slate-500">
        No active crisis workflow detected. Awaiting crisis submission.
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex justify-between items-center">
        <div>
          <Typography variant="h4" sx={{ fontWeight: 800, background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Executive Dashboard
          </Typography>
          <p className="text-slate-500 text-sm mt-1">Live Multi-Agent Synthesis</p>
        </div>
        <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-5 py-2.5 rounded-xl font-medium flex items-center gap-2 shadow-lg hover:shadow-indigo-500/30 transition-all">
          <Download className="w-4 h-4" />
          Export Intelligence Brief
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Executive Summary */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div 
            whileHover={{ scale: 1.01 }}
            className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-xl relative overflow-hidden"
          >
            {/* Ambient glow effect */}
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-blue-500/20 blur-3xl rounded-full" />
            
            <div className="flex items-center justify-between mb-4 relative z-10">
              <h3 className="text-xl font-bold flex items-center gap-3 text-slate-800 dark:text-white">
                <FileText className="w-6 h-6 text-blue-500" />
                Commander Summary
              </h3>
              <RiskBadge level={data.severity || "CRITICAL"} />
            </div>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-lg relative z-10">
              {data.decision || data.crisis_description || "Agents are currently synthesizing information..."}
            </p>
          </motion.div>

          {/* Impact Matrix */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { title: 'Customer Reputation', val: data.customer_analysis, color: 'from-pink-500 to-rose-500', icon: '👥' },
              { title: 'Market Intelligence', val: data.market_analysis, color: 'from-violet-500 to-purple-500', icon: '📈' },
              { title: 'Financial Risk', val: data.finance_analysis, color: 'from-emerald-500 to-teal-500', icon: '💰' },
              { title: 'Supply Chain', val: data.supply_analysis, color: 'from-amber-500 to-orange-500', icon: '🚢' },
              { title: 'Cyber Security', val: data.cyber_analysis, color: 'from-blue-500 to-cyan-500', icon: '🔒' },
              { title: 'Legal Compliance', val: data.legal_analysis, color: 'from-slate-500 to-gray-500', icon: '⚖️' },
            ].map((impact, idx) => (
              <motion.div 
                key={idx} 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.1 }}
                whileHover={{ y: -5, boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)' }}
                className={`bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm transition-all duration-300 ${!impact.val ? 'opacity-60' : 'ring-1 ring-slate-800'}`}
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{impact.icon}</span>
                    <h4 className="font-semibold text-slate-800 dark:text-slate-100">{impact.title}</h4>
                  </div>
                  {impact.val && (
                    <span className="flex h-3 w-3 relative">
                      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full bg-gradient-to-r ${impact.color} opacity-75`}></span>
                      <span className={`relative inline-flex rounded-full h-3 w-3 bg-gradient-to-r ${impact.color}`}></span>
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-500 leading-snug">{impact.val || "Awaiting intelligence..."}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Action Plan */}
        <div className="space-y-6">
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden text-white"
          >
            <div className="absolute inset-0 bg-gradient-to-b from-blue-900/20 to-transparent pointer-events-none" />
            
            <h3 className="text-lg font-bold flex items-center gap-2 mb-6">
              <AlertOctagon className="w-5 h-5 text-orange-400" />
              Live Workflow Status
            </h3>
            
            <div className="space-y-6 relative">
              {/* Vertical line indicator */}
              <div className="absolute left-2.5 top-2 bottom-2 w-0.5 bg-slate-800" />
              
              <div className="flex items-start gap-4 relative">
                <div className="relative z-10 mt-1">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center ${data.status === 'completed' ? 'bg-green-500' : 'bg-blue-500 ring-4 ring-blue-500/30 animate-pulse'}`}>
                    {data.status === 'completed' && <CheckCircle2 className="w-3 h-3 text-white" />}
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-200 capitalize">
                    {data.status?.replace(/_/g, ' ') || 'Initializing...'}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1">
                    {data.status === 'completed' ? 'All agents have reported.' : 'Commander AI is coordinating agents in real-time.'}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
