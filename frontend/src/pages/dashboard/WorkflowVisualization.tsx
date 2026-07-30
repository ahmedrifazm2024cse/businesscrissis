import { useState, useCallback } from 'react';
import { 
  ReactFlow, 
  MiniMap, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  MarkerType,
  BackgroundVariant
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Network, Server } from 'lucide-react';

import { useCommanderStore } from '../../store/useCommanderStore';
import { useEffect } from 'react';

const initialNodes = [
  { id: 'Workflow Manager', position: { x: 400, y: 50 }, data: { label: 'Workflow Manager' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #2563eb', borderRadius: '8px' } },
  
  // Level 1
  { id: 'Customer Reputation', position: { x: 50, y: 150 }, data: { label: 'Customer Rep.' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
  { id: 'Market Intelligence', position: { x: 250, y: 150 }, data: { label: 'Market Intel' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
  { id: 'Cybersecurity', position: { x: 450, y: 150 }, data: { label: 'Cyber Sec.' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
  { id: 'Operations', position: { x: 650, y: 150 }, data: { label: 'Operations' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
  { id: 'HR', position: { x: 850, y: 150 }, data: { label: 'HR' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
  
  // Level 2
  { id: 'Legal & Compliance', position: { x: 250, y: 250 }, data: { label: 'Legal' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
  { id: 'Financial Risk', position: { x: 450, y: 250 }, data: { label: 'Financial' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
  { id: 'Supply Chain', position: { x: 650, y: 250 }, data: { label: 'Supply Chain' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },

  // Level 3,4,5,6,7
  { id: 'Predictive Analytics', position: { x: 450, y: 350 }, data: { label: 'Predictive Analytics' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
  { id: 'Strategy', position: { x: 450, y: 450 }, data: { label: 'Strategy' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
  { id: 'Executive Decision', position: { x: 450, y: 550 }, data: { label: 'Executive Decision' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
  { id: 'Communication & PR', position: { x: 250, y: 650 }, data: { label: 'Public Relations' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
  { id: 'Report Generator', position: { x: 650, y: 650 }, data: { label: 'Report Generator' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px' } },
];

const initialEdges = [
  // L1
  { id: 'e1-cr', source: 'Workflow Manager', target: 'Customer Reputation', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e1-mi', source: 'Workflow Manager', target: 'Market Intelligence', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e1-cs', source: 'Workflow Manager', target: 'Cybersecurity', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e1-op', source: 'Workflow Manager', target: 'Operations', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e1-hr', source: 'Workflow Manager', target: 'HR', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  
  // L2 dependencies (simplified visual flow)
  { id: 'e-cs-lc', source: 'Cybersecurity', target: 'Legal & Compliance', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e-mi-fr', source: 'Market Intelligence', target: 'Financial Risk', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e-op-sc', source: 'Operations', target: 'Supply Chain', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  
  // L3 -> L7 flow
  { id: 'e-lc-pa', source: 'Legal & Compliance', target: 'Predictive Analytics', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e-fr-pa', source: 'Financial Risk', target: 'Predictive Analytics', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e-sc-pa', source: 'Supply Chain', target: 'Predictive Analytics', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e-pa-st', source: 'Predictive Analytics', target: 'Strategy', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e-st-ed', source: 'Strategy', target: 'Executive Decision', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e-ed-pr', source: 'Executive Decision', target: 'Communication & PR', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
  { id: 'e-ed-rg', source: 'Executive Decision', target: 'Report Generator', animated: true, stroke: '#334155', markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } },
];

export function WorkflowVisualization() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const { agents } = useCommanderStore();

  useEffect(() => {
    // Update node styles based on agent status
    setNodes((nds) => 
      nds.map((node) => {
        const agentState = agents.find(a => a.name === node.id);
        if (agentState) {
          if (agentState.status === 'running') {
            return {
              ...node,
              style: { ...node.style, border: '1px solid #3b82f6', boxShadow: '0 0 15px rgba(59,130,246,0.5)' }
            };
          } else if (agentState.status === 'completed') {
            return {
              ...node,
              style: { ...node.style, border: '1px solid #22c55e', boxShadow: 'none' }
            };
          } else {
            return {
              ...node,
              style: { ...node.style, border: '1px solid #334155', boxShadow: 'none' }
            };
          }
        }
        return node;
      })
    );

    // Update edge animations and colors based on source/target status
    setEdges((eds) => 
      eds.map((edge) => {
        const targetAgent = agents.find(a => a.name === edge.target);
        if (targetAgent?.status === 'running') {
          return { ...edge, stroke: '#3b82f6', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' } };
        } else if (targetAgent?.status === 'completed') {
          return { ...edge, stroke: '#22c55e', animated: false, markerEnd: { type: MarkerType.ArrowClosed, color: '#22c55e' } };
        } else {
          return { ...edge, stroke: '#334155', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' } };
        }
      })
    );
  }, [agents, setNodes, setEdges]);

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex justify-between items-center shrink-0">
        <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight flex items-center gap-2">
            <Network className="w-7 h-7 text-primary" /> Orchestration Graph
          </h1>
          <p className="text-muted-foreground mt-1">Real-time LangGraph execution DAG for all 13 active agents.</p>
        </div>
      </div>

      <div className="flex-1 bg-card/50 backdrop-blur-md border border-border rounded-xl shadow-[0_8px_32px_rgba(0,0,0,0.3)] overflow-hidden relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          className="bg-transparent"
        >
          <Controls className="bg-card border-border fill-foreground" />
          <MiniMap className="bg-card border-border mask-secondary" nodeColor="#1e293b" maskColor="rgba(9, 9, 11, 0.7)" />
          <Background variant={BackgroundVariant.Dots} color="#334155" gap={16} />
        </ReactFlow>

        {/* Enterprise Legend Overlay */}
        <div className="absolute top-4 left-4 bg-card/80 backdrop-blur-md border border-border p-4 rounded-xl shadow-lg text-sm">
          <h4 className="font-semibold mb-3 text-foreground flex items-center gap-2">
            <Server className="w-4 h-4 text-primary" /> System State
          </h4>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]"></div>
              <span className="text-muted-foreground font-medium">Executing</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
              <span className="text-muted-foreground font-medium">Completed</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full border-2 border-dashed border-slate-600 bg-transparent"></div>
              <span className="text-muted-foreground font-medium">Queued</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
