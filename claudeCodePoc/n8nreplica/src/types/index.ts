export interface WorkflowNode {
  id: string;
  name: string;
  type: 'trigger' | 'action' | 'condition' | 'transform' | 'output';
  functionality: string;
  description: string;
  operation: string;
  position: { x: number; y: number };
  data: {
    label: string;
    description: string;
    functionality: string;
    operation: string;
    nodeType: 'trigger' | 'action' | 'condition' | 'transform' | 'output';
    icon: string;
    color: string;
    inputs?: NodeInput[];
    outputs?: NodeOutput[];
    parameters?: NodeParameter[];
  };
}

export interface NodeInput {
  id: string;
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  required: boolean;
  description?: string;
}

export interface NodeOutput {
  id: string;
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  description?: string;
}

export interface NodeParameter {
  id: string;
  name: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'textarea';
  value: any;
  options?: { label: string; value: any }[];
  description?: string;
  required?: boolean;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  type?: string;
  data?: {
    label?: string;
  };
}

export interface ComponentTemplate {
  id: string;
  name: string;
  type: 'trigger' | 'action' | 'condition' | 'transform' | 'output';
  category: string;
  icon: string;
  color: string;
  description: string;
  functionality: string;
  operation: string;
  inputs: NodeInput[];
  outputs: NodeOutput[];
  parameters: NodeParameter[];
  version: string;
  author?: string;
  tags?: string[];
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  version: string;
  author?: string;
  tags?: string[];
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  metadata?: {
    createdAt: string;
    updatedAt: string;
    category?: string;
    thumbnail?: string;
  };
}

export interface CanvasState {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  selectedNode?: WorkflowNode;
  selectedEdge?: WorkflowEdge;
  viewport: {
    x: number;
    y: number;
    zoom: number;
  };
}

export interface AppState {
  canvas: CanvasState;
  templates: ComponentTemplate[];
  workflow: WorkflowTemplate | null;
  isDarkMode: boolean;
  isLoading: boolean;
  error?: string;
}

export interface DragDropItem {
  type: string;
  id: string;
  data: ComponentTemplate;
}

export interface NodeContextMenuProps {
  x: number;
  y: number;
  nodeId: string;
  isVisible: boolean;
}

export interface ExportOptions {
  format: 'json' | 'yaml' | 'javascript' | 'python';
  includeMetadata: boolean;
  minify: boolean;
}

export interface ImportOptions {
  validateSchema: boolean;
  mergeWithExisting: boolean;
  replaceAll: boolean;
}

export type NodeType = 'trigger' | 'action' | 'condition' | 'transform' | 'output';

export type ComponentCategory = 
  | 'agents'
  | 'tools'
  | 'api-calls'
  | 'integrations'
  | 'triggers'
  | 'actions' 
  | 'conditions'
  | 'transforms'
  | 'outputs'
  | 'utilities'
  | 'ai'
  | 'data';

export interface SearchFilters {
  category?: ComponentCategory;
  type?: NodeType;
  tags?: string[];
  author?: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  id: string;
  message: string;
  nodeId?: string;
  edgeId?: string;
  severity: 'error' | 'warning' | 'info';
}

export interface ValidationWarning {
  id: string;
  message: string;
  nodeId?: string;
  edgeId?: string;
  suggestion?: string;
}

export interface ExecutionContext {
  workflowId: string;
  executionId: string;
  variables: Record<string, any>;
  secrets: Record<string, string>;
  environment: 'development' | 'staging' | 'production';
}

export interface ExecutionResult {
  success: boolean;
  output: any;
  error?: string;
  executionTime: number;
  logs: ExecutionLog[];
}

export interface ExecutionLog {
  timestamp: string;
  level: 'debug' | 'info' | 'warn' | 'error';
  message: string;
  nodeId?: string;
  data?: any;
}