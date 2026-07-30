import React from 'react';

type BadgeVariant = 'critical' | 'warning' | 'success' | 'info' | 'neutral' | 'violet';
type BadgeSize = 'sm' | 'md';

interface BadgeProps {
  variant?: BadgeVariant;
  size?: BadgeSize;
  children: React.ReactNode;
  dot?: boolean;
  className?: string;
}

const VARIANT_CLASSES: Record<BadgeVariant, string> = {
  critical: 'badge-critical',
  warning:  'badge-warning',
  success:  'badge-success',
  info:     'badge-info',
  neutral:  'badge-neutral',
  violet:   'bg-violet-500/12 text-violet-300 border border-violet-500/25',
};

const SIZE_CLASSES: Record<BadgeSize, string> = {
  sm: 'text-[9px] px-1.5 py-0.5 rounded-md',
  md: 'text-[10px] px-2 py-0.5 rounded-lg',
};

export const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  size = 'md',
  children,
  dot = false,
  className = '',
}) => (
  <span
    className={`
      inline-flex items-center gap-1 font-bold tracking-wider uppercase
      font-terminal
      ${VARIANT_CLASSES[variant]}
      ${SIZE_CLASSES[size]}
      ${className}
    `}
  >
    {dot && (
      <span
        className="w-1.5 h-1.5 rounded-full shrink-0"
        style={{
          background: variant === 'critical' ? '#ef4444' :
                      variant === 'warning'  ? '#f59e0b' :
                      variant === 'success'  ? '#22c55e' :
                      variant === 'info'     ? '#3b82f6' :
                      variant === 'violet'   ? '#8b5cf6' :
                                               '#6b7280',
          boxShadow: `0 0 4px currentColor`,
        }}
      />
    )}
    {children}
  </span>
);
