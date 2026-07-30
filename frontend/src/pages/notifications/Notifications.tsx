import { Bell, ShieldAlert, AlertTriangle, Info, CheckCircle2, Search, Filter } from 'lucide-react';
import clsx from 'clsx';

const mockNotifications = [
  { id: 1, type: 'critical', title: 'Cyber Threat Detected', message: 'DDoS mitigation active on primary load balancers.', time: '2 mins ago', read: false },
  { id: 2, type: 'warning', title: 'Supply Chain Anomaly', message: 'Tier-1 supplier (APAC) latency exceeded SLA thresholds.', time: '14 mins ago', read: false },
  { id: 3, type: 'info', title: 'Workflow Completed', message: 'Executive summary report (REP-001) successfully generated.', time: '1 hour ago', read: true },
  { id: 4, type: 'resolved', title: 'Market Volatility Alert', message: 'Competitor pricing strategy analyzed and mitigated.', time: '3 hours ago', read: true },
  { id: 5, type: 'critical', title: 'Financial Risk Threshold', message: 'Projected Q3 margins dropped below 1.5% tolerance.', time: '5 hours ago', read: true },
];

export function Notifications() {
  const getIcon = (type: string) => {
    switch(type) {
      case 'critical': return <ShieldAlert className="w-5 h-5 text-destructive" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-amber-500" />;
      case 'info': return <Info className="w-5 h-5 text-primary" />;
      case 'resolved': return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
      default: return <Bell className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const getBadgeColor = (type: string) => {
    switch(type) {
      case 'critical': return 'bg-destructive/10 text-destructive border-destructive/20';
      case 'warning': return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
      case 'info': return 'bg-primary/10 text-primary border-primary/20';
      case 'resolved': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      default: return 'bg-secondary text-muted-foreground border-border';
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-end border-b border-border pb-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight flex items-center gap-3">
            <Bell className="w-8 h-8 text-primary" />
            Alerts & Notifications
          </h1>
          <p className="text-muted-foreground mt-1">Real-time system events, AI insights, and workflow triggers.</p>
        </div>
        <div className="flex gap-3">
          <button className="bg-secondary hover:bg-secondary/80 text-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-border">
            Mark all as read
          </button>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 justify-between items-center bg-card/50 backdrop-blur-sm border border-border p-4 rounded-xl">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search alerts..." 
            className="w-full bg-secondary/50 border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-foreground placeholder:text-muted-foreground"
          />
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          {['All', 'Critical', 'Warning', 'Info'].map((filter) => (
            <button key={filter} className={clsx(
              "px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border",
              filter === 'All' ? "bg-primary text-primary-foreground border-primary" : "bg-secondary text-muted-foreground border-border hover:bg-secondary/80 hover:text-foreground"
            )}>
              {filter}
            </button>
          ))}
          <button className="bg-secondary text-muted-foreground p-2 rounded-lg border border-border hover:bg-secondary/80 hover:text-foreground transition-colors ml-2">
            <Filter className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl overflow-hidden divide-y divide-border">
        {mockNotifications.map((note) => (
          <div key={note.id} className={clsx(
            "p-5 flex gap-4 transition-colors hover:bg-secondary/30",
            !note.read && "bg-primary/5"
          )}>
            <div className="mt-1 shrink-0">
              {getIcon(note.type)}
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-start mb-1">
                <div className="flex items-center gap-3">
                  <h4 className={clsx("font-semibold", !note.read ? "text-foreground" : "text-muted-foreground")}>{note.title}</h4>
                  <span className={clsx("text-[10px] px-2 py-0.5 rounded-md border uppercase font-bold tracking-wider", getBadgeColor(note.type))}>
                    {note.type}
                  </span>
                </div>
                <span className="text-xs text-muted-foreground whitespace-nowrap ml-4 font-mono">{note.time}</span>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">{note.message}</p>
            </div>
            {!note.read && (
              <div className="shrink-0 self-center">
                <div className="w-2.5 h-2.5 rounded-full bg-primary shadow-[0_0_8px_rgba(37,99,235,0.8)]"></div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
