import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Briefcase, 
  Activity, 
  Network, 
  FileText, 
  HeartPulse, 
  Settings,
  BrainCircuit,
  Database,
  Globe,
  DollarSign,
  Truck,
  ShieldAlert,
  Scale
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Home', icon: LayoutDashboard },
  { path: '/executive', label: 'Executive', icon: Briefcase },
  { path: '/system/workflow', label: 'Workflow', icon: Network },
  { path: '/system/monitor', label: 'Agents', icon: Activity },
  { path: '/system/memory', label: 'Memory', icon: Database },
  { path: '/reports', label: 'Reports', icon: FileText },
  { path: '/knowledge', label: 'Knowledge', icon: BrainCircuit },
];

const agentItems = [
  { path: '/agent/customer', label: 'Customer', icon: Globe },
  { path: '/agent/market', label: 'Market', icon: Globe },
  { path: '/agent/financial', label: 'Financial', icon: DollarSign },
  { path: '/agent/supply', label: 'Supply Chain', icon: Truck },
  { path: '/agent/cyber', label: 'Cyber Security', icon: ShieldAlert },
  { path: '/agent/legal', label: 'Legal', icon: Scale },
];

export function Sidebar() {
  return (
    <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 flex flex-col h-full overflow-y-auto">
      <div className="p-6">
        <div className="flex items-center gap-2 text-primary font-bold text-xl">
          <BrainCircuit className="w-6 h-6" />
          <span>Agentverse</span>
        </div>
      </div>
      
      <div className="px-4 py-2">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">Dashboards</p>
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                    isActive 
                      ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400 font-medium' 
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900 hover:text-slate-900 dark:hover:text-slate-50'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      <div className="px-4 py-4 mt-2 border-t border-slate-100 dark:border-slate-800/50">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">Business Agents</p>
        <nav className="flex flex-col gap-1">
          {agentItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                    isActive 
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-400 font-medium' 
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900 hover:text-slate-900 dark:hover:text-slate-50'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      <div className="mt-auto px-4 py-4 border-t border-slate-200 dark:border-slate-800">
        <nav className="flex flex-col gap-1">
          <NavLink to="/system/health" className="flex items-center gap-3 px-3 py-2 rounded-md text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors">
            <HeartPulse className="w-4 h-4" />
            <span className="text-sm">System Health</span>
          </NavLink>
          <NavLink to="/settings" className="flex items-center gap-3 px-3 py-2 rounded-md text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors">
            <Settings className="w-4 h-4" />
            <span className="text-sm">Settings</span>
          </NavLink>
        </nav>
      </div>
    </aside>
  );
}
