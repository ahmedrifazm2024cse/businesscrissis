import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  AlertTriangle, 
  FileBarChart, 
  MessageSquare,
  Settings,
  Bell,
  Shield,
  FileText
} from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
  { icon: Users, label: 'Agents Workspace', href: '/dashboard/agents' },
  { icon: AlertTriangle, label: 'Crisis Center', href: '/dashboard/crisis' },
  { icon: Shield, label: 'Admin Panel', href: '/dashboard/admin' },
  { icon: FileBarChart, label: 'Analytics', href: '/dashboard/analytics' },
  { icon: FileText, label: 'Reports', href: '/dashboard/reports' },
  { icon: MessageSquare, label: 'AI Chat', href: '/dashboard/chat' },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 border-r border-border bg-card flex flex-col">
      <div className="p-6">
        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-300 flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center border border-primary/50 shadow-[0_0_15px_rgba(37,99,235,0.2)]">
            <LayoutDashboard className="w-4 h-4 text-primary" />
          </div>
          Commander AI
        </h1>
      </div>

      <nav className="flex-1 px-4 space-y-2 mt-4">
        {navItems.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.href}
              to={item.href}
              className={clsx(
                'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200',
                isActive 
                  ? 'bg-primary/10 text-primary border border-primary/20 shadow-sm' 
                  : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
              )}
            >
              <item.icon className={clsx("w-5 h-5", isActive ? "text-primary" : "text-muted-foreground")} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border space-y-2">
        <Link to="/dashboard/notifications" className="w-full flex items-center gap-3 px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
          <Bell className="w-4 h-4" /> Notifications
        </Link>
        <Link to="/dashboard/settings" className="w-full flex items-center gap-3 px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
          <Settings className="w-4 h-4" /> Settings
        </Link>
      </div>
    </aside>
  );
}
