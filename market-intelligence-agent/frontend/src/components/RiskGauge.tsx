import React from 'react';

interface RiskGaugeProps {
  score: number;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ score }) => {
  const needleRotation = -90 + (score / 100) * 180;

  const getRiskLabel = (s: number) => {
    if (s > 75) return { text: 'Critical Threat', color: 'text-red-400', glow: 'shadow-red-500/30' };
    if (s > 50) return { text: 'Elevated Risk',   color: 'text-amber-400', glow: 'shadow-amber-500/30' };
    if (s > 25) return { text: 'Moderate Risk',   color: 'text-yellow-400', glow: 'shadow-yellow-500/30' };
    return { text: 'Low Threat', color: 'text-emerald-400', glow: 'shadow-emerald-500/30' };
  };

  const info = getRiskLabel(score);

  return (
    <div className="flex flex-col items-center justify-center p-6 rounded-2xl border border-slate-800/60 h-full"
         style={{ background: 'rgba(10,18,35,0.85)' }}>
      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest self-start mb-5 font-terminal">
        Risk Gauge
      </p>

      <div className="relative w-64 h-36 flex items-center justify-center">
        <svg className="w-full h-full" viewBox="0 0 100 50">
          <defs>
            <linearGradient id="gaugeGradientPremium" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%"   stopColor="#10b981" />
              <stop offset="40%"  stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#ef4444" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="1.5" result="blur" />
              <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>

          {/* Track */}
          <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="rgba(30,41,59,0.8)" strokeWidth="8" strokeLinecap="round" />

          {/* Colored arc */}
          <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="url(#gaugeGradientPremium)" strokeWidth="8" strokeLinecap="round" filter="url(#glow)" opacity="0.85" />

          {/* Tick marks */}
          {[0, 25, 50, 75, 100].map((pct) => {
            const angle = -180 + (pct / 100) * 180;
            const rad = (angle * Math.PI) / 180;
            const cx = 50, cy = 50, r = 40;
            const x1 = cx + r * Math.cos(rad);
            const y1 = cy + r * Math.sin(rad);
            const x2 = cx + (r - 6) * Math.cos(rad);
            const y2 = cy + (r - 6) * Math.sin(rad);
            return <line key={pct} x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(100,116,139,0.5)" strokeWidth="1.5" />;
          })}
        </svg>

        {/* Needle */}
        <div
          className="absolute w-1.5 bg-white rounded-full origin-bottom transition-transform duration-1000 ease-out shadow-lg"
          style={{
            height: '36px',
            bottom: '4px',
            left: 'calc(50% - 3px)',
            transform: `rotate(${needleRotation}deg)`,
            transformOrigin: 'bottom center',
            boxShadow: '0 0 8px rgba(255,255,255,0.4)',
          }}
        />
        {/* Needle pin */}
        <div className="absolute w-4 h-4 rounded-full bg-gradient-to-br from-brand-400 to-violet-500 border-2 border-slate-900 shadow-lg"
             style={{ bottom: '-4px', left: 'calc(50% - 8px)' }} />
      </div>

      <div className="text-center mt-5">
        <div className="flex items-end justify-center gap-1">
          <span className={`text-5xl font-extrabold tracking-tight ${info.color}`}>{score}</span>
          <span className="text-slate-500 text-lg font-medium mb-1">/100</span>
        </div>
        <p className={`text-sm font-bold mt-1.5 ${info.color}`}>{info.text}</p>
        <div className="mt-3 h-1 w-32 mx-auto rounded-full bg-slate-800 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${score}%`,
              background: score > 75 ? '#ef4444' : score > 50 ? '#f59e0b' : score > 25 ? '#eab308' : '#10b981'
            }}
          />
        </div>
      </div>
    </div>
  );
};
