/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Exact spec colors
        primary:   '#0B1220',
        secondary: '#111827',
        card:      '#1F2937',
        accent:    '#3B82F6',
        success:   '#22C55E',
        warning:   '#F59E0B',
        critical:  '#EF4444',

        brand: {
          50:  '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        surface: {
          0:   '#0B1220',
          1:   '#111827',
          2:   '#1F2937',
          3:   '#374151',
          4:   '#4B5563',
        },
        neon: {
          blue:   '#3B82F6',
          green:  '#22C55E',
          amber:  '#F59E0B',
          red:    '#EF4444',
          violet: '#8B5CF6',
          cyan:   '#06B6D4',
        },
        violet: {
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
        },
        emerald: {
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
        },
      },
      fontFamily: {
        sans:     ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono:     ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
        display:  ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'glow-pulse':       'glow-pulse 2s ease-in-out infinite',
        'float':            'float 3s ease-in-out infinite',
        'shimmer':          'shimmer 2s linear infinite',
        'slide-in-up':      'slide-in-up 0.4s ease-out',
        'slide-in-right':   'slide-in-right 0.35s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-in-left':    'slide-in-left 0.35s cubic-bezier(0.16, 1, 0.3, 1)',
        'fade-in':          'fade-in 0.3s ease-out',
        'fade-in-scale':    'fade-in-scale 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'scan-line':        'scan-line 3s linear infinite',
        'counter-up':       'counter-up 0.8s ease-out',
        'border-glow':      'border-glow 2s ease-in-out infinite',
        'spin-slow':        'spin 3s linear infinite',
        'ping-slow':        'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
        'status-pulse':     'status-pulse 2s ease-in-out infinite',
        'notification-in':  'notification-in 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 5px rgba(59,130,246,0.3), 0 0 20px rgba(59,130,246,0.1)' },
          '50%':       { boxShadow: '0 0 15px rgba(59,130,246,0.6), 0 0 40px rgba(59,130,246,0.2)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':       { transform: 'translateY(-4px)' },
        },
        'shimmer': {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'slide-in-up': {
          '0%':   { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-right': {
          '0%':   { opacity: '0', transform: 'translateX(100%)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'slide-in-left': {
          '0%':   { opacity: '0', transform: 'translateX(-100%)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'fade-in': {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-in-scale': {
          '0%':   { opacity: '0', transform: 'scale(0.92)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'scan-line': {
          '0%':   { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(500%)' },
        },
        'counter-up': {
          '0%':   { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'border-glow': {
          '0%, 100%': { borderColor: 'rgba(59,130,246,0.3)' },
          '50%':       { borderColor: 'rgba(59,130,246,0.8)' },
        },
        'status-pulse': {
          '0%, 100%': { opacity: '1' },
          '50%':       { opacity: '0.4' },
        },
        'notification-in': {
          '0%':   { opacity: '0', transform: 'translateX(calc(100% + 1rem))' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
      backdropBlur: {
        xs: '2px',
        '2xl': '40px',
      },
      boxShadow: {
        'glow-blue':    '0 0 20px rgba(59,130,246,0.25)',
        'glow-green':   '0 0 20px rgba(34,197,94,0.25)',
        'glow-red':     '0 0 20px rgba(239,68,68,0.25)',
        'glow-amber':   '0 0 20px rgba(245,158,11,0.25)',
        'glow-violet':  '0 0 20px rgba(139,92,246,0.25)',
        'card':         '0 1px 3px rgba(0,0,0,0.3), 0 8px 32px rgba(0,0,0,0.2)',
        'card-hover':   '0 4px 16px rgba(0,0,0,0.4), 0 20px 64px rgba(0,0,0,0.3)',
        'panel':        '0 8px 32px rgba(0,0,0,0.5), 0 32px 64px rgba(0,0,0,0.3)',
        'inner-glow':   'inset 0 1px 0 rgba(255,255,255,0.06)',
        'sidebar':      '4px 0 24px rgba(0,0,0,0.4)',
        'navbar':       '0 1px 0 rgba(255,255,255,0.05), 0 4px 24px rgba(0,0,0,0.3)',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
    },
  },
  plugins: [],
}
