import { Search, Bell, Sun, User, ChevronRight } from 'lucide-react';
import { useLocation } from 'react-router-dom';

export function Navbar() {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  return (
    <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 flex items-center px-6 justify-between sticky top-0 z-20">
      {/* Breadcrumbs */}
      <div className="flex items-center text-sm text-slate-500">
        <span className="capitalize">Agentverse</span>
        {pathnames.map((name, index) => {
          return (
            <div key={name} className="flex items-center">
              <ChevronRight className="w-4 h-4 mx-1" />
              <span className={`capitalize ${index === pathnames.length - 1 ? 'text-slate-900 dark:text-slate-100 font-medium' : ''}`}>
                {name.replace('-', ' ')}
              </span>
            </div>
          );
        })}
        {pathnames.length === 0 && (
          <>
            <ChevronRight className="w-4 h-4 mx-1" />
            <span className="text-slate-900 dark:text-slate-100 font-medium">Dashboard</span>
          </>
        )}
      </div>

      {/* Right Side Actions */}
      <div className="flex items-center gap-4">
        <div className="relative hidden md:block">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search agents, workflows..." 
            className="pl-9 pr-4 py-1.5 bg-slate-100 dark:bg-slate-900 border-none rounded-md text-sm focus:ring-2 focus:ring-blue-500 w-64 outline-none transition-all"
          />
        </div>
        
        <button className="p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full relative transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-white dark:border-slate-950"></span>
        </button>

        <button className="p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors">
          <Sun className="w-5 h-5" />
        </button>

        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white ml-2 cursor-pointer shadow-sm hover:shadow-md transition-shadow">
          <User className="w-4 h-4" />
        </div>
      </div>
    </header>
  );
}
