import { useState } from 'react';
import { 
  ReactFlow, 
  MiniMap, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { PlayCircle, StopCircle, RefreshCw } from 'lucide-react';

const initialNodes = [
  { id: '1', position: { x: 400, y: 50 }, data: { label: 'Workflow Manager (Active)' }, type: 'input', style: { background: '#3b82f6', color: 'white', borderRadius: '8px', border: 'none' } },
  
  { id: '2', position: { x: 50, y: 150 }, data: { label: 'Customer Rep. (Done)' }, style: { background: '#22c55e', color: 'white', borderRadius: '8px', border: 'none' } },
  { id: '3', position: { x: 250, y: 150 }, data: { label: 'Market Intel (Running)' }, style: { background: '#eab308', color: 'white', borderRadius: '8px', border: 'none' } },
  { id: '4', position: { x: 450, y: 150 }, data: { label: 'Cyber Sec. (Done)' }, style: { background: '#22c55e', color: 'white', borderRadius: '8px', border: 'none' } },
  { id: '5', position: { x: 650, y: 150 }, data: { label: 'Financial (Done)' }, style: { background: '#22c55e', color: 'white', borderRadius: '8px', border: 'none' } },
  
  { id: '6', position: { x: 50, y: 250 }, data: { label: 'Supply Chain (Done)' }, style: { background: '#22c55e', color: 'white', borderRadius: '8px', border: 'none' } },
  { id: '7', position: { x: 250, y: 250 }, data: { label: 'Human Resources (Done)' }, style: { background: '#22c55e', color: 'white', borderRadius: '8px', border: 'none' } },
  { id: '8', position: { x: 450, y: 250 }, data: { label: 'Public Relations (Done)' }, style: { background: '#22c55e', color: 'white', borderRadius: '8px', border: 'none' } },
  { id: '9', position: { x: 650, y: 250 }, data: { label: 'IT Ops (Running)' }, style: { background: '#eab308', color: 'white', borderRadius: '8px', border: 'none' } },
  { id: '10', position: { x: 850, y: 250 }, data: { label: 'Legal (Done)' }, style: { background: '#22c55e', color: 'white', borderRadius: '8px', border: 'none' } },

  { id: '11', position: { x: 250, y: 350 }, data: { label: 'Risk Mgmt (Queued)' }, style: { background: '#64748b', color: 'white', borderRadius: '8px', border: 'none' } },
  { id: '12', position: { x: 550, y: 350 }, data: { label: 'Strategic Plan (Queued)' }, style: { background: '#64748b', color: 'white', borderRadius: '8px', border: 'none' } },

  { id: '13', position: { x: 400, y: 450 }, data: { label: 'Executive Decision (Queued)' }, style: { background: '#64748b', color: 'white', borderRadius: '8px', border: 'none' } },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e1-3', source: '1', target: '3', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e1-4', source: '1', target: '4', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e1-5', source: '1', target: '5', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  
  { id: 'e2-6', source: '2', target: '6', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e3-7', source: '3', target: '7', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e4-8', source: '4', target: '8', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e5-9', source: '5', target: '9', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e5-10', source: '5', target: '10', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  
  { id: 'e6-11', source: '6', target: '11', animated: false, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e7-11', source: '7', target: '11', animated: false, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e8-11', source: '8', target: '11', animated: false, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e9-12', source: '9', target: '12', animated: false, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e10-12', source: '10', target: '12', animated: false, markerEnd: { type: MarkerType.ArrowClosed } },
  
  { id: 'e11-13', source: '11', target: '13', animated: false, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e12-13', source: '12', target: '13', animated: false, markerEnd: { type: MarkerType.ArrowClosed } },
];

export function WorkflowMonitor() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [isRunning, setIsRunning] = useState(true);

  // Here we would typically use useEffect to subscribe to EventBus via websocket
  // and dynamically add nodes/edges as the LLM orchestrator plans the DAG.
  // For the final demonstration layout, we map the LLM plan to the ReactFlow state.

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex justify-between items-center shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Live Workflow DAG</h1>
          <p className="text-slate-500 text-sm mt-1">Real-time LangChain Execution Graph.</p>
        </div>
        <div className="flex gap-3">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 shadow-sm transition-colors">
            <RefreshCw className="w-4 h-4" />
            Sync Status
          </button>
        </div>
      </div>

      <div className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          className="bg-slate-50 dark:bg-slate-950"
        >
          <Controls className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700" />
          <MiniMap className="bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800" maskColor="rgba(0,0,0,0.1)" />
          <Background color="#94a3b8" gap={16} />
        </ReactFlow>

        {/* Legend Overlay */}
        <div className="absolute top-4 left-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur border border-slate-200 dark:border-slate-800 p-3 rounded-lg shadow-sm text-sm">
          <h4 className="font-semibold mb-2 text-slate-800 dark:text-slate-200">Legend</h4>
          <div className="space-y-2">
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-blue-500"></div><span className="text-slate-600 dark:text-slate-400">Orchestrator</span></div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-yellow-500"></div><span className="text-slate-600 dark:text-slate-400">Executing</span></div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-green-500"></div><span className="text-slate-600 dark:text-slate-400">Completed</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
