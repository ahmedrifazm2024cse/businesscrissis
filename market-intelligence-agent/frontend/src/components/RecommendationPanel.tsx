import React from 'react';
import { ShieldCheck, TrendingUp, AlertTriangle, Zap } from 'lucide-react';

interface RecommendationPanelProps {
  recommendations: string[];
}

const ICON_CONFIG = [
  { icon: ShieldCheck, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  { icon: TrendingUp,  color: 'text-brand-400',   bg: 'bg-brand-500/10 border-brand-500/20' },
  { icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
  { icon: Zap,         color: 'text-violet-400',  bg: 'bg-violet-500/10 border-violet-500/20' },
];

export const RecommendationPanel: React.FC<RecommendationPanelProps> = ({ recommendations }) => {
  return (
    <div className="flex flex-col rounded-2xl border border-slate-800/60 overflow-hidden h-full"
         style={{ background: 'rgba(10,18,35,0.85)' }}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800/60 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-300">Executive Directives</h3>
        <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full uppercase tracking-widest">
          Agent Validated
        </span>
      </div>

      {/* Recommendations */}
      <div className="flex-1 p-5 space-y-3">
        {recommendations.map((rec, index) => {
          const cfg = ICON_CONFIG[index % ICON_CONFIG.length];
          const Icon = cfg.icon;
          return (
            <div
              key={index}
              className="flex items-start gap-3.5 p-4 rounded-xl border border-slate-800/40 bg-slate-900/30 hover:bg-slate-800/30 hover:border-slate-700/50 transition-all duration-150 group"
            >
              <div className={`p-2 rounded-lg border shrink-0 mt-0.5 ${cfg.bg} transition-transform duration-150 group-hover:scale-105`}>
                <Icon className={`w-4 h-4 ${cfg.color}`} />
              </div>
              <div>
                <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-1 font-terminal">
                  Directive MI-{100 + index}
                </p>
                <p className="text-sm text-slate-300 leading-relaxed">{rec}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="px-6 py-3 border-t border-slate-800/60 text-center">
        <p className="text-[11px] text-slate-600">Route directives to the executive crisis dashboard</p>
      </div>
    </div>
  );
};
