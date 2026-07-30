import React, { useEffect, useRef, useState } from 'react';
import { Terminal, Zap, Activity, X } from 'lucide-react';

interface LogEntry {
  ts: number;
  source: string;
  message: string;
  type: 'thought' | 'action' | 'result' | 'system' | 'heartbeat';
}

interface AgentThinkingPanelProps {
  isRunning: boolean;
  onClose?: () => void;
}

const TYPE_STYLES: Record<string, string> = {
  thought: 'text-brand-400',
  action:  'text-amber-400',
  result:  'text-emerald-400',
  system:  'text-violet-400',
};

const TYPE_PREFIX: Record<string, string> = {
  thought: '💭',
  action:  '⚡',
  result:  '✅',
  system:  '🔧',
};

export const AgentThinkingPanel: React.FC<AgentThinkingPanelProps> = ({ isRunning, onClose }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [connected, setConnected] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Connect to SSE when component mounts
    const es = new EventSource('http://localhost:8000/api/market/agent-logs');
    esRef.current = es;

    es.onopen = () => setConnected(true);

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as LogEntry;
        if (data.type === 'heartbeat') return;
        setLogs((prev) => [...prev, data]);
      } catch {
        // Ignore parse errors
      }
    };

    es.onerror = () => {
      setConnected(false);
    };

    return () => {
      es.close();
      setConnected(false);
    };
  }, []);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const formatTime = (ts: number) => {
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  return (
    <div className="flex flex-col h-full rounded-2xl overflow-hidden border border-brand-900/40 terminal-panel animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-brand-900/30 bg-[#050b15]">
        <div className="flex items-center gap-2.5">
          <Terminal className="w-4 h-4 text-brand-400" />
          <span className="font-terminal text-xs font-semibold text-brand-300 uppercase tracking-widest">
            Agent Console
          </span>
          {isRunning && (
            <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-400 uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping inline-block" />
              Live
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-500' : 'bg-red-500'}`} />
          <span className="font-terminal text-[10px] text-slate-500">
            {connected ? 'SSE Connected' : 'Disconnected'}
          </span>
          {onClose && (
            <button onClick={onClose} className="text-slate-600 hover:text-slate-300 transition-colors">
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Log body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-1.5 min-h-0 scan-overlay">
        {logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-3 py-10">
            <Activity className="w-8 h-8 text-brand-900/60" />
            <p className="font-terminal text-xs text-slate-600">
              {isRunning ? 'Awaiting agent output...' : 'Run an analysis to see agent thinking.'}
            </p>
          </div>
        ) : (
          logs.map((log, i) => (
            <div
              key={i}
              className="font-terminal text-[11px] leading-relaxed flex gap-2 animate-fade-in"
            >
              <span className="text-slate-600 shrink-0 select-none">[{formatTime(log.ts)}]</span>
              <span className="text-slate-600 shrink-0 select-none">{TYPE_PREFIX[log.type] ?? '•'}</span>
              <span className={`text-slate-500 shrink-0 font-semibold`}>{log.source}:</span>
              <span className={`${TYPE_STYLES[log.type] ?? 'text-slate-400'} break-all`}>
                {log.message}
              </span>
            </div>
          ))
        )}

        {/* Typing indicator when running */}
        {isRunning && (
          <div className="flex items-center gap-2 pt-1">
            <span className="text-slate-600 font-terminal text-[11px]">Agent processing</span>
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Footer stats */}
      <div className="px-4 py-2 border-t border-brand-900/30 bg-[#050b15] flex items-center justify-between">
        <span className="font-terminal text-[10px] text-slate-600">
          {logs.length} events captured
        </span>
        <button
          onClick={() => setLogs([])}
          className="font-terminal text-[10px] text-slate-600 hover:text-brand-400 transition-colors"
        >
          Clear
        </button>
      </div>
    </div>
  );
};
