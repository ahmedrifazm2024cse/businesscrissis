import React from 'react';
import { useMarketReport } from '../hooks/useMarketData';
import { Loader2, FileText, Download, Sparkles } from 'lucide-react';

export const Reports: React.FC = () => {
  const { data, isLoading, error } = useMarketReport();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
        <p className="text-sm font-semibold text-slate-500">Compiling executive brief...</p>
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
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-800 dark:text-white">
            Executive Briefs
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Official records of autonomous agent assessment runs.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button 
            onClick={() => window.print()}
            className="flex items-center gap-2 px-4 py-2 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-650 dark:text-slate-350 text-xs font-semibold"
          >
            <Download className="w-4 h-4" />
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      {/* Main Document Layout */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800/80 rounded-2xl shadow-sm overflow-hidden max-w-4xl mx-auto">
        {/* Document Header Accent */}
        <div className="bg-slate-950 px-8 py-6 text-white flex justify-between items-center">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-brand-400" />
            <div>
              <h3 className="font-bold text-md tracking-tight">MARKET ADVISORY BRIEF</h3>
              <p className="text-[10px] text-slate-400 font-semibold tracking-widest uppercase">ID: MI-REPORT-{data.id}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400 font-semibold">CONFIDENCE INDEX</p>
            <p className="text-lg font-extrabold text-brand-400">{data.confidence}%</p>
          </div>
        </div>

        <div className="p-8 md:p-10 space-y-8">
          {/* Metadata Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-semibold text-slate-500 dark:text-slate-400 border-b border-slate-100 dark:border-slate-805/60 pb-6">
            <div>
              <p className="text-slate-400 uppercase text-[10px]">Issued By</p>
              <p className="text-slate-700 dark:text-white mt-1">{data.agent} Agent</p>
            </div>
            <div>
              <p className="text-slate-400 uppercase text-[10px]">Release Timestamp</p>
              <p className="text-slate-700 dark:text-white mt-1">{new Date(data.timestamp).toLocaleString()}</p>
            </div>
            <div>
              <p className="text-slate-400 uppercase text-[10px]">Market Risk Level</p>
              <p className="text-slate-700 dark:text-white mt-1 font-bold">{data.marketRiskScore} / 100</p>
            </div>
            <div>
              <p className="text-slate-400 uppercase text-[10px]">Competitor Threat</p>
              <p className="text-slate-700 dark:text-white mt-1 font-bold">{data.competitorThreat}</p>
            </div>
          </div>

          {/* Section 1: Findings */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-brand-500" />
              <h4 className="text-sm font-extrabold text-slate-800 dark:text-white uppercase tracking-wider">
                Key Intelligence Findings
              </h4>
            </div>
            <ul className="space-y-3.5 pl-2 text-sm text-slate-650 dark:text-slate-350 list-none">
              {data.keyFindings.map((finding, i) => (
                <li key={i} className="flex gap-3 leading-relaxed">
                  <span className="text-brand-500 shrink-0 font-bold">•</span>
                  <span>{finding}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Section 2: Directives */}
          <div className="space-y-4 pt-4 border-t border-slate-100 dark:border-slate-850/60">
            <h4 className="text-sm font-extrabold text-slate-800 dark:text-white uppercase tracking-wider">
              Strategic Directives & Risk Offsets
            </h4>
            <ul className="space-y-3.5 pl-2 text-sm text-slate-650 dark:text-slate-350 list-none">
              {data.recommendations.map((rec, i) => (
                <li key={i} className="flex gap-3 leading-relaxed">
                  <span className="text-emerald-500 shrink-0 font-bold">✓</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
