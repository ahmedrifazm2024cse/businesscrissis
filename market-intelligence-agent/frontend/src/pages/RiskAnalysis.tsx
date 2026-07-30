import React from 'react';
import { useMarketRisk } from '../hooks/useMarketData';
import { Loader2, AlertCircle } from 'lucide-react';

export const RiskAnalysis: React.FC = () => {
  const { data, isLoading, error } = useMarketRisk();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
        <p className="text-sm font-semibold text-slate-500">Deconstructing threat models...</p>
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

  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/30 dark:text-red-400';
      case 'medium':
        return 'bg-amber-50 text-amber-700 border-amber-250 dark:bg-amber-950/30 dark:text-amber-400';
      default:
        return 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/30 dark:text-emerald-400';
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-800 dark:text-white">
          Risk Metrics Analysis
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Component weights contributing to the global Market Risk Score.
        </p>
      </div>

      {/* Component Scores */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-sm text-center">
          <p className="text-xs font-bold text-slate-405 uppercase tracking-wide">Overall Risk</p>
          <p className="text-4xl font-extrabold text-brand-500 mt-3">{data.overallScore}</p>
          <span className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold block mt-1">Weighted Composite</span>
        </div>
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-sm text-center">
          <p className="text-xs font-bold text-slate-405 uppercase tracking-wide">Competitor Threat</p>
          <p className="text-4xl font-extrabold text-red-500 mt-3">{data.competitorThreatScore}</p>
          <span className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold block mt-1">40% Total Weight</span>
        </div>
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-sm text-center">
          <p className="text-xs font-bold text-slate-405 uppercase tracking-wide">Economic Risk</p>
          <p className="text-4xl font-extrabold text-amber-500 mt-3">{data.economicRiskScore}</p>
          <span className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold block mt-1">30% Total Weight</span>
        </div>
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-sm text-center">
          <p className="text-xs font-bold text-slate-405 uppercase tracking-wide">Demand Volatility</p>
          <p className="text-4xl font-extrabold text-yellow-500 mt-3">{data.demandRiskScore}</p>
          <span className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold block mt-1">30% Total Weight</span>
        </div>
      </div>

      {/* Risk Factors List */}
      <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 mb-6">Identified Threat Vectors</h3>
        <div className="space-y-4">
          {data.riskFactors.map((risk, index) => (
            <div 
              key={index} 
              className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 border border-slate-100 dark:border-slate-800/80 rounded-xl bg-slate-50/50 dark:bg-slate-800/20"
            >
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-bold text-slate-800 dark:text-white">{risk.factor}</h4>
                  <p className="text-xs text-slate-550 dark:text-slate-400 mt-1 leading-relaxed">{risk.description}</p>
                </div>
              </div>
              <span className={`inline-block text-xs font-bold px-3 py-1 rounded-full border shrink-0 text-center uppercase ${getSeverityBadge(risk.severity)}`}>
                {risk.severity} Severity
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
