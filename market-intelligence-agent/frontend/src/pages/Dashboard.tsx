import React, { useState } from 'react';
import { 
  ShieldAlert, Sparkles, Newspaper, Play, Loader2, Info,
  TrendingUp, Users2, Zap, RefreshCw, ChevronRight, AlertTriangle
} from 'lucide-react';
import { useMarketDashboard, useTriggerAnalysis } from '../hooks/useMarketData';
import { MetricCard } from '../components/MetricCard';
import { RiskGauge } from '../components/RiskGauge';
import { CompetitorsTable } from '../components/CompetitorsTable';
import { RecommendationPanel } from '../components/RecommendationPanel';
import { AgentThinkingPanel } from '../components/AgentThinkingPanel';

export const Dashboard: React.FC = () => {
  const { data, isLoading, error, refetch } = useMarketDashboard();
  const analyzeMutation = useTriggerAnalysis();
  const [showThinking, setShowThinking] = useState(false);

  const handleAnalyze = () => {
    setShowThinking(true);
    analyzeMutation.mutate();
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-5">
        <div className="relative">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-500/20 to-violet-500/20 flex items-center justify-center border border-brand-500/20 animate-pulse">
            <Zap className="w-7 h-7 text-brand-400" />
          </div>
          <div className="absolute inset-0 rounded-2xl animate-ping bg-brand-500/10" />
        </div>
        <div className="text-center">
          <p className="font-semibold text-slate-300">Loading Intelligence Feed</p>
          <p className="text-sm text-slate-600 mt-1 font-terminal">Syncing market data...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 rounded-2xl border border-red-500/20 bg-red-500/5 flex items-start gap-4 animate-slide-in-up">
        <div className="p-2 rounded-xl bg-red-500/15">
          <AlertTriangle className="w-5 h-5 text-red-400" />
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-red-400 mb-1">Backend Connection Failed</h3>
          <p className="text-sm text-slate-500">
            Could not reach the Market Intelligence API at <span className="font-terminal text-brand-400">localhost:8000</span>. 
            Start the FastAPI backend with <span className="font-terminal text-amber-400">python main.py</span>.
          </p>
          <button
            onClick={() => refetch()}
            className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-brand-400 hover:text-brand-300 transition-colors"
          >
            <RefreshCw className="w-3 h-3" /> Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-7">
      {/* ── Header ───────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 animate-slide-in-up">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <div className="live-badge">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              Live Intelligence
            </div>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
            Market Intelligence <span className="gradient-text-brand">Command Center</span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Continuous threat surveillance · Competitor movement mapping · Demand forecasting
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => setShowThinking(!showThinking)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold border transition-all ${
              showThinking
                ? 'bg-violet-500/15 text-violet-300 border-violet-500/30'
                : 'bg-slate-800/60 text-slate-400 border-slate-700/60 hover:border-slate-600'
            }`}
          >
            <Zap className="w-4 h-4" />
            Agent Console
          </button>

          <button
            onClick={handleAnalyze}
            disabled={analyzeMutation.isPending}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-violet-600 text-white font-semibold text-sm hover:from-brand-500 hover:to-violet-500 transition-all shadow-lg shadow-brand-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {analyzeMutation.isPending ? (
              <><Loader2 className="w-4 h-4 animate-spin" /><span>Running Analysis...</span></>
            ) : (
              <><Play className="w-4 h-4" fill="currentColor" /><span>Run Agent Analysis</span></>
            )}
          </button>
        </div>
      </div>

      {/* ── Agent Console (collapsible) ───────────────────────────── */}
      {showThinking && (
        <div className="h-64 animate-slide-in-up">
          <AgentThinkingPanel
            isRunning={analyzeMutation.isPending}
            onClose={() => setShowThinking(false)}
          />
        </div>
      )}

      {/* ── KPI Cards ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <MetricCard
          title="Market Risk Score"
          value={data.marketRiskScore}
          subtitle="Composite vulnerability rating across all vectors"
          icon={<ShieldAlert className="w-5 h-5" />}
          colorScheme={data.marketRiskScore > 75 ? 'red' : data.marketRiskScore > 45 ? 'yellow' : 'green'}
        />
        <MetricCard
          title="Competitor Threat"
          value={data.competitorThreat}
          subtitle="Relative peer movement intensity index"
          icon={<Users2 className="w-5 h-5" />}
          colorScheme={data.competitorThreat === 'High' ? 'red' : data.competitorThreat === 'Medium' ? 'yellow' : 'green'}
        />
        <MetricCard
          title="Market Opportunity"
          value={data.marketOpportunity}
          subtitle="Untapped industry growth potential"
          icon={<Sparkles className="w-5 h-5" />}
          colorScheme={data.marketOpportunity === 'High' ? 'green' : 'blue'}
        />
      </div>

      {/* ── Risk Gauge + Competitors ──────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <RiskGauge score={data.marketRiskScore} />
        </div>
        <div className="lg:col-span-2">
          <CompetitorsTable competitors={data.competitors} />
        </div>
      </div>

      {/* ── Recommendations + News ─────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecommendationPanel recommendations={data.recommendations} />

        {/* News Feed */}
        <div className="rounded-2xl border border-slate-800/60 overflow-hidden"
             style={{ background: 'rgba(10,18,35,0.85)' }}>
          <div className="px-6 py-4 border-b border-slate-800/60 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Newspaper className="w-4 h-4 text-brand-400" />
              <h3 className="text-sm font-semibold text-slate-300">Industry News Bulletin</h3>
            </div>
            <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider font-terminal">
              {data.news.length} Sources
            </span>
          </div>

          <div className="divide-y divide-slate-800/40">
            {data.news.slice(0, 5).map((item, idx) => (
              <div key={idx} className="px-6 py-4 hover:bg-slate-800/20 transition-colors group">
                <div className="flex justify-between items-start gap-3 mb-1">
                  <h4 className="text-sm font-semibold text-slate-200 line-clamp-1 group-hover:text-brand-300 transition-colors">
                    {item.title}
                  </h4>
                  <span className={`text-[9px] font-extrabold px-2 py-0.5 rounded border uppercase shrink-0 ${
                    item.sentiment === 'Positive'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : item.sentiment === 'Negative'
                      ? 'bg-red-500/10 text-red-400 border-red-500/20'
                      : 'bg-slate-700/50 text-slate-400 border-slate-700'
                  }`}>{item.sentiment}</span>
                </div>
                <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed mb-2">{item.summary}</p>
                <div className="flex justify-between text-[10px] font-semibold text-slate-600 font-terminal">
                  <span>{item.source}</span>
                  <div className="flex items-center gap-2">
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                      item.impact_score >= 8 ? 'bg-red-500/10 text-red-400' :
                      item.impact_score >= 5 ? 'bg-amber-500/10 text-amber-400' :
                      'bg-slate-700/50 text-slate-500'
                    }`}>Impact {item.impact_score}/10</span>
                    <span>{item.date}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="px-6 py-3 border-t border-slate-800/40 flex items-center gap-2 text-[11px] text-slate-600">
            <Info className="w-3 h-3" />
            <span>Syncing continuously from public regulatory feeds</span>
          </div>
        </div>
      </div>

      {/* ── Agent Analysis Results ─────────────────────────────────── */}
      {analyzeMutation.data && (
        <div className="rounded-2xl border border-brand-500/20 overflow-hidden animate-slide-in-up"
             style={{ background: 'rgba(10,18,35,0.85)' }}>
          <div className="px-6 py-4 border-b border-brand-500/15 flex items-center justify-between bg-brand-500/5">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-brand-400" />
              <span className="text-sm font-semibold text-brand-300">Agent Analysis Complete</span>
            </div>
            <span className="text-[10px] font-bold font-terminal text-emerald-400 border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 rounded">
              Confidence: {analyzeMutation.data.confidence}%
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">Key Findings</p>
              <ul className="space-y-2">
                {analyzeMutation.data.keyFindings.map((f, i) => (
                  <li key={i} className="flex gap-2.5 text-sm text-slate-400 leading-relaxed">
                    <ChevronRight className="w-4 h-4 text-brand-500 shrink-0 mt-0.5" />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">Recommendations</p>
              <ul className="space-y-2">
                {analyzeMutation.data.recommendations.map((r, i) => (
                  <li key={i} className="flex gap-2.5 text-sm text-emerald-400 leading-relaxed">
                    <span className="text-emerald-500 mt-0.5">✓</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
