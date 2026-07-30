import { Server, Activity, HardDrive, Cpu, CheckCircle2 } from 'lucide-react';
import { RiskBadge } from '../components/common/RiskBadge';

const mockAgents = [
  { id: '1', name: 'Executive Decision', type: 'Executive', status: 'Running', latency: '45ms', cpu: '12%', mem: '1.2GB', task: 'Aggregating Risk Scores' },
  { id: '2', name: 'Workflow Manager', type: 'Executive', status: 'Running', latency: '22ms', cpu: '8%', mem: '400MB', task: 'Orchestrating DAG' },
  { id: '3', name: 'Customer Reputation', type: 'Business', status: 'Idle', latency: '15ms', cpu: '1%', mem: '250MB', task: 'Waiting for trigger' },
  { id: '4', name: 'Market Intelligence', type: 'Business', status: 'Running', latency: '120ms', cpu: '45%', mem: '2.1GB', task: 'Scraping competitor pricing' },
  { id: '5', name: 'Cyber Security', type: 'Business', status: 'Offline', latency: '-', cpu: '0%', mem: '0MB', task: 'Disconnected' },
];

export function AgentMonitor() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Agent Monitor</h1>
          <p className="text-slate-500 text-sm mt-1">Real-time health and execution metrics for all 13 AI agents.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg"><Server className="w-6 h-6" /></div>
          <div><p className="text-sm text-slate-500">Total Agents</p><p className="text-xl font-bold text-slate-900 dark:text-white">13</p></div>
        </div>
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg"><Activity className="w-6 h-6" /></div>
          <div><p className="text-sm text-slate-500">Active (Running)</p><p className="text-xl font-bold text-slate-900 dark:text-white">4</p></div>
        </div>
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg"><Server className="w-6 h-6" /></div>
          <div><p className="text-sm text-slate-500">Offline</p><p className="text-xl font-bold text-slate-900 dark:text-white">1</p></div>
        </div>
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg"><CheckCircle2 className="w-6 h-6" /></div>
          <div><p className="text-sm text-slate-500">Avg Success Rate</p><p className="text-xl font-bold text-slate-900 dark:text-white">98.2%</p></div>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 uppercase text-xs font-semibold">
              <tr>
                <th className="px-6 py-4">Agent Name</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Task</th>
                <th className="px-6 py-4">Latency</th>
                <th className="px-6 py-4">CPU / Mem</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {mockAgents.map((agent) => (
                <tr key={agent.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-900 dark:text-white flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      agent.status === 'Running' ? 'bg-blue-500 animate-pulse' : 
                      agent.status === 'Idle' ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    {agent.name}
                  </td>
                  <td className="px-6 py-4 text-slate-600 dark:text-slate-400">{agent.type}</td>
                  <td className="px-6 py-4">
                    <RiskBadge level={agent.status === 'Offline' ? 'CRITICAL' : agent.status === 'Running' ? 'NORMAL' : 'LOW'} />
                  </td>
                  <td className="px-6 py-4 text-slate-600 dark:text-slate-400 max-w-xs truncate">{agent.task}</td>
                  <td className="px-6 py-4 text-slate-600 dark:text-slate-400 font-mono">{agent.latency}</td>
                  <td className="px-6 py-4 text-slate-600 dark:text-slate-400 font-mono text-xs">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-1"><Cpu className="w-3 h-3"/> {agent.cpu}</div>
                      <div className="flex items-center gap-1"><HardDrive className="w-3 h-3"/> {agent.mem}</div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
