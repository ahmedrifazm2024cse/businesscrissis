import React from 'react';

interface ProgressBarProps {
  value: number;         // 0-100
  max?: number;
  label?: string;
  showValue?: boolean;
  height?: number;
  colorClass?: string;   // custom kpi CSS var class e.g. 'kpi-blue'
  animated?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  label,
  showValue = false,
  height = 3,
  colorClass = 'kpi-blue',
  animated = true,
  className = '',
}) => {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className={`w-full ${className}`}>
      {(label || showValue) && (
        <div className="flex items-center justify-between mb-1.5">
          {label && (
            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider font-terminal">
              {label}
            </span>
          )}
          {showValue && (
            <span className="text-[11px] font-bold text-slate-300 font-terminal">
              {value}{max !== 100 ? `/${max}` : '%'}
            </span>
          )}
        </div>
      )}
      <div
        className={`metric-bar ${colorClass}`}
        style={{ height: `${height}px` }}
      >
        <div
          className={`metric-bar-fill kpi-bar-fill ${colorClass} ${animated ? 'transition-all duration-[800ms] ease-out' : ''}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
};
