import { Typography, Switch, FormControlLabel } from '@mui/material';
import { Settings as SettingsIcon, Database, Shield } from 'lucide-react';
import { motion } from 'framer-motion';

export function Settings() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="p-6">
      <Typography variant="h4" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
        Platform Settings
      </Typography>
      <p className="text-slate-400 mb-8">Configure your Enterprise AI parameters.</p>

      <div className="space-y-6 max-w-2xl">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="flex items-center gap-3 mb-6">
            <SettingsIcon className="text-blue-400" />
            <h3 className="text-xl font-semibold text-white">General Preferences</h3>
          </div>
          <div className="space-y-4">
            <FormControlLabel control={<Switch defaultChecked color="primary" />} label="Enable Auto-Execution of High-Confidence Decisions" sx={{ color: 'white' }} />
            <FormControlLabel control={<Switch defaultChecked color="primary" />} label="Real-time Event Bus Streaming" sx={{ color: 'white' }} />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="flex items-center gap-3 mb-6">
            <Shield className="text-orange-400" />
            <h3 className="text-xl font-semibold text-white">Security & API Keys</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-2">LLM Provider API Key</label>
              <input type="password" value="************************" readOnly className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none" />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
