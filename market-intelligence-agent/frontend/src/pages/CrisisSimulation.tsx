import React, { useState, useRef, useEffect } from 'react';
import { useCrisisAnalyze } from '../hooks/useMarketData';
import { AgentThinkingPanel } from '../components/AgentThinkingPanel';
import { 
  ShieldAlert, Send, FileText, CheckCircle2, Sparkles, Loader2,
  Terminal, AlertTriangle, TrendingDown, Users2, Zap, ChevronRight, X
} from 'lucide-react';
import { CrisisAnalysisResponse } from '../types/market';

type ChatMessage = {
  sender: 'agent' | 'user';
  text: string;
  result?: CrisisAnalysisResponse;
  isTyping?: boolean;
};

const RISK_COLOR = (score: string) => {
  const n = parseInt(score);
  if (n >= 8) return 'text-red-400 border-red-500/30 bg-red-500/10';
  if (n >= 5) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
  return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
};

const ResultCard: React.FC<{ data: CrisisAnalysisResponse }> = ({ data }) => (
  <div className="mt-3 rounded-xl border border-brand-500/20 overflow-hidden text-left animate-slide-in-up"
       style={{ background: 'rgba(5,12,24,0.95)' }}>
    {/* Risk Score Header */}
    <div className="px-4 py-3 border-b border-brand-500/15 bg-brand-500/5 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-brand-400" />
        <span className="text-xs font-bold text-brand-300">Crisis Assessment Complete</span>
      </div>
      <span className={`text-xs font-extrabold px-2.5 py-1 rounded-lg border font-terminal ${RISK_COLOR(data.market_risk_score)}`}>
        Risk: {data.market_risk_score}/10
      </span>
    </div>

    <div className="p-4 space-y-4">
      {/* Summary */}
      <div>
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1.5">Market Summary</p>
        <p className="text-xs text-slate-300 leading-relaxed">{data.market_summary}</p>
      </div>

      {/* Impact + Competitors */}
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-lg border border-slate-800/60 bg-slate-900/40 p-3">
          <p className="text-[9px] font-bold text-slate-500 uppercase mb-1.5">Market Impact</p>
          <p className="text-[11px] text-slate-400 leading-relaxed">{data.market_impact}</p>
        </div>
        <div className="rounded-lg border border-slate-800/60 bg-slate-900/40 p-3">
          <p className="text-[9px] font-bold text-slate-500 uppercase mb-1.5">Competitor Reaction</p>
          <p className="text-[11px] text-slate-400 leading-relaxed">{data.competitor_analysis}</p>
        </div>
      </div>

      {/* Opportunities */}
      <div>
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Opportunities</p>
        <ul className="space-y-1.5">
          {data.business_opportunities.map((o, i) => (
            <li key={i} className="flex gap-2 text-xs text-brand-400">
              <ChevronRight className="w-3.5 h-3.5 shrink-0 mt-0.5" />
              <span>{o}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Recommendations */}
      <div className="border-t border-slate-800/40 pt-3">
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Strategic Directives</p>
        <ul className="space-y-1.5">
          {data.recommendations.map((r, i) => (
            <li key={i} className="flex gap-2 text-xs text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5 shrink-0 mt-0.5 text-emerald-500" />
              <span>{r}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  </div>
);

export const CrisisSimulation: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'form' | 'chatbot'>('form');
  const [showConsole, setShowConsole] = useState(false);
  const crisisMutation = useCrisisAnalyze();
  const chatEndRef = useRef<HTMLDivElement>(null);

  const [formData, setFormData] = useState({
    company_name: 'TechCorp SaaS',
    industry: 'Enterprise Software',
    crisis_type: 'Competitor Pricing War & Data Mandates',
    crisis_description: 'Competitor Alpha launched a premium tier with 20% discount, combined with EU local storage compliance mandates.',
    current_market_trend: 'Consolidation toward sovereign cloud models',
    competitor_information: 'Competitor Alpha and Epsilon have native EU cloud hosting.',
    customer_demand: 'Shifting to vendors guaranteeing EU data residency.',
    location: 'Europe & UK'
  });

  const [messages, setMessages] = useState<ChatMessage[]>([
    { 
      sender: 'agent', 
      text: '⚡ War Room Online. Paste a crisis briefing below or use the structured form. I will parse the context and invoke the market intelligence engine.' 
    }
  ]);
  const [chatInput, setChatInput] = useState('');

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowConsole(true);
    crisisMutation.mutate(formData);
  };

  const handleChatSend = () => {
    if (!chatInput.trim() || crisisMutation.isPending) return;
    const userMsg = chatInput.trim();
    setChatInput('');

    // Add user message
    setMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    
    // Add typing indicator
    setMessages(prev => [...prev, { sender: 'agent', text: '', isTyping: true }]);

    const payload = {
      company_name: 'Parsed Company',
      industry: 'Enterprise',
      crisis_type: 'Operational Crisis',
      crisis_description: userMsg,
      current_market_trend: 'Market volatility',
      competitor_information: 'Active sector competitors',
      customer_demand: 'Stability and resilience',
      location: 'Global'
    };

    crisisMutation.mutate(payload, {
      onSuccess: (data) => {
        // Remove typing indicator, add result message
        setMessages(prev => {
          const withoutTyping = prev.filter(m => !m.isTyping);
          return [
            ...withoutTyping,
            {
              sender: 'agent',
              text: `Crisis assessment for: "${userMsg.slice(0, 60)}${userMsg.length > 60 ? '...' : ''}"`,
              result: data
            }
          ];
        });
      },
      onError: () => {
        setMessages(prev => {
          const withoutTyping = prev.filter(m => !m.isTyping);
          return [
            ...withoutTyping,
            { sender: 'agent', text: '❌ Crisis analysis failed. Check backend connection and retry.' }
          ];
        });
      }
    });
  };

  return (
    <div className="space-y-6">
      {/* ── Header ──────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 animate-slide-in-up">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full border bg-red-500/10 text-red-400 border-red-500/20">
              War Room
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
            Crisis <span className="gradient-text-brand">Commander</span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Input crisis telemetry · Get instant AI-powered market response strategy
          </p>
        </div>
        <button
          onClick={() => setShowConsole(!showConsole)}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold border transition-all shrink-0 ${
            showConsole
              ? 'bg-violet-500/15 text-violet-300 border-violet-500/30'
              : 'bg-slate-800/60 text-slate-400 border-slate-700/60 hover:border-slate-600'
          }`}
        >
          <Terminal className="w-4 h-4" />
          Agent Console
        </button>
      </div>

      {/* ── Agent Console ────────────────────────────────────────── */}
      {showConsole && (
        <div className="h-52 animate-slide-in-up">
          <AgentThinkingPanel isRunning={crisisMutation.isPending} onClose={() => setShowConsole(false)} />
        </div>
      )}

      {/* ── Tabs ─────────────────────────────────────────────────── */}
      <div className="flex gap-1 p-1 rounded-xl bg-slate-900/60 border border-slate-800/60 w-fit">
        {(['form', 'chatbot'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-5 py-2 rounded-lg text-sm font-semibold transition-all ${
              activeTab === tab
                ? 'bg-gradient-to-r from-brand-600 to-violet-600 text-white shadow-md'
                : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            {tab === 'form' ? '⚙️ Structured Form' : '💬 Intelligence Chat'}
          </button>
        ))}
      </div>

      {/* ── Main Grid ────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Left: Input */}
        <div>
          {activeTab === 'form' ? (
            <form onSubmit={handleFormSubmit}
                  className="rounded-2xl border border-slate-800/60 overflow-hidden animate-fade-in"
                  style={{ background: 'rgba(10,18,35,0.85)' }}>
              <div className="px-6 py-4 border-b border-slate-800/60 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-red-400" />
                <span className="text-sm font-semibold text-slate-300">Crisis Parameters</span>
              </div>
              <div className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: 'Company Name', name: 'company_name' },
                    { label: 'Industry', name: 'industry' },
                    { label: 'Crisis Type', name: 'crisis_type' },
                    { label: 'Location', name: 'location' },
                  ].map(({ label, name }) => (
                    <div key={name}>
                      <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1.5">{label}</label>
                      <input
                        type="text"
                        name={name}
                        value={(formData as Record<string, string>)[name]}
                        onChange={handleFormChange}
                        className="w-full p-2.5 rounded-xl border border-slate-700/60 bg-slate-900/60 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-brand-500/60 focus:ring-1 focus:ring-brand-500/30 transition-all"
                      />
                    </div>
                  ))}
                </div>
                {[
                  { label: 'Crisis Description', name: 'crisis_description', rows: 2 },
                  { label: 'Current Market Trend', name: 'current_market_trend', rows: 1 },
                  { label: 'Competitor Information', name: 'competitor_information', rows: 1 },
                  { label: 'Customer Demand Status', name: 'customer_demand', rows: 1 },
                ].map(({ label, name, rows }) => (
                  <div key={name}>
                    <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1.5">{label}</label>
                    <textarea
                      name={name}
                      rows={rows}
                      value={(formData as Record<string, string>)[name]}
                      onChange={handleFormChange}
                      className="w-full p-2.5 rounded-xl border border-slate-700/60 bg-slate-900/60 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-brand-500/60 focus:ring-1 focus:ring-brand-500/30 transition-all resize-none"
                    />
                  </div>
                ))}

                <button
                  type="submit"
                  disabled={crisisMutation.isPending}
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-red-600 to-brand-600 text-white font-semibold text-sm hover:from-red-500 hover:to-brand-500 transition-all shadow-lg shadow-red-500/20 flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {crisisMutation.isPending ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /><span>Running Crisis Assessment...</span></>
                  ) : (
                    <><ShieldAlert className="w-4 h-4" /><span>Run Market Crisis Assessment</span></>
                  )}
                </button>
              </div>
            </form>
          ) : (
            /* Chat interface */
            <div className="flex flex-col h-[560px] rounded-2xl border border-slate-800/60 overflow-hidden animate-fade-in"
                 style={{ background: 'rgba(10,18,35,0.85)' }}>
              <div className="px-5 py-3.5 border-b border-slate-800/60 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-sm font-semibold text-slate-300">Crisis Intelligence Chat</span>
                <span className="ml-auto text-[10px] font-terminal text-slate-600">AI Officer Online</span>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                    {msg.sender === 'agent' && (
                      <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-brand-600 to-violet-600 flex items-center justify-center shrink-0 mr-2 mt-0.5">
                        <Zap className="w-3.5 h-3.5 text-white" />
                      </div>
                    )}
                    <div className={`max-w-[85%] ${msg.sender === 'user' ? '' : ''}`}>
                      <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                        msg.sender === 'user'
                          ? 'bg-gradient-to-br from-brand-600 to-violet-600 text-white rounded-br-none'
                          : 'rounded-bl-none border border-slate-800/60 text-slate-300'
                      }`}
                      style={msg.sender === 'agent' ? { background: 'rgba(15,25,45,0.9)' } : {}}>
                        {msg.isTyping ? (
                          <div className="flex items-center gap-1 py-1">
                            <span className="typing-dot" />
                            <span className="typing-dot" />
                            <span className="typing-dot" />
                          </div>
                        ) : (
                          <>{msg.text}</>
                        )}
                      </div>
                      {/* Inline result card */}
                      {msg.result && <ResultCard data={msg.result} />}
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>

              <div className="p-3 border-t border-slate-800/60 flex gap-2">
                <input
                  type="text"
                  placeholder="Describe the crisis situation..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleChatSend()}
                  className="flex-1 p-3 rounded-xl border border-slate-700/60 bg-slate-900/60 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-brand-500/60 focus:ring-1 focus:ring-brand-500/30 transition-all"
                />
                <button
                  onClick={handleChatSend}
                  disabled={crisisMutation.isPending || !chatInput.trim()}
                  className="p-3 rounded-xl bg-gradient-to-br from-brand-600 to-violet-600 hover:from-brand-500 hover:to-violet-500 text-white transition-all disabled:opacity-40 shrink-0"
                >
                  {crisisMutation.isPending ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right: Results */}
        <div>
          {crisisMutation.data && activeTab === 'form' ? (
            <div className="rounded-2xl border border-brand-500/20 overflow-hidden animate-slide-in-right"
                 style={{ background: 'rgba(10,18,35,0.90)' }}>
              {/* Header */}
              <div className="px-6 py-4 border-b border-brand-500/15 bg-brand-500/5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-brand-400" />
                  <span className="text-sm font-bold text-brand-300">War Room Assessment</span>
                </div>
                <span className={`text-sm font-extrabold px-3 py-1 rounded-lg border font-terminal ${RISK_COLOR(crisisMutation.data.market_risk_score)}`}>
                  Risk Score: {crisisMutation.data.market_risk_score}/10
                </span>
              </div>

              <div className="p-6 space-y-5">
                {/* Summary */}
                <div className="p-4 rounded-xl border border-slate-800/40 bg-slate-900/30">
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Market Summary</p>
                  <p className="text-sm text-slate-300 leading-relaxed font-medium">{crisisMutation.data.market_summary}</p>
                </div>

                {/* Impact + Competitor grid */}
                <div className="grid grid-cols-1 gap-3">
                  <div className="p-4 rounded-xl border border-amber-500/15 bg-amber-500/5">
                    <p className="text-[10px] font-bold text-amber-500/70 uppercase tracking-widest mb-2">Market Impact</p>
                    <p className="text-sm text-slate-400 leading-relaxed">{crisisMutation.data.market_impact}</p>
                  </div>
                  <div className="p-4 rounded-xl border border-red-500/15 bg-red-500/5">
                    <p className="text-[10px] font-bold text-red-500/70 uppercase tracking-widest mb-2">Competitor Reactions</p>
                    <p className="text-sm text-slate-400 leading-relaxed">{crisisMutation.data.competitor_analysis}</p>
                  </div>
                </div>

                {/* Demand prediction */}
                <div className="p-4 rounded-xl border border-violet-500/15 bg-violet-500/5">
                  <p className="text-[10px] font-bold text-violet-400/70 uppercase tracking-widest mb-2">Demand Prediction</p>
                  <p className="text-sm text-slate-400 leading-relaxed">{crisisMutation.data.customer_demand_prediction}</p>
                </div>

                {/* Opportunities */}
                <div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2.5">Strategic Opportunities</p>
                  <ul className="space-y-2">
                    {crisisMutation.data.business_opportunities.map((o, i) => (
                      <li key={i} className="flex gap-2.5 text-sm text-brand-400">
                        <ChevronRight className="w-4 h-4 shrink-0 mt-0.5" />
                        <span>{o}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Recommendations */}
                <div className="border-t border-slate-800/40 pt-4">
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2.5">Executive Directives</p>
                  <ul className="space-y-2.5">
                    {crisisMutation.data.recommendations.map((r, i) => (
                      <li key={i} className="flex gap-2.5 text-sm text-emerald-400">
                        <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-500" />
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ) : !crisisMutation.data ? (
            <div className="h-full min-h-[400px] flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-800/60 text-center p-8 animate-fade-in"
                 style={{ background: 'rgba(10,18,35,0.5)' }}>
              <div className="w-16 h-16 rounded-2xl bg-slate-900/60 border border-slate-800/60 flex items-center justify-center mb-4">
                <FileText className="w-7 h-7 text-slate-700" />
              </div>
              <h4 className="font-bold text-slate-500 mb-2">Awaiting Crisis Briefing</h4>
              <p className="text-sm text-slate-600 max-w-xs">
                Fill out the form or send a message to initiate AI-powered crisis market assessment.
              </p>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};
