import { Box, Typography } from '@mui/material';
import { FileText, Download, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';

export function Reports() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="p-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <Typography variant="h4" sx={{ fontWeight: 800, color: 'white' }}>
            Executive Reports
          </Typography>
          <p className="text-slate-400 mt-1">Generated intelligence briefings and workflow audit logs.</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2">
          <Download className="w-4 h-4" /> Export All
        </button>
      </div>

      <div className="grid gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 p-6 rounded-xl flex items-center justify-between hover:border-slate-700 transition-colors">
            <div className="flex items-center gap-4">
              <div className="bg-blue-900/30 p-3 rounded-lg text-blue-400">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-white font-semibold text-lg">Crisis Resolution Report #{1024 + i}</h3>
                <div className="flex items-center gap-2 text-sm text-slate-500 mt-1">
                  <Calendar className="w-4 h-4" /> 
                  {new Date().toLocaleDateString()}
                </div>
              </div>
            </div>
            <button className="text-blue-400 hover:text-blue-300 font-medium text-sm">View Report</button>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
