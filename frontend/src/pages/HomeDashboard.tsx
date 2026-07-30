import { useState, useEffect } from 'react';
import { AlertTriangle, Activity, CheckCircle, ShieldAlert } from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { CommanderAPI } from '../services/commanderAPI';

const mockChartData = [
  { time: '08:00', risk: 20 },
  { time: '09:00', risk: 35 },
  { time: '10:00', risk: 60 },
  { time: '11:00', risk: 85 },
  { time: '12:00', risk: 90 },
  { time: '13:00', risk: 75 },
  { time: '14:00', risk: 45 },
];

export function HomeDashboard() {
  const [tasks, setTasks] = useState<any[]>([]);

  useEffect(() => {
    CommanderAPI.getActiveTasks().then(data => {
      if (data && data.tasks) {
        setTasks(data.tasks);
      }
    });
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Home Dashboard</h1>
          <p className="text-slate-500 text-sm mt-1">Platform overview and real-time metrics.</p>
        </div>
        <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 shadow-sm transition-colors">
          <AlertTriangle className="w-4 h-4" />
          Declare Crisis
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Running Crises" value={1} icon={<AlertTriangle />} trend="up" trendValue="+1 today" />
        <StatCard title="Overall Risk Score" value="85/100" icon={<ShieldAlert />} trend="up" trendValue="High Risk" />
        <StatCard title="Business Health" value="72%" icon={<Activity />} trend="down" trendValue="-8% from baseline" />
        <StatCard title="AI Confidence" value="94%" icon={<CheckCircle />} trend="neutral" trendValue="Stable" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart Section */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-6">Risk Trend (Last 6 Hours)</h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockChartData}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.2} />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area type="monotone" dataKey="risk" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorRisk)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Activity Feed */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-6">Pending Tasks</h3>
          <div className="space-y-4">
            {tasks.map((task, i) => (
              <div key={task.id || i} className="flex gap-4 items-start p-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-lg transition-colors border border-slate-100 dark:border-slate-800">
                <div className="w-2 h-2 mt-2 bg-blue-500 rounded-full shrink-0"></div>
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-200">{task.description}</p>
                  <p className="text-xs text-slate-500 mt-1">Workflow ID: {task.id}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
