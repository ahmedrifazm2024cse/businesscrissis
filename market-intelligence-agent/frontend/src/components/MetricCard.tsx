import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  icon: React.ReactNode;
  colorScheme: 'red' | 'yellow' | 'green' | 'blue';
  trend?: number; // optional percentage change
}

const COLOR_MAP = {
  red:    { bg: 'kpi-card-red',    icon: 'bg-red-500/15 text-red-400',    bar: 'from-red-500 to-red-600',    glow: 'shadow-red-500/10',    border: 'border-red-500/15' },
  yellow: { bg: 'kpi-card-yellow', icon: 'bg-amber-500/15 text-amber-400', bar: 'from-amber-400 to-orange-500', glow: 'shadow-amber-500/10', border: 'border-amber-500/15' },
  green:  { bg: 'kpi-card-green',  icon: 'bg-emerald-500/15 text-emerald-400', bar: 'from-emerald-500 to-teal-400', glow: 'shadow-emerald-500/10', border: 'border-emerald-500/15' },
  blue:   { bg: 'kpi-card-blue',   icon: 'bg-brand-500/15 text-brand-400', bar: 'from-brand-500 to-violet-500', glow: 'shadow-brand-500/10', border: 'border-brand-500/15' },
};

export const MetricCard: React.FC<MetricCardProps> = ({ title, value, subtitle, icon, colorScheme, trend }) => {
  const c = COLOR_MAP[colorScheme];
  const numericValue = typeof value === 'number' ? value : null;
  const barWidth = numericValue !== null ? Math.min(100, Math.max(0, numericValue)) : null;

  return (
    <div className={`relative rounded-2xl border ${c.border} p-6 overflow-hidden transition-all duration-300 hover:scale-[1.02] hover:shadow-xl ${c.glow} animate-slide-in-up group`}
         style={{ background: 'rgba(10,18,35,0.85)' }}>
      {/* Background gradient accent */}
      <div className={`kpi-accent absolute inset-0 ${c.bg}`} />

      {/* Content */}
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-2.5 rounded-xl ${c.icon}`}>
            {icon}
          </div>
          {trend !== undefined && (
            <span className={`text-[11px] font-bold px-2 py-1 rounded-lg ${trend >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
              {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
            </span>
          )}
        </div>

        <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest mb-1">{title}</p>
        
        <div className="flex items-end gap-2 mb-1">
          <span className="text-3xl font-extrabold text-white leading-none tracking-tight">
            {value}
          </span>
          {numericValue !== null && (
            <span className="text-sm text-slate-500 mb-0.5 font-medium">/100</span>
          )}
        </div>

        <p className="text-xs text-slate-600 mb-3">{subtitle}</p>

        {/* Score bar */}
        {barWidth !== null && (
          <div className="metric-bar">
            <div
              className={`metric-bar-fill bg-gradient-to-r ${c.bar}`}
              style={{ width: `${barWidth}%` }}
            />
          </div>
        )}
      </div>

      {/* Subtle corner glow on hover */}
      <div className="absolute top-0 right-0 w-32 h-32 rounded-full opacity-0 group-hover:opacity-10 transition-opacity duration-500"
           style={{ background: `radial-gradient(circle, rgba(var(--kpi-color), 1) 0%, transparent 70%)`,
                    transform: 'translate(30%, -30%)' }} />
    </div>
  );
};
