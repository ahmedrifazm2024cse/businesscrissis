import React from 'react';
import { useMarketDashboard } from '../hooks/useMarketData';
import { Loader2, Compass } from 'lucide-react';

export const MarketTrends: React.FC = () => {
  const { data, isLoading, error } = useMarketDashboard();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
        <p className="text-sm font-semibold text-slate-500">Mapping industry shifts...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 border border-red-200 dark:border-red-900/30 bg-red-50 dark:bg-red-950/20 rounded-2xl">
        <h3 className="font-bold text-red-800 dark:text-red-400">Connection Failed</h3>
        <p className="text-sm text-red-700 dark:text-red-400/80 mt-1">
          Could not communicate with the Market Intelligence Agent API.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-800 dark:text-white">
          Market Trends & Adoption
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Technology integration rates, segment growth trajectories, and adoption catalysts.
        </p>
      </div>

      {/* Grid List of Trends */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {data.trends.map((trend, idx) => (
          <div 
            key={idx} 
            className="p-6 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
          >
            <div>
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-brand-500 bg-brand-50 px-2 py-0.5 rounded dark:bg-brand-950/30 dark:text-brand-400">
                    {trend.quarter}
                  </span>
                  <h3 className="text-lg font-bold text-slate-800 dark:text-white mt-2">
                    {trend.trend_name}
                  </h3>
                </div>
                <span className={`text-xs font-bold px-2 py-0.5 rounded uppercase border ${
                  trend.sentiment === 'Positive'
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-250 dark:bg-emerald-950/20 dark:text-emerald-400 dark:border-emerald-900/30'
                    : 'bg-slate-50 text-slate-650 border-slate-200 dark:bg-slate-900/20'
                }`}>
                  {trend.sentiment}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mt-6">
                <div className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-100 dark:border-slate-850">
                  <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase">Adoption Rate</span>
                  <p className="text-xl font-bold text-slate-700 dark:text-slate-100 mt-1">{trend.adoption_rate}%</p>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-100 dark:border-slate-850">
                  <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase">Quarter Growth</span>
                  <p className="text-xl font-bold text-slate-700 dark:text-slate-100 mt-1">+{trend.growth_rate}%</p>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-850 flex items-center gap-3">
              <Compass className="w-4 h-4 text-slate-400 shrink-0" />
              <p className="text-xs font-medium text-slate-550 dark:text-slate-400">
                <strong className="text-slate-750 dark:text-slate-350">Driver:</strong> {trend.primary_driver}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
