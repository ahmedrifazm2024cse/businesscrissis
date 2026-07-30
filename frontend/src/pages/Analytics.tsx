import { Typography } from '@mui/material';
import { BarChart3, TrendingUp, Users } from 'lucide-react';
import { motion } from 'framer-motion';

export function Analytics() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="p-6">
      <Typography variant="h4" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
        Global Analytics
      </Typography>
      <p className="text-slate-400 mb-8">Enterprise-wide agent performance and resolution metrics.</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {[
          { label: 'Total Crises Resolved', value: '142', icon: <BarChart3 /> },
          { label: 'Avg Resolution Time', value: '1.2s', icon: <TrendingUp /> },
          { label: 'Active Agents', value: '13', icon: <Users /> }
        ].map((stat, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
            <div className="text-blue-400 mb-4">{stat.icon}</div>
            <Typography variant="h3" sx={{ color: 'white', fontWeight: 'bold' }}>{stat.value}</Typography>
            <p className="text-slate-400 mt-2">{stat.label}</p>
          </div>
        ))}
      </div>
      
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl h-64 flex items-center justify-center">
        <p className="text-slate-500">Analytics visualization integration pending.</p>
      </div>
    </motion.div>
  );
}
