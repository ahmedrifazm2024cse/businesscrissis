import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingUp, BarChart3, Activity } from 'lucide-react';

const revenueData = [
  { month: 'Jan', revenue: 4000, projected: 4400 },
  { month: 'Feb', revenue: 3000, projected: 3200 },
  { month: 'Mar', revenue: 2000, projected: 2500 },
  { month: 'Apr', revenue: 2780, projected: 3000 },
  { month: 'May', revenue: 1890, projected: 2100 },
  { month: 'Jun', revenue: 2390, projected: 2800 },
  { month: 'Jul', revenue: 3490, projected: 3800 },
];

const sentimentData = [
  { day: 'Mon', positive: 65, neutral: 20, negative: 15 },
  { day: 'Tue', positive: 59, neutral: 25, negative: 16 },
  { day: 'Wed', positive: 80, neutral: 15, negative: 5 },
  { day: 'Thu', positive: 81, neutral: 10, negative: 9 },
  { day: 'Fri', positive: 56, neutral: 30, negative: 14 },
  { day: 'Sat', positive: 55, neutral: 35, negative: 10 },
  { day: 'Sun', positive: 40, neutral: 40, negative: 20 },
];

const threatData = [
  { time: '00:00', score: 20 },
  { time: '04:00', score: 35 },
  { time: '08:00', score: 85 },
  { time: '12:00', score: 45 },
  { time: '16:00', score: 30 },
  { time: '20:00', score: 25 },
];

export function Analytics() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end border-b border-border pb-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-primary" />
            Platform Analytics
          </h1>
          <p className="text-muted-foreground mt-1">Deep-dive visualizations of business health, market sentiment, and threat vectors.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Impact Chart */}
        <div className="bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl">
          <h3 className="text-lg font-bold text-foreground mb-6 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-500" /> Revenue & Projections
          </h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={revenueData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" opacity={0.5} />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} />
                <Tooltip contentStyle={{ backgroundColor: '#09090b', borderColor: '#1e293b', color: '#fff', borderRadius: '8px' }} />
                <Legend iconType="circle" />
                <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6', strokeWidth: 0 }} activeDot={{ r: 6 }} name="Actual Revenue (k$)" />
                <Line type="monotone" dataKey="projected" stroke="#94a3b8" strokeDasharray="5 5" strokeWidth={2} dot={false} name="Projected (k$)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Customer Sentiment Chart */}
        <div className="bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl">
          <h3 className="text-lg font-bold text-foreground mb-6 flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary" /> Customer Sentiment Index
          </h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sentimentData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" opacity={0.5} />
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} />
                <Tooltip contentStyle={{ backgroundColor: '#09090b', borderColor: '#1e293b', color: '#fff', borderRadius: '8px' }} cursor={{ fill: '#1e293b', opacity: 0.4 }} />
                <Legend iconType="circle" />
                <Bar dataKey="positive" stackId="a" fill="#10b981" name="Positive" radius={[0, 0, 4, 4]} />
                <Bar dataKey="neutral" stackId="a" fill="#64748b" name="Neutral" />
                <Bar dataKey="negative" stackId="a" fill="#ef4444" name="Negative" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Threat Level Chart */}
        <div className="lg:col-span-2 bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl">
          <h3 className="text-lg font-bold text-foreground mb-6 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-destructive" /> Threat Score Trajectory
          </h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={threatData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.5}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" opacity={0.5} />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} />
                <Tooltip contentStyle={{ backgroundColor: '#09090b', borderColor: '#1e293b', color: '#fff', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="score" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#colorScore)" name="Threat Score" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
