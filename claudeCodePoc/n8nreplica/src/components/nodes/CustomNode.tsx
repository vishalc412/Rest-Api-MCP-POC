'use client';

import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

interface CustomNodeData {
  label: string;
  description: string;
  functionality: string;
  operation: string;
  nodeType: 'trigger' | 'action' | 'condition' | 'transform' | 'output';
  icon: string;
  color: string;
  inputs?: any[];
  outputs?: any[];
  parameters?: any[];
}

const getNodeTypeColor = (type: string) => {
  switch (type) {
    case 'trigger':
      return '#4ade80';
    case 'action':
      return '#3b82f6';
    case 'condition':
      return '#f59e0b';
    case 'transform':
      return '#8b5cf6';
    case 'output':
      return '#ef4444';
    default:
      return '#6b7280';
  }
};

const CustomNode = memo(({ data, selected }: NodeProps<CustomNodeData>) => {
  const nodeColor = getNodeTypeColor(data.nodeType);
  
  // Improved logic for handles based on actual inputs and outputs
  const hasInputs = data.inputs && data.inputs.length > 0;
  const hasOutputs = data.outputs && data.outputs.length > 0;

  return (
    <div className={`ai-custom-node ${selected ? 'selected' : ''}`}>
      {/* Input Handle */}
      {hasInputs && (
        <Handle
          type="target"
          position={Position.Left}
          id="input"
          style={{
            background: nodeColor,
            border: '3px solid white',
            width: 14,
            height: 14,
            left: -7,
          }}
        />
      )}

      {/* Node Header */}
      <div className="ai-node-header" style={{ background: `linear-gradient(135deg, ${nodeColor}dd, ${nodeColor})` }}>
        <div style={{ fontSize: '16px', color: 'white' }}>
          {data.icon}
        </div>
        <div className="ai-node-title" style={{ color: 'white' }}>
          {data.label}
        </div>
        <div className="ai-node-type-badge" style={{ background: 'rgba(255,255,255,0.2)', color: 'white' }}>
          {data.nodeType}
        </div>
      </div>

      {/* Node Body */}
      <div className="ai-node-body">
        {data.description && (
          <div className="ai-node-description">
            {data.description}
          </div>
        )}
        
        {/* Parameters Count */}
        {data.parameters && data.parameters.length > 0 && (
          <div style={{ 
            fontSize: '11px', 
            color: 'var(--color-text-tertiary)', 
            marginTop: 'var(--space-2)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-1)',
            fontWeight: 'var(--font-weight-medium)'
          }}>
            <span>⚙️</span>
            <span>{data.parameters.length} parameter{data.parameters.length !== 1 ? 's' : ''}</span>
          </div>
        )}
      </div>

      {/* Output Handle */}
      {hasOutputs && (
        <Handle
          type="source"
          position={Position.Right}
          id="output"
          style={{
            background: nodeColor,
            border: '3px solid white',
            width: 14,
            height: 14,
            right: -7,
          }}
        />
      )}

      {/* Status Indicator */}
      <div className="ai-node-status" style={{ background: '#10b981' }}></div>
    </div>
  );
});

CustomNode.displayName = 'CustomNode';

export default CustomNode;