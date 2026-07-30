import { useEffect } from 'react';
import { useCommanderStore } from '../../store/useCommanderStore';
import { Cpu, HardDrive, Clock, Activity, AlertCircle, CheckCircle2, Terminal } from 'lucide-react';
import clsx from 'clsx';

export function MultiAgentWorkspace() {
  const { agents, fetchAgents } = useCommanderStore();

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(() => {
      fetchAgents();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch(status.toLowerCase()) {
      case 'running': return 'text-primary bg-primary/10 border-primary/30';
      case 'idle': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30';
      case 'offline': return 'text-destructive bg-destructive/10 border-destructive/30';
      default: return 'text-muted-foreground bg-secondary border-border';
    }
  };

  const getStatusIcon = (status: string) => {
    switch(status.toLowerCase()) {
      case 'running': return <Activity className="w-3.5 h-3.5" />;
      case 'idle': return <CheckCircle2 className="w-3.5 h-3.5" />;
      case 'offline': return <AlertCircle className="w-3.5 h-3.5" />;
      default: return <Clock className="w-3.5 h-3.5" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight">Multi-Agent Workspace</h1>
          <p className="text-muted-foreground mt-1">Live telemetry and operational status for all 13 specialized AI agents.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div key={agent.id} className="bg-card/50 backdrop-blur-sm border border-border p-5 rounded-xl shadow-sm hover:border-primary/40 transition-all group flex flex-col h-full">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-semibold text-foreground text-lg">{agent.name}</h3>
                <p className="text-xs font-mono text-muted-foreground mt-0.5">{agent.type} Layer</p>
              </div>
              <div className={clsx("flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium uppercase tracking-wider", getStatusColor(agent.status))}>
                {getStatusIcon(agent.status)}
                {agent.status}
              </div>
            </div>

            <div className="bg-secondary/30 border border-border/50 rounded-lg p-3 mb-4">
              <p className="text-xs text-muted-foreground mb-1 uppercase tracking-wider font-semibold">Current Operation</p>
              <p className="text-sm text-foreground line-clamp-2">{agent.task}</p>
            </div>

            <div className="bg-black/50 border border-border/50 rounded-lg p-3 mb-4 flex-1 overflow-hidden flex flex-col min-h-[150px]">
              <p className="text-[10px] text-muted-foreground mb-2 uppercase tracking-wider font-semibold flex items-center gap-1">
                <Terminal className="w-3 h-3" /> {agent.status.toLowerCase() === 'completed' ? 'Output Result' : 'Live Logs'}
              </p>
              <div className="flex-1 overflow-y-auto space-y-1 custom-scrollbar pr-2 font-mono text-xs">
                {agent.status.toLowerCase() === 'running' ? (
                  <>
                    <p className="text-emerald-400">&gt; Initializing task parameters...</p>
                    <p className="text-emerald-400">&gt; Connecting to data stream [OK]</p>
                    <p className="text-emerald-400 animate-pulse">&gt; Processing... {agent.task}</p>
                  </>
                ) : agent.status.toLowerCase() === 'idle' ? (
                  <p className="text-muted-foreground">&gt; Waiting for orchestrator trigger...</p>
                ) : agent.status.toLowerCase() === 'completed' ? (
                  <div className="text-emerald-300 whitespace-pre-wrap font-mono text-xs break-words">
                    {agent.output ? (
                      Object.entries(agent.output).map(([key, value], idx) => (
                        <div key={idx} className="mb-1">
                          <span className="text-blue-400">"{key}"</span>: 
                          <span className={typeof value === 'string' ? 'text-amber-300' : typeof value === 'number' ? 'text-purple-400' : 'text-emerald-200'}>
                            {typeof value === 'object' ? JSON.stringify(value) : ` ${JSON.stringify(value)}`}
                          </span>
                        </div>
                      ))
                    ) : 'No output recorded.'}
                  </div>
                ) : (
                  <p className="text-destructive">&gt; Connection lost. Attempting reconnect...</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3 border-t border-border pt-4 mt-auto">
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider flex items-center gap-1"><Cpu className="w-3 h-3"/> CPU</p>
                <p className="text-sm font-mono text-foreground mt-0.5">{agent.cpu}</p>
              </div>
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider flex items-center gap-1"><HardDrive className="w-3 h-3"/> MEM</p>
                <p className="text-sm font-mono text-foreground mt-0.5">{agent.mem}</p>
              </div>
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider flex items-center gap-1"><Clock className="w-3 h-3"/> PING</p>
                <p className="text-sm font-mono text-foreground mt-0.5">{agent.latency}</p>
              </div>
            </div>
            
            {/* Progress Bar (Simulated based on status) */}
            <div className="mt-4 h-1 w-full bg-secondary rounded-full overflow-hidden">
              <div 
                className={clsx("h-full rounded-full transition-all duration-1000", agent.status.toLowerCase() === 'running' ? 'bg-primary w-3/4' : agent.status.toLowerCase() === 'idle' ? 'bg-emerald-400 w-full' : 'bg-destructive w-0')}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
