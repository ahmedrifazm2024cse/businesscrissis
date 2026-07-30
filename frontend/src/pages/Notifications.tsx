import { Typography } from '@mui/material';
import { Bell, AlertTriangle, Info } from 'lucide-react';
import { motion } from 'framer-motion';

export function Notifications() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="p-6">
      <Typography variant="h4" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
        System Notifications
      </Typography>
      <p className="text-slate-400 mb-8">Real-time alerts from the Event Bus.</p>

      <div className="space-y-4">
        {[
          { type: 'alert', msg: 'Cyber Agent detected unauthorized access attempt.', time: '2 mins ago' },
          { type: 'info', msg: 'Workflow execution completed successfully.', time: '1 hour ago' },
          { type: 'info', msg: 'Database backup completed.', time: '3 hours ago' }
        ].map((notif, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex items-start gap-4">
            <div className={`p-2 rounded-lg ${notif.type === 'alert' ? 'bg-orange-500/20 text-orange-400' : 'bg-blue-500/20 text-blue-400'}`}>
              {notif.type === 'alert' ? <AlertTriangle className="w-5 h-5" /> : <Info className="w-5 h-5" />}
            </div>
            <div>
              <p className="text-white font-medium">{notif.msg}</p>
              <p className="text-slate-500 text-sm mt-1">{notif.time}</p>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
