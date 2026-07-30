import { useEffect, useState } from 'react';
import { useCommanderStore } from '../../store/useCommanderStore';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, ShieldAlert, TrendingDown, Users, Globe, Truck, CheckCircle2, ShieldCheck, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

const mockRiskData = [
  { time: '08:00', risk: 20 },
  { time: '09:00', risk: 35 },
  { time: '10:00', risk: 42 },
  { time: '11:00', risk: 85 },
  { time: '12:00', risk: 75 },
  { time: '13:00', risk: 60 },
  { time: '14:00', risk: 55 },
];

export function ExecutiveDashboard() {
  const { health, activeTasks, fetchHealth, fetchActiveTasks, declareCrisis, metrics, revenueChart, fetchDashboardData } = useCommanderStore();
  const [isDeclaring, setIsDeclaring] = useState(false);

  useEffect(() => {
    fetchHealth();
    fetchActiveTasks();
    fetchDashboardData();
    const interval = setInterval(() => {
      fetchHealth();
      fetchActiveTasks();
      fetchDashboardData();
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const statCards = [
    { title: 'Business Health', value: metrics ? `${metrics.businessHealth}%` : '...', icon: Activity, trend: 'Overall status', color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { title: 'Overall Risk Score', value: metrics ? `${metrics.overallRisk}/100` : '...', icon: ShieldAlert, trend: metrics?.threatLevel || 'Normal', color: 'text-red-500', bg: 'bg-red-500/10' },
    { title: 'Active Crises', value: metrics?.activeCrises ?? '...', icon: TrendingDown, trend: 'Needs attention', color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { title: 'Resolved Crises', value: metrics?.resolvedCrises ?? '...', icon: Users, trend: 'Completed', color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
    { title: 'Total Agents', value: metrics?.totalAgents ?? '...', icon: Globe, trend: 'Active', color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { title: 'AI Confidence', value: metrics ? `${metrics.aiConfidence}%` : '...', icon: ShieldCheck, trend: 'High', color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight">Executive Summary</h1>
          <p className="text-muted-foreground mt-1">Real-time enterprise metrics from the Commander AI.</p>
        </div>
        {health && (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-secondary/50 px-4 py-2 rounded-lg border border-border">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
              <span className="text-sm font-medium">Orchestrator {health.status}</span>
            </div>
            <button 
              onClick={async () => {
                setIsDeclaring(true);
                await declareCrisis("Global Supply Chain Disruption detected in APAC region");
                setIsDeclaring(false);
              }}
              disabled={isDeclaring}
              className="bg-destructive hover:bg-destructive/90 text-destructive-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 shadow-[0_0_15px_rgba(239,68,68,0.2)] disabled:opacity-50"
            >
              {isDeclaring ? 'Declaring...' : 'Declare Crisis'}
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {statCards.map((stat, i) => (
          <div key={i} className="bg-card/50 backdrop-blur-sm border border-border p-5 rounded-xl shadow-sm hover:border-primary/50 transition-colors group">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                <p className="text-2xl font-bold text-foreground mt-1">{stat.value}</p>
              </div>
              <div className={clsx("p-2 rounded-lg", stat.bg)}>
                <stat.icon className={clsx("w-5 h-5", stat.color)} />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-1.5 text-xs text-muted-foreground">
              {stat.trend === 'Critical' || stat.trend.includes('attention') ? (
                <TrendingDown className="w-3.5 h-3.5 text-red-400" />
              ) : (
                <Activity className="w-3.5 h-3.5 text-emerald-400" />
              )}
              {stat.trend}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-emerald-400" /> Revenue Trajectory
          </h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueChart || []}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" opacity={0.5} />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#09090b', borderColor: '#1e293b', color: '#fff', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorRisk)" name="Actual Revenue" />
                <Area type="monotone" dataKey="projected" stroke="#3b82f6" strokeWidth={2} strokeDasharray="5 5" fillOpacity={0} name="Projected" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6 flex flex-col">
          <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-primary" /> Active Orchestration
          </h3>
          <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
            {activeTasks.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center mt-10">No active tasks</p>
            ) : (
              activeTasks.map((task) => (
                <div key={task.id} className="p-3 rounded-lg border border-border bg-secondary/30 hover:bg-secondary/50 transition-colors">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-mono text-muted-foreground bg-secondary px-2 py-0.5 rounded text-[10px] truncate max-w-[150px]">{task.id}</span>
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                    </span>
                  </div>
                  <p className="text-sm text-foreground font-medium">{task.description}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
