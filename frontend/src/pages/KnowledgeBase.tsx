import { Typography } from '@mui/material';
import { BookOpen, Search } from 'lucide-react';
import { motion } from 'framer-motion';

export function KnowledgeBase() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="p-6">
      <Typography variant="h4" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
        Corporate Knowledge Base
      </Typography>
      <p className="text-slate-400 mb-8">Centralized repository for Agent intelligence and past playbooks.</p>

      <div className="relative mb-8 max-w-2xl">
        <Search className="absolute left-4 top-3.5 text-slate-500 w-5 h-5" />
        <input 
          type="text" 
          placeholder="Search historical crises, SLA documents, or playbooks..." 
          className="w-full bg-slate-900 border border-slate-800 rounded-xl py-3 pl-12 pr-4 text-white focus:outline-none focus:border-blue-500 transition-colors"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[
          { title: 'Cyber Incident Response Playbook v2.1', category: 'Security' },
          { title: 'Q3 Vendor Redundancy Guidelines', category: 'Supply Chain' },
          { title: 'PR Crisis Communication Templates', category: 'Public Relations' },
          { title: 'Global Compliance Audit 2025', category: 'Legal' }
        ].map((item, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 p-6 rounded-xl hover:border-blue-500/50 cursor-pointer transition-colors group">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">{item.category}</span>
                <h3 className="text-white font-semibold text-lg mt-2 group-hover:text-blue-400 transition-colors">{item.title}</h3>
              </div>
              <BookOpen className="text-slate-600 group-hover:text-blue-400" />
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
