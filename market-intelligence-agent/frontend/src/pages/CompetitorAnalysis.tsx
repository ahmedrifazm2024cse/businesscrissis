import React from 'react';
import { useMarketDashboard } from '../hooks/useMarketData';
import { Loader2 } from 'lucide-react';

export const CompetitorAnalysis: React.FC = () => {
  const { data, isLoading, error } = useMarketDashboard();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
        <p className="text-sm font-semibold text-slate-500">Scanning competitor catalogs...</p>
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
          Competitor Analysis
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Peer feature sets, pricing matrices, and activity indexes.
        </p>
      </div>

      {/* Competitors List Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.competitors.map((comp) => (
          <div 
            key={comp.competitor_id} 
            className="p-6 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
          >
            <div>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-bold text-slate-800 dark:text-white">{comp.name}</h3>
                  <p className="text-xs text-brand-500 font-semibold">{comp.product_name}</p>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-50 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                  Share: {comp.market_share}%
                </span>
              </div>

              <div className="mt-4 space-y-2">
                <p className="text-xs text-slate-400 font-medium">Core Capabilities</p>
                <div className="flex flex-wrap gap-1.5">
                  {comp.feature_set.split(',').map((feat, i) => (
                    <span 
                      key={i} 
                      className="text-[10px] font-semibold px-2 py-0.5 bg-slate-50 text-slate-600 dark:bg-slate-800 dark:text-slate-400 rounded-md"
                    >
                      {feat.trim()}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-850 flex items-center justify-between">
              <span className="text-xs text-slate-400 dark:text-slate-500">
                Launch: {comp.last_launch_date}
              </span>
              <span className={`text-xs font-extrabold px-2.5 py-0.5 rounded uppercase ${
                comp.status === 'Highly Active' 
                  ? 'bg-red-50 text-red-700 dark:bg-red-950/20 dark:text-red-400' 
                  : 'bg-blue-50 text-blue-700 dark:bg-blue-950/20 dark:text-blue-400'
              }`}>
                {comp.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Pricing Table Section */}
      <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-6">Competitor Pricing Matrix</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-100 dark:border-slate-800 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase">
                <th className="pb-3 pl-2">Competitor</th>
                <th className="pb-3">Plan Name</th>
                <th className="pb-3 text-right">Price (Monthly)</th>
                <th className="pb-3 pl-6">Key Features</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 text-sm">
              {data.pricing.map((price, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="py-3.5 pl-2 font-bold text-slate-800 dark:text-slate-200">{price.competitor_name}</td>
                  <td className="py-3.5 text-slate-600 dark:text-slate-400">{price.plan_name}</td>
                  <td className="py-3.5 text-right font-extrabold text-slate-800 dark:text-white">
                    ${price.price_monthly.toFixed(2)}
                  </td>
                  <td className="py-3.5 pl-6 text-xs text-slate-550 dark:text-slate-400 max-w-sm truncate">
                    {price.features_included}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
