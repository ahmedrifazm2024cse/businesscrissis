import { Link } from 'react-router-dom';
import { ArrowRight, Shield, Cpu, Zap, Globe, Layers, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden">
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
            <div className="w-8 h-8 rounded-lg bg-primary/20 border border-primary flex items-center justify-center text-primary shadow-[0_0_15px_rgba(37,99,235,0.4)]">
              <Shield className="w-5 h-5" />
            </div>
            Commander <span className="text-primary">AI</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
            <a href="#features" className="hover:text-foreground transition-colors">Features</a>
            <a href="#architecture" className="hover:text-foreground transition-colors">Architecture</a>
            <a href="#agents" className="hover:text-foreground transition-colors">13 Agents</a>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/dashboard" className="bg-primary hover:bg-primary/90 text-primary-foreground px-5 py-2 rounded-full text-sm font-medium transition-all shadow-[0_0_15px_rgba(37,99,235,0.3)] flex items-center gap-2">
              Launch Platform <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/10 rounded-full blur-[120px] pointer-events-none"></div>
        
        <div className="max-w-7xl mx-auto px-6 relative z-10 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary/50 border border-border text-xs font-medium text-primary mb-8 shadow-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              Agentverse 2.0 is Live
            </div>
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-foreground via-foreground to-muted-foreground">
              Autonomous Business <br className="hidden md:block" />
              <span className="text-primary">Crisis Commander</span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-10 leading-relaxed">
              An enterprise-grade multi-agent orchestration platform. Deploy 13 specialized AI agents to analyze, predict, and mitigate global business disruptions in real-time.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/dashboard" className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-4 rounded-full text-base font-semibold transition-all shadow-[0_0_25px_rgba(37,99,235,0.4)] flex items-center gap-2 w-full sm:w-auto justify-center">
                Access Command Center <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Overview */}
      <section id="features" className="py-20 bg-secondary/20 border-y border-border">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4">Enterprise Capabilities</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">Built for scale, security, and instantaneous executive decision-making.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-card border border-border p-8 rounded-2xl">
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary mb-6">
                <Network className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-3">Multi-Agent Orchestration</h3>
              <p className="text-muted-foreground leading-relaxed">Dynamic DAG execution routing complex crisis workflows across specialized departmental AI agents automatically.</p>
            </div>
            <div className="bg-card border border-border p-8 rounded-2xl">
              <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center text-emerald-500 mb-6">
                <Activity className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-3">Real-Time Telemetry</h3>
              <p className="text-muted-foreground leading-relaxed">WebSockets stream live execution state, CPU, memory, and operational logs directly to the command dashboard.</p>
            </div>
            <div className="bg-card border border-border p-8 rounded-2xl">
              <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center text-amber-500 mb-6">
                <Shield className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-3">Executive Decision Engine</h3>
              <p className="text-muted-foreground leading-relaxed">Aggregates output from all 13 agents to form a cohesive, data-backed strategic recommendation matrix.</p>
            </div>
          </div>
        </div>
      </section>

      <footer className="bg-card border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-6 text-center text-muted-foreground text-sm">
          <p>© 2026 Autonomous Business Commander AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

// Inline Icon to avoid extra imports for this simple component
function Network(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="16" y="16" width="6" height="6" rx="1" />
      <rect x="2" y="16" width="6" height="6" rx="1" />
      <rect x="9" y="2" width="6" height="6" rx="1" />
      <path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3" />
      <path d="M12 12V8" />
    </svg>
  );
}
