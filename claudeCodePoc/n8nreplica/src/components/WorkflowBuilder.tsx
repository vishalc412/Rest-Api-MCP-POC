'use client';

import React, { useState, useCallback, useRef } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Connection,
  Edge,
  Node,
  ReactFlowProvider,
  useReactFlow,
} from 'reactflow';

import 'reactflow/dist/style.css';

import Header from './Header';
import LeftSidebar from './LeftSidebar';
import RightSidebar from './RightSidebar';
import CustomNode from './nodes/CustomNode';
import { ComponentTemplate, WorkflowNode, WorkflowEdge } from '@/types';
import { defaultComponents } from '@/data/defaultComponents';
import { ChevronRight, ChevronLeft, Play, Terminal } from 'lucide-react';

const nodeTypes = {
  customNode: CustomNode,
};

const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

function WorkflowBuilderInner() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<WorkflowEdge | null>(null);
  const [templates, setTemplates] = useState<ComponentTemplate[]>(defaultComponents);
  const [isLeftSidebarOpen, setIsLeftSidebarOpen] = useState(true);
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { project, getViewport } = useReactFlow();

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node as WorkflowNode);
    setSelectedEdge(null);
  }, []);

  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    setSelectedEdge(edge as WorkflowEdge);
    setSelectedNode(null);
  }, []);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      if (!reactFlowWrapper.current) return;

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');
      const templateData = event.dataTransfer.getData('application/json');

      if (!type || !templateData) return;

      const template: ComponentTemplate = JSON.parse(templateData);
      const position = project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode: Node = {
        id: `${template.type}-${Date.now()}`,
        type: 'customNode',
        position,
        data: {
          label: template.name,
          description: template.description,
          functionality: template.functionality,
          operation: template.operation,
          nodeType: template.type,
          icon: template.icon,
          color: template.color,
          inputs: template.inputs,
          outputs: template.outputs,
          parameters: template.parameters.map(param => ({ ...param, value: param.value || '' })),
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [project, setNodes]
  );

  const handleTemplateUpload = useCallback((uploadedTemplates: ComponentTemplate[]) => {
    setTemplates(prev => [...prev, ...uploadedTemplates]);
  }, []);

  const handleWorkflowExport = useCallback(() => {
    const workflowData = {
      nodes: nodes.map(node => ({
        id: node.id,
        name: node.data.label,
        type: node.data.nodeType,
        functionality: node.data.functionality,
        description: node.data.description,
        operation: node.data.operation,
        position: node.position,
        data: node.data,
      })),
      edges: edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle,
        targetHandle: edge.targetHandle,
        type: edge.type,
        data: edge.data,
      })),
      viewport: getViewport(),
      metadata: {
        createdAt: new Date().toISOString(),
        version: '1.0.0',
      },
    };

    const dataStr = JSON.stringify(workflowData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `workflow-${Date.now()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  }, [nodes, edges, getViewport]);

  const handleWorkflowImport = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const workflowData = JSON.parse(e.target?.result as string);
        if (workflowData.nodes && workflowData.edges) {
          setNodes(workflowData.nodes.map((node: any) => ({
            id: node.id,
            type: 'customNode',
            position: node.position,
            data: node.data,
          })));
          setEdges(workflowData.edges);
        }
      } catch (error) {
        console.error('Error importing workflow:', error);
      }
    };
    reader.readAsText(file);
  }, [setNodes, setEdges]);

  const handleNodeUpdate = useCallback((nodeId: string, updates: Partial<Node['data']>) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...updates } }
          : node
      )
    );
  }, [setNodes]);

  const handleNodeDelete = useCallback((nodeId: string) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId));
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId));
    setSelectedNode(null);
  }, [setNodes, setEdges]);

  const toggleTheme = useCallback(() => {
    setIsDarkMode(prev => !prev);
    document.documentElement.setAttribute('data-theme', !isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  const handleWorkflowExecute = useCallback(() => {
    if (nodes.length === 0) {
      alert('Please add some nodes to execute the workflow.');
      return;
    }
    
    console.log('Executing workflow with nodes:', nodes);
    console.log('Executing workflow with edges:', edges);
    
    // Simulate execution
    alert(`Workflow execution started!\n\nNodes to execute: ${nodes.length}\nConnections: ${edges.length}\n\nCheck console for details.`);
  }, [nodes, edges]);

  return (
    <div className={`ai-workflow-app ${isDarkMode ? 'dark' : ''}`}>
      <div className="ai-header">
        <Header
          onTemplateUpload={handleTemplateUpload}
          onWorkflowExport={handleWorkflowExport}
          onWorkflowImport={handleWorkflowImport}
          onWorkflowExecute={handleWorkflowExecute}
          onToggleTheme={toggleTheme}
          isDarkMode={isDarkMode}
          onToggleLeftSidebar={() => setIsLeftSidebarOpen(!isLeftSidebarOpen)}
          onToggleRightSidebar={() => setIsRightSidebarOpen(!isRightSidebarOpen)}
          isLeftSidebarOpen={isLeftSidebarOpen}
          isRightSidebarOpen={isRightSidebarOpen}
        />
      </div>
      
      <div className="ai-main">
        {isLeftSidebarOpen && (
          <LeftSidebar
            templates={templates}
            onTemplateUpload={handleTemplateUpload}
            onToggle={() => setIsLeftSidebarOpen(!isLeftSidebarOpen)}
          />
        )}
        
        <div className="ai-canvas" ref={reactFlowWrapper}>
          {/* Floating Left Sidebar Restore Button */}
          {!isLeftSidebarOpen && (
            <button
              className="ai-floating-restore-left"
              onClick={() => setIsLeftSidebarOpen(true)}
              title="Show AI Nodes Panel"
            >
              <ChevronRight size={16} />
            </button>
          )}

          {/* Floating Right Sidebar Restore Button */}
          {!isRightSidebarOpen && (
            <button
              className="ai-floating-restore-right"
              onClick={() => setIsRightSidebarOpen(true)}
              title="Show Properties Panel"
            >
              <ChevronLeft size={16} />
            </button>
          )}

          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.1}
            maxZoom={2}
            defaultViewport={{ x: 0, y: 0, zoom: 1 }}
          >
            <Background 
              gap={20} 
              size={1}
              color={isDarkMode ? "#334155" : "#cbd5e1"}
            />
            <Controls />
            <MiniMap 
              nodeColor={(node) => {
                switch (node.data?.nodeType) {
                  case 'trigger': return '#10b981';
                  case 'action': return '#3b82f6';
                  case 'condition': return '#f59e0b';
                  case 'transform': return '#8b5cf6';
                  case 'output': return '#ef4444';
                  default: return '#6366f1';
                }
              }}
            />
          </ReactFlow>
        </div>
        
        {isRightSidebarOpen && (
          <RightSidebar
            selectedNode={selectedNode}
            selectedEdge={selectedEdge}
            onNodeUpdate={handleNodeUpdate}
            onNodeDelete={handleNodeDelete}
            onToggle={() => setIsRightSidebarOpen(!isRightSidebarOpen)}
          />
        )}
      </div>
    </div>
  );
}

export default function WorkflowBuilder() {
  return (
    <ReactFlowProvider>
      <WorkflowBuilderInner />
    </ReactFlowProvider>
  );
}