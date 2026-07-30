import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, Users2, BarChart3, TrendingUp, ShieldAlert, FileText, Sun, Moon, 
  Menu, X, Brain, Terminal, Zap, ChevronRight
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [darkMode, setDarkMode] = useState<boolean>(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    const root = window.document.documentElement;
    if (darkMode) { root.classList.add('dark'); } 
    else { root.classList.remove('dark'); }
  }, [darkMode]);

  useEffect(() => {
    const tick = () => setLastUpdate(new Date().toLocaleTimeString('en-US', { hour12: false }));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const navItems = [
    { name: 'Dashboard',          path: '/',            icon: <LayoutDashboard className="w-4.5 h-4.5" />, badge: null },
    { name: 'Competitor Analysis',path: '/competitors', icon: <Users2 className="w-4.5 h-4.5" />,         badge: null },
    { name: 'Market Trends',      path: '/trends',      icon: <TrendingUp className="w-4.5 h-4.5" />,     badge: null },
    { name: 'Demand Forecast',    path: '/forecast',    icon: <BarChart3 className="w-4.5 h-4.5" />,      badge: null },
    { name: 'Risk Analysis',      path: '/risk',        icon: <ShieldAlert className="w-4.5 h-4.5" />,    badge: 'LIVE' },
    { name: 'Reports',            path: '/reports',     icon: <FileText className="w-4.5 h-4.5" />,       badge: null },
    { name: 'Crisis Commander',   path: '/crisis',      icon: <Terminal className="w-4.5 h-4.5" />,       badge: 'AI' },
  ];

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-[#070d1a] text-slate-800 dark:text-slate-100 transition-colors duration-300">
      
      {/* ── Desktop Sidebar ─────────────────────────────────────── */}
      <aside className="hidden lg:flex flex-col w-72 shrink-0 border-r border-slate-200/60 dark:border-slate-800/60"
             style={{ background: 'rgba(7,13,26,0.98)' }}>
        
        {/* Brand */}
        <div className="h-[72px] flex items-center gap-3.5 px-6 border-b border-slate-800/80">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center shadow-lg shadow-brand-500/30">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-500 border-2 border-[#070d1a] animate-pulse" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight gradient-text-brand">Crisis Commander</h1>
            <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mt-0.5">Market Intelligence</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-5 space-y-0.5 overflow-y-auto">
          <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest px-3 mb-3">Navigation</p>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'nav-active text-brand-300 font-semibold'
                    : 'text-slate-500 hover:bg-slate-800/60 hover:text-slate-200'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <span className={`transition-colors duration-150 ${isActive ? 'text-brand-400' : 'text-slate-600 group-hover:text-slate-300'}`}>
                    {item.icon}
                  </span>
                  <span className="flex-1">{item.name}</span>
                  {item.badge && (
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider ${
                      item.badge === 'LIVE' 
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20' 
                        : 'bg-brand-500/15 text-brand-400 border border-brand-500/20'
                    }`}>{item.badge}</span>
                  )}
                  {isActive && <ChevronRight className="w-3 h-3 text-brand-500 shrink-0" />}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* System Status */}
        <div className="mx-3 mb-3 p-3 rounded-xl border border-slate-800/80 bg-slate-900/30">
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">System</span>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
              <span className="text-[10px] text-emerald-400 font-semibold">Online</span>
            </div>
          </div>
          <div className="space-y-1.5 font-terminal text-[10px] text-slate-500">
            <div className="flex justify-between">
              <span>Agent Status</span>
              <span className="text-emerald-400 font-semibold">Active</span>
            </div>
            <div className="flex justify-between">
              <span>API Engine</span>
              <span className="text-brand-400">Rule-Based</span>
            </div>
            <div className="flex justify-between">
              <span>Clock</span>
              <span className="text-slate-400">{lastUpdate}</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-4 border-t border-slate-800/60 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-3.5 h-3.5 text-brand-500" />
            <span className="text-xs font-semibold text-slate-500">MI-Agent v1.0</span>
          </div>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-lg border border-slate-800 hover:bg-slate-800 text-slate-500 hover:text-slate-300 transition-colors"
          >
            {darkMode ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
          </button>
        </div>
      </aside>

      {/* ── Mobile Top Bar ───────────────────────────────────────── */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-14 border-b border-slate-800/60 px-5 flex items-center justify-between z-30"
           style={{ background: 'rgba(7,13,26,0.97)', backdropFilter: 'blur(12px)' }}>
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center">
            <Brain className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-sm gradient-text-brand">Crisis Commander</span>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setDarkMode(!darkMode)} className="p-2 text-slate-400">
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
          <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="p-2 text-slate-300">
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* ── Mobile Drawer ────────────────────────────────────────── */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 top-14 z-20" onClick={() => setMobileMenuOpen(false)}>
          <div className="absolute inset-x-0 top-0 border-b border-slate-800/60 px-3 py-4 space-y-0.5"
               style={{ background: 'rgba(7,13,26,0.98)' }}
               onClick={(e) => e.stopPropagation()}>
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition-all ${
                    isActive ? 'nav-active text-brand-300' : 'text-slate-400 hover:bg-slate-800/60'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <span className={isActive ? 'text-brand-400' : 'text-slate-600'}>{item.icon}</span>
                    <span>{item.name}</span>
                    {item.badge && (
                      <span className={`ml-auto text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                        item.badge === 'LIVE' 
                          ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20' 
                          : 'bg-brand-500/15 text-brand-400 border border-brand-500/20'
                      }`}>{item.badge}</span>
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </div>
        </div>
      )}

      {/* ── Main Content ─────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col min-w-0 pt-14 lg:pt-0 overflow-y-auto">
        {/* Top Status Bar */}
        <header className="hidden lg:flex h-[72px] items-center justify-between px-8 border-b border-slate-800/40"
                style={{ background: 'rgba(7,13,26,0.6)', backdropFilter: 'blur(12px)' }}>
          <div className="flex items-center gap-3">
            <div className="live-badge">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              Live Monitor
            </div>
            <span className="text-xs font-semibold text-slate-500">Market Intelligence Agent Active</span>
          </div>
          <div className="flex items-center gap-6 text-[11px] font-semibold font-terminal">
            <span className="text-slate-600">REF: MI-A1</span>
            <span className="text-slate-600">|</span>
            <span className="text-brand-500">API: localhost:8000</span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400">{lastUpdate}</span>
          </div>
        </header>

        {/* Page content */}
        <div className="flex-1 p-5 md:p-8 max-w-[1440px] w-full mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};
