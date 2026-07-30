import { ShieldAlert, AlertTriangle, Crosshair, Users, Activity, TrendingDown, RefreshCw, FileText } from 'lucide-react';
import { useCommanderStore } from '../../store/useCommanderStore';
import { useEffect } from 'react';

export function CrisisCommandCenter() {
  const { commandCenter, fetchCommandCenter } = useCommanderStore();

  useEffect(() => {
    fetchCommandCenter();
    const interval = setInterval(fetchCommandCenter, 10000);
    return () => clearInterval(interval);
  }, []);

  if (!commandCenter || commandCenter.status === "no_active_crisis") {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-end border-b border-border pb-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground tracking-tight flex items-center gap-3">
              <ShieldAlert className="w-8 h-8 text-emerald-500" />
              Crisis Command Center
            </h1>
            <p className="text-muted-foreground mt-1">No active crisis detected.</p>
          </div>
        </div>
      </div>
    );
  }

  const { crisis, recommendations, timeline } = commandCenter;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end border-b border-border pb-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight flex items-center gap-3">
            <ShieldAlert className="w-8 h-8 text-destructive" />
            Crisis Command Center
          </h1>
          <p className="text-muted-foreground mt-1">Centralized view for active business disruptions and AI-driven mitigation.</p>
        </div>
        <div className="flex gap-3">
          <button className="bg-secondary hover:bg-secondary/80 text-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-border flex items-center gap-2">
            <RefreshCw className="w-4 h-4" /> Refresh Data
          </button>
          <button className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-[0_0_15px_rgba(37,99,235,0.2)]">
            Generate Briefing
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Crisis Details */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-destructive/5 border border-destructive/20 p-6 rounded-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4">
              <span className="bg-destructive text-destructive-foreground text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest animate-pulse">Critical Priority</span>
            </div>
            
            <h2 className="text-xl font-bold text-foreground mb-2">{crisis.title}</h2>
            <p className="text-muted-foreground mb-6">{crisis.description}</p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-background/50 backdrop-blur border border-border p-3 rounded-lg">
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Severity Score</p>
                <p className="text-2xl font-bold text-destructive mt-1">{crisis.severityScore}<span className="text-sm text-muted-foreground">/100</span></p>
              </div>
              <div className="bg-background/50 backdrop-blur border border-border p-3 rounded-lg">
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Financial Impact</p>
                <p className="text-2xl font-bold text-amber-500 mt-1">{crisis.financialImpact}</p>
              </div>
              <div className="bg-background/50 backdrop-blur border border-border p-3 rounded-lg">
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Affected Depts</p>
                <p className="text-2xl font-bold text-foreground mt-1">{crisis.affectedDepts}</p>
              </div>
              <div className="bg-background/50 backdrop-blur border border-border p-3 rounded-lg">
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Time Active</p>
                <p className="text-2xl font-bold text-foreground mt-1">{crisis.timeActive}</p>
              </div>
            </div>
          </div>

          <div className="bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl">
            <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <Crosshair className="w-5 h-5 text-primary" /> AI Strategic Recommendations
            </h3>
            <div className="space-y-4">
              {recommendations.map((rec: any, i: number) => (
                <div key={i} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-secondary/30 border border-border rounded-lg gap-4">
                  <div className="flex-1">
                    <p className="font-medium text-foreground">{rec.title}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1"><Activity className="w-3.5 h-3.5 text-emerald-400" /> Conf: {rec.conf}</span>
                      <span className="flex items-center gap-1"><TrendingDown className="w-3.5 h-3.5 text-amber-400" /> Impact: {rec.impact}</span>
                    </div>
                  </div>
                  <button className="bg-secondary hover:bg-secondary/80 border border-border px-4 py-2 rounded text-sm font-medium transition-colors">
                    {rec.action}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar context */}
        <div className="space-y-6">
          <div className="bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl">
            <h3 className="text-lg font-bold text-foreground mb-4">Live Incident Timeline</h3>
            <div className="relative border-l border-border ml-3 space-y-6">
              {timeline.map((event: any, i: number) => (
                <div key={i} className="pl-6 relative">
                  <div className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-primary/20 border border-primary"></div>
                  <p className="text-xs text-muted-foreground font-mono mb-1">{event.time}</p>
                  <p className="text-sm text-foreground">{event.text}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl">
            <h3 className="text-lg font-bold text-foreground mb-4">Department Status</h3>
            <div className="space-y-3">
              {[
                { name: 'Supply Chain', status: 'Critical', icon: AlertTriangle, color: 'text-destructive' },
                { name: 'Customer Success', status: 'Warning', icon: Users, color: 'text-amber-500' },
                { name: 'Financial', status: 'Warning', icon: TrendingDown, color: 'text-amber-500' },
                { name: 'Legal', status: 'Stable', icon: FileText, color: 'text-emerald-500' },
              ].map((dept, i) => (
                <div key={i} className="flex items-center justify-between p-2 bg-secondary/20 rounded">
                  <div className="flex items-center gap-2">
                    <dept.icon className={`w-4 h-4 ${dept.color}`} />
                    <span className="text-sm font-medium text-foreground">{dept.name}</span>
                  </div>
                  <span className={`text-xs font-bold uppercase ${dept.color}`}>{dept.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
