import { useCommanderStore } from '../../store/useCommanderStore';
import { ShieldCheck, ServerCrash, Search, UserCircle } from 'lucide-react';
import clsx from 'clsx';

export function Topbar() {
  const { wsConnected } = useCommanderStore();

  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex items-center gap-4 flex-1">
        <div className="relative w-96">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search agents, workflows, or reports..." 
            className="w-full bg-secondary/50 border border-border rounded-lg pl-10 pr-4 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-foreground placeholder:text-muted-foreground"
          />
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-sm font-medium">
          <span className="text-muted-foreground">System Status:</span>
          <div className={clsx("flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs", 
            wsConnected 
              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
              : "bg-destructive/10 border-destructive/20 text-destructive-foreground"
          )}>
            {wsConnected ? (
              <><ShieldCheck className="w-3.5 h-3.5" /> SECURE</>
            ) : (
              <><ServerCrash className="w-3.5 h-3.5" /> DISCONNECTED</>
            )}
          </div>
        </div>

        <div className="w-px h-6 bg-border"></div>

        <div className="flex items-center gap-3 cursor-pointer group">
          <div className="text-right hidden md:block">
            <p className="text-sm font-medium text-foreground group-hover:text-primary transition-colors">Commander Admin</p>
            <p className="text-xs text-muted-foreground">Executive Level</p>
          </div>
          <div className="w-9 h-9 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-primary shadow-sm">
            <UserCircle className="w-5 h-5" />
          </div>
        </div>
      </div>
    </header>
  );
}
