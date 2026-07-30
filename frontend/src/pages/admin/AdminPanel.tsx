import { useState } from 'react';
import { Shield, Users, Database, Activity, Lock, Search, MoreHorizontal, Edit, Trash2, CheckCircle, XCircle } from 'lucide-react';
import clsx from 'clsx';

const mockUsers = [
  { id: 'USR-001', name: 'Alice Smith', email: 'alice@agentverse.ai', role: 'Super Admin', status: 'Active', lastActive: '2 mins ago' },
  { id: 'USR-002', name: 'Bob Jones', email: 'bob@agentverse.ai', role: 'Analyst', status: 'Active', lastActive: '1 hr ago' },
  { id: 'USR-003', name: 'Charlie Day', email: 'charlie@agentverse.ai', role: 'Viewer', status: 'Inactive', lastActive: '2 days ago' },
  { id: 'USR-004', name: 'Diana Prince', email: 'diana@agentverse.ai', role: 'Manager', status: 'Active', lastActive: '5 mins ago' },
];

export function AdminPanel() {
  const [activeTab, setActiveTab] = useState<'users' | 'system'>('users');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end border-b border-border pb-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight flex items-center gap-3">
            <Shield className="w-8 h-8 text-primary" />
            Administration
          </h1>
          <p className="text-muted-foreground mt-1">Manage users, roles, and system-wide configurations.</p>
        </div>
        <div className="flex bg-secondary/50 p-1 rounded-lg border border-border">
          <button 
            onClick={() => setActiveTab('users')}
            className={clsx("px-4 py-2 rounded-md text-sm font-medium transition-colors", activeTab === 'users' ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground")}
          >
            User Management
          </button>
          <button 
            onClick={() => setActiveTab('system')}
            className={clsx("px-4 py-2 rounded-md text-sm font-medium transition-colors", activeTab === 'system' ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground")}
          >
            System Health
          </button>
        </div>
      </div>

      {activeTab === 'users' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div className="relative w-72">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input 
                type="text" 
                placeholder="Search users..." 
                className="w-full bg-card border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-foreground placeholder:text-muted-foreground"
              />
            </div>
            <button className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm">
              Add User
            </button>
          </div>

          <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-secondary/40 border-b border-border text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                    <th className="p-4">User</th>
                    <th className="p-4">Role</th>
                    <th className="p-4">Status</th>
                    <th className="p-4">Last Active</th>
                    <th className="p-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {mockUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-secondary/20 transition-colors">
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-xs border border-primary/20">
                            {user.name.charAt(0)}
                          </div>
                          <div>
                            <p className="font-medium text-foreground text-sm">{user.name}</p>
                            <p className="text-xs text-muted-foreground">{user.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="p-4">
                        <span className="flex items-center gap-1.5 text-sm text-foreground">
                          {user.role === 'Super Admin' && <Lock className="w-3.5 h-3.5 text-amber-500" />}
                          {user.role}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className={clsx(
                          "px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border flex items-center gap-1 w-fit",
                          user.status === 'Active' ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20" : "bg-muted text-muted-foreground border-border"
                        )}>
                          {user.status === 'Active' ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                          {user.status}
                        </span>
                      </td>
                      <td className="p-4 text-sm text-muted-foreground">{user.lastActive}</td>
                      <td className="p-4 flex items-center justify-end gap-2">
                        <button className="p-1.5 text-muted-foreground hover:text-primary transition-colors"><Edit className="w-4 h-4" /></button>
                        <button className="p-1.5 text-muted-foreground hover:text-destructive transition-colors"><Trash2 className="w-4 h-4" /></button>
                        <button className="p-1.5 text-muted-foreground hover:text-foreground transition-colors"><MoreHorizontal className="w-4 h-4" /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'system' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl space-y-4">
            <div className="flex items-center gap-3 text-emerald-500">
              <Activity className="w-6 h-6" />
              <h3 className="font-bold text-foreground text-lg">Backend API</h3>
            </div>
            <p className="text-3xl font-light text-foreground">99.9% <span className="text-sm text-muted-foreground font-normal">Uptime</span></p>
            <p className="text-xs text-muted-foreground">All systems operational.</p>
          </div>
          <div className="bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl space-y-4">
            <div className="flex items-center gap-3 text-primary">
              <Database className="w-6 h-6" />
              <h3 className="font-bold text-foreground text-lg">Database</h3>
            </div>
            <p className="text-3xl font-light text-foreground">42% <span className="text-sm text-muted-foreground font-normal">Capacity</span></p>
            <p className="text-xs text-muted-foreground">Connected to primary cluster.</p>
          </div>
          <div className="bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl space-y-4">
            <div className="flex items-center gap-3 text-amber-500">
              <Users className="w-6 h-6" />
              <h3 className="font-bold text-foreground text-lg">Agent Queue</h3>
            </div>
            <p className="text-3xl font-light text-foreground">12 <span className="text-sm text-muted-foreground font-normal">Tasks</span></p>
            <p className="text-xs text-muted-foreground">Normal processing load.</p>
          </div>
        </div>
      )}
    </div>
  );
}
