import { useState } from 'react';
import { Box, Typography, Card, CardContent, Button, Chip } from '@mui/material';
import { Play as PlayArrowIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import { CommanderAPI } from '../services/commanderAPI';
import { useNavigate } from 'react-router-dom';

const SCENARIOS = [
  { id: '1_cyber', name: 'Cyber Attack', color: 'error', icon: '🔒' },
  { id: '2_supply', name: 'Supply Chain Failure', color: 'warning', icon: '🚢' },
  { id: '3_customer', name: 'Customer Reputation Crisis', color: 'secondary', icon: '🗣️' },
  { id: '4_financial', name: 'Financial Loss', color: 'error', icon: '📉' },
  { id: '5_legal', name: 'Legal Compliance Violation', color: 'warning', icon: '⚖️' },
  { id: '6_market', name: 'Market Collapse', color: 'error', icon: '🏢' },
  { id: '7_multi_crisis', name: 'Combined Multi-Crisis Event', color: 'error', icon: '🔥' }
];

export default function PresentationMode() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const launchScenario = async (_id: string, name: string) => {
    setLoading(true);
    try {
      const res = await CommanderAPI.triggerCrisis(`Simulated Demo: ${name}`, "CRITICAL");
      if (res && res.workflow_id) {
        localStorage.setItem('active_workflow_id', res.workflow_id);
      }
      // Redirect to the DAG monitor so judges can watch it live
      setTimeout(() => {
        navigate('/workflow');
      }, 1000);
    } catch (error) {
      console.error("Failed to launch scenario", error);
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 4, height: '100%' }}>
      <Typography variant="h3" sx={{ fontWeight: 800, mb: 4, background: 'linear-gradient(45deg, #FF8E53 30%, #FE6B8B 90%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        Live Demonstration Mode
      </Typography>
      <Typography variant="h6" sx={{ color: 'text.secondary', mb: 6 }}>
        Select a predefined enterprise crisis to trigger a full multi-agent simulation.
      </Typography>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {SCENARIOS.map((scenario) => (
          <div key={scenario.id}>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Card sx={{ 
                height: '100%', 
                background: 'rgba(255, 255, 255, 0.05)', 
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}>
                <CardContent>
                  <Typography variant="h2" sx={{ mb: 2 }}>{scenario.icon}</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 1, color: 'white' }}>
                    {scenario.name}
                  </Typography>
                  <Chip label={scenario.color === 'error' ? 'Critical Impact' : 'High Impact'} color={scenario.color as any} size="small" />
                </CardContent>
                <Box sx={{ p: 2 }}>
                  <Button 
                    variant="contained" 
                    fullWidth 
                    size="large"
                    disabled={loading}
                    startIcon={<PlayArrowIcon />}
                    onClick={() => launchScenario(scenario.id, scenario.name)}
                    sx={{ 
                      background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                      color: 'white',
                      fontWeight: 'bold'
                    }}
                  >
                    Launch Crisis
                  </Button>
                </Box>
              </Card>
            </motion.div>
          </div>
        ))}
      </div>
    </Box>
  );
}
