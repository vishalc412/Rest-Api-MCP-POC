'use client';

import React, { useState, useEffect } from 'react';
import { Panel } from 'primereact/panel';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { InputSwitch } from 'primereact/inputswitch';
import { TabView, TabPanel } from 'primereact/tabview';
import { ScrollPanel } from 'primereact/scrollpanel';
import { Tag } from 'primereact/tag';
import { Divider } from 'primereact/divider';
import { 
  Settings, 
  Trash2, 
  Copy, 
  Eye, 
  Code,
  Info,
  Link,
  Terminal,
  ChevronRight
} from 'lucide-react';
import { WorkflowNode, WorkflowEdge, NodeParameter } from '@/types';

interface RightSidebarProps {
  selectedNode?: WorkflowNode | null;
  selectedEdge?: WorkflowEdge | null;
  onNodeUpdate: (nodeId: string, updates: Partial<WorkflowNode['data']>) => void;
  onNodeDelete: (nodeId: string) => void;
  onToggle: () => void;
}

export default function RightSidebar({
  selectedNode,
  selectedEdge,
  onNodeUpdate,
  onNodeDelete,
  onToggle,
}: RightSidebarProps) {
  const [nodeData, setNodeData] = useState<any>(null);
  const [showJson, setShowJson] = useState(false);

  useEffect(() => {
    if (selectedNode) {
      setNodeData(selectedNode.data);
    } else {
      setNodeData(null);
    }
  }, [selectedNode]);

  const handleParameterChange = (paramId: string, value: any) => {
    if (!selectedNode || !nodeData) return;

    const updatedParameters = nodeData.parameters?.map((param: NodeParameter) =>
      param.id === paramId ? { ...param, value } : param
    ) || [];

    const updates = {
      parameters: updatedParameters,
    };

    setNodeData((prev: any) => ({ ...prev, parameters: updatedParameters }));
    onNodeUpdate(selectedNode.id, updates);
  };

  const handleNodePropertyChange = (property: string, value: any) => {
    if (!selectedNode) return;

    const updates = { [property]: value };
    setNodeData((prev: any) => ({ ...prev, [property]: value }));
    onNodeUpdate(selectedNode.id, updates);
  };

  const renderParameterField = (parameter: NodeParameter) => {
    switch (parameter.type) {
      case 'string':
        return (
          <InputText
            value={parameter.value || ''}
            onChange={(e) => handleParameterChange(parameter.id, e.target.value)}
            placeholder={parameter.description}
            className="ai-input"
          />
        );
      
      case 'textarea':
      case 'html':
        return (
          <InputTextarea
            value={parameter.value || ''}
            onChange={(e) => handleParameterChange(parameter.id, e.target.value)}
            placeholder={parameter.description || "Enter content..."}
            rows={4}
            className="ai-textarea"
          />
        );
      
      case 'number':
        return (
          <InputText
            type="number"
            value={parameter.value || ''}
            onChange={(e) => handleParameterChange(parameter.id, Number(e.target.value))}
            placeholder={parameter.description}
            className="ai-input"
          />
        );
      
      case 'boolean':
        return (
          <div className="ai-switch-container">
            <InputSwitch
              checked={parameter.value || false}
              onChange={(e) => handleParameterChange(parameter.id, e.value)}
            />
          </div>
        );
      
      case 'select':
        return (
          <Dropdown
            value={parameter.value}
            options={parameter.options || []}
            onChange={(e) => handleParameterChange(parameter.id, e.value)}
            placeholder={parameter.description}
            className="ai-dropdown"
          />
        );
      
      default:
        return (
          <InputText
            value={parameter.value || ''}
            onChange={(e) => handleParameterChange(parameter.id, e.target.value)}
            placeholder={parameter.description}
            className="ai-input"
          />
        );
    }
  };

  const renderNodeProperties = () => {
    if (!selectedNode || !nodeData) {
      return (
        <div className="ai-empty-state">
          <Settings className="ai-empty-state-icon" size={48} />
          <div className="ai-empty-state-title">No Selection</div>
          <div className="ai-empty-state-description">Select a node to edit properties</div>
        </div>
      );
    }

    return (
      <div className="ai-properties-container">
        <div className="ai-properties-tabs">
          <TabView>
            <TabPanel header="Properties" leftIcon={<Settings size={16} className="mr-2" />}>
              <div className="ai-properties-content">
                {/* Basic Properties */}
                <div className="ai-property-section">
                  <div className="ai-section-header">
                    <Info size={16} />
                    <span>Basic Information</span>
                  </div>
                  
                  <div className="ai-form-group">
                    <label className="ai-form-label">Name</label>
                    <InputText
                      value={nodeData.label || ''}
                      onChange={(e) => handleNodePropertyChange('label', e.target.value)}
                      className="ai-input"
                    />
                  </div>

                  <div className="ai-form-group">
                    <label className="ai-form-label">Description</label>
                    <InputTextarea
                      value={nodeData.description || ''}
                      onChange={(e) => handleNodePropertyChange('description', e.target.value)}
                      rows={2}
                      className="ai-textarea"
                    />
                  </div>

                  <div className="ai-tag-group">
                    <Tag value={nodeData.nodeType} severity="info" />
                    <Tag value={selectedNode.id} severity="secondary" />
                  </div>
                </div>

                {/* Node Actions */}
                <div className="ai-property-section">
                  <div className="ai-section-header">
                    <Terminal size={16} />
                    <span>Node Actions</span>
                  </div>
                  
                  <div className="warry-node-actions">
                    <button
                      className="warry-action-button duplicate"
                      onClick={() => {
                        // Copy node logic
                        console.log('Duplicate node:', selectedNode.id);
                      }}
                    >
                      <Copy size={18} />
                      <span>Duplicate Node</span>
                    </button>
                    
                    <button
                      className="warry-action-button delete"
                      onClick={() => selectedNode && onNodeDelete(selectedNode.id)}
                    >
                      <Trash2 size={18} />
                      <span>Delete Node</span>
                    </button>
                  </div>
                </div>

                {/* Parameters */}
                {nodeData.parameters && nodeData.parameters.length > 0 && (
                  <div className="ai-property-section">
                    <div className="ai-section-header">
                      <Settings size={16} />
                      <span>Parameters</span>
                    </div>
                    
                    {nodeData.parameters.map((parameter: NodeParameter) => (
                      <div key={parameter.id} className="ai-form-group">
                        <label className="ai-form-label">
                          {parameter.name}
                          {parameter.required && <span className="ai-required">*</span>}
                        </label>
                        {renderParameterField(parameter)}
                        {parameter.description && (
                          <div className="ai-field-help">{parameter.description}</div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Inputs */}
                {nodeData.inputs && nodeData.inputs.length > 0 && (
                  <div className="ai-property-section">
                    <div className="ai-section-header">
                      <Link size={16} />
                      <span>Inputs</span>
                    </div>
                    {nodeData.inputs.map((input: any) => (
                      <div key={input.id} className="ai-connection-item">
                        <div className="ai-connection-name">{input.name}</div>
                        <div className="ai-connection-type">{input.type} {input.required && '(required)'}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Outputs */}
                {nodeData.outputs && nodeData.outputs.length > 0 && (
                  <div className="ai-property-section">
                    <div className="ai-section-header">
                      <Link size={16} />
                      <span>Outputs</span>
                    </div>
                    {nodeData.outputs.map((output: any) => (
                      <div key={output.id} className="ai-connection-item">
                        <div className="ai-connection-name">{output.name}</div>
                        <div className="ai-connection-type">{output.type}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </TabPanel>

            <TabPanel header="Preview" leftIcon={<Eye size={16} className="mr-2" />}>
              <div className="ai-properties-content">
                <div className="ai-property-section">
                  <div className="ai-section-header">
                    <Info size={16} />
                    <span>Functionality</span>
                  </div>
                  <div className="ai-connection-item">
                    <div className="ai-connection-name">What it does</div>
                    <div className="ai-connection-type">{nodeData.functionality}</div>
                  </div>
                </div>
                
                <div className="ai-property-section">
                  <div className="ai-section-header">
                    <Terminal size={16} />
                    <span>Operation</span>
                  </div>
                  <div className="ai-connection-item">
                    <div className="ai-connection-name">Technical operation</div>
                    <div className="ai-connection-type">{nodeData.operation}</div>
                  </div>
                </div>
              </div>
            </TabPanel>

            <TabPanel header="JSON" leftIcon={<Code size={16} className="mr-2" />}>
              <div className="ai-properties-content">
                <div className="ai-property-section">
                  <div className="ai-section-header">
                    <Code size={16} />
                    <span>Node Data</span>
                  </div>
                  
                  <div className="ai-form-group">
                    <Button
                      label={showJson ? "Hide JSON" : "Show JSON"}
                      icon={<Terminal size={16} />}
                      onClick={() => setShowJson(!showJson)}
                      className="ai-button secondary"
                    />
                  </div>
                  
                  {showJson && (
                    <pre className="warry-json-preview">
                      {JSON.stringify(
                        {
                          id: selectedNode.id,
                          type: nodeData.nodeType,
                          data: nodeData,
                          position: selectedNode.position,
                        },
                        null,
                        2
                      )}
                    </pre>
                  )}
                </div>
              </div>
            </TabPanel>
          </TabView>
        </div>
      </div>
    );
  };

  const renderEdgeProperties = () => {
    if (!selectedEdge) return null;

    return (
      <div className="space-y-4 p-4">
        <h3 className="text-sm font-semibold">Edge Properties</h3>
        <div className="space-y-2">
          <div>
            <label className="block text-xs font-medium mb-1">Source</label>
            <Tag value={selectedEdge.source} severity="info" />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1">Target</label>
            <Tag value={selectedEdge.target} severity="info" />
          </div>
          {selectedEdge.data?.label && (
            <div>
              <label className="block text-xs font-medium mb-1">Label</label>
              <InputText
                value={selectedEdge.data.label}
                className="w-full"
                disabled
              />
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="ai-sidebar-right">
      <div className="ai-sidebar-header premium">
        <div className="warry-sidebar-title">
          <Settings size={20} />
          <span>WarryWorks Properties</span>
        </div>
        <button 
          className="ai-sidebar-toggle premium"
          onClick={onToggle}
          title="Hide Properties Panel"
        >
          <ChevronRight size={16} />
        </button>
      </div>
      
      <div className="ai-sidebar-content">
        {selectedNode ? renderNodeProperties() : selectedEdge ? renderEdgeProperties() : (
          <div className="ai-empty-state">
            <Settings className="ai-empty-state-icon" size={48} />
            <div className="ai-empty-state-title">No Selection</div>
            <div className="ai-empty-state-description">Select a node or edge to edit properties</div>
          </div>
        )}
      </div>
    </div>
  );
}