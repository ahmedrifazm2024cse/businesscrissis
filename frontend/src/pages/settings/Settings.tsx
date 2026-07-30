import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Save, User, Shield, BellRing, Monitor, LayoutDashboard } from 'lucide-react';

const settingsSchema = z.object({
  fullName: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  role: z.string(),
  theme: z.enum(['dark', 'light', 'system']),
  notifications: z.boolean(),
  twoFactor: z.boolean(),
  apiKey: z.string().optional(),
});

type SettingsFormValues = z.infer<typeof settingsSchema>;

export function Settings() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isDirty },
    reset,
  } = useForm<SettingsFormValues>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      fullName: 'Commander Admin',
      email: 'admin@agentverse.ai',
      role: 'Executive',
      theme: 'dark',
      notifications: true,
      twoFactor: true,
      apiKey: 'sk-live-***************************',
    }
  });

  const onSubmit = async (data: SettingsFormValues) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('Settings saved:', data);
    reset(data);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="border-b border-border pb-4">
        <h1 className="text-3xl font-bold text-foreground tracking-tight flex items-center gap-3">
          <Monitor className="w-8 h-8 text-primary" />
          Platform Settings
        </h1>
        <p className="text-muted-foreground mt-1">Manage your enterprise profile, security, and orchestrator preferences.</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        
        {/* Profile Section */}
        <div className="bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl">
          <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2 border-b border-border pb-2">
            <User className="w-5 h-5 text-primary" /> Profile Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Full Name</label>
              <input 
                {...register('fullName')}
                className="w-full bg-secondary/50 border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-foreground"
              />
              {errors.fullName && <p className="text-xs text-destructive">{errors.fullName.message}</p>}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Email Address</label>
              <input 
                {...register('email')}
                className="w-full bg-secondary/50 border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-foreground"
              />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>
          </div>
        </div>

        {/* Security Section */}
        <div className="bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl">
          <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2 border-b border-border pb-2">
            <Shield className="w-5 h-5 text-primary" /> Security & Access
          </h2>
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-foreground">Two-Factor Authentication (2FA)</p>
                <p className="text-sm text-muted-foreground">Require a security key or authenticator app during login.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" {...register('twoFactor')} className="sr-only peer" />
                <div className="w-11 h-6 bg-secondary peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Commander API Key</label>
              <div className="flex gap-2">
                <input 
                  type="password"
                  {...register('apiKey')}
                  className="w-full bg-secondary/50 border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-foreground font-mono"
                />
                <button type="button" className="bg-secondary hover:bg-secondary/80 text-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-border whitespace-nowrap">
                  Rotate Key
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Preferences Section */}
        <div className="bg-card/50 backdrop-blur-sm border border-border p-6 rounded-xl">
          <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2 border-b border-border pb-2">
            <LayoutDashboard className="w-5 h-5 text-primary" /> Workspace Preferences
          </h2>
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-foreground">Push Notifications</p>
                <p className="text-sm text-muted-foreground">Receive real-time alerts for agent workflows and crisis events.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" {...register('notifications')} className="sr-only peer" />
                <div className="w-11 h-6 bg-secondary peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">UI Theme</label>
              <select 
                {...register('theme')}
                className="w-full bg-secondary/50 border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-foreground"
              >
                <option value="dark">Enterprise Dark (Recommended)</option>
                <option value="light">Light Mode</option>
                <option value="system">System Default</option>
              </select>
            </div>
          </div>
        </div>

        <div className="flex justify-end pt-4">
          <button 
            type="submit" 
            disabled={!isDirty || isSubmitting}
            className="bg-primary hover:bg-primary/90 disabled:bg-primary/50 disabled:cursor-not-allowed text-primary-foreground px-6 py-2.5 rounded-lg text-sm font-medium transition-all shadow-[0_0_15px_rgba(37,99,235,0.3)] flex items-center gap-2"
          >
            {isSubmitting ? (
              <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></span>
            ) : (
              <Save className="w-4 h-4" />
            )}
            {isSubmitting ? 'Saving Changes...' : 'Save Settings'}
          </button>
        </div>
      </form>
    </div>
  );
}
