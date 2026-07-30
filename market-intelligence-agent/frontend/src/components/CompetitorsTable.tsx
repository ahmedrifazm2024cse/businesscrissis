import React from 'react';
import { CompetitorData } from '../types/market';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface CompetitorsTableProps {
  competitors: CompetitorData[];
}

export const CompetitorsTable: React.FC<CompetitorsTableProps> = ({ competitors }) => {
  const getStatusBadge = (status: string) => {
    if (status === 'Highly Active')
      return 'bg-red-500/10 text-red-400 border border-red-500/20';
    if (status === 'Active')
      return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
    return 'bg-slate-700/50 text-slate-400 border border-slate-700/50';
  };

  const getSentimentIcon = (score: number) => {
    if (score >= 0.7) return <TrendingUp className="w-3.5 h-3.5 text-red-400" />;
    if (score >= 0.4) return <Minus className="w-3.5 h-3.5 text-amber-400" />;
    return <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />;
  };

  return (
    <div className="rounded-2xl border border-slate-800/60 overflow-hidden h-full"
         style={{ background: 'rgba(10,18,35,0.85)' }}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800/60 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-300">Competitor Intelligence Matrix</h3>
        <span className="font-terminal text-[10px] text-slate-600">{competitors.length} tracked</span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-800/40">
              {['Competitor', 'Product', 'Market Share', 'Threat', 'Status'].map(h => (
                <th key={h} className="px-5 py-3 text-left text-[10px] font-bold text-slate-600 uppercase tracking-widest font-terminal">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/30">
            {competitors.map((c, i) => (
              <tr key={i} className="hover:bg-slate-800/20 transition-colors group">
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-brand-600/30 to-violet-600/30 border border-brand-500/20 flex items-center justify-center text-[10px] font-bold text-brand-400">
                      {c.name.charAt(0)}
                    </div>
                    <span className="font-semibold text-slate-200 group-hover:text-white transition-colors">{c.name}</span>
                  </div>
                </td>
                <td className="px-5 py-3.5 text-slate-500 text-xs">{c.product_name}</td>
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-2.5">
                    <div className="w-20 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-brand-500 to-violet-500 transition-all duration-700"
                        style={{ width: `${Math.min(100, c.market_share * 4)}%` }}
                      />
                    </div>
                    <span className="text-xs font-semibold text-slate-300 font-terminal">{c.market_share}%</span>
                  </div>
                </td>
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-1.5">
                    {getSentimentIcon(c.sentiment_score)}
                    <span className="text-xs font-terminal text-slate-400">{(c.sentiment_score * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td className="px-5 py-3.5">
                  <span className={`text-[10px] font-bold px-2.5 py-1 rounded-lg uppercase tracking-wider font-terminal ${getStatusBadge(c.status)}`}>
                    {c.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
