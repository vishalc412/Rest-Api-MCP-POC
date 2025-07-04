import { WorkflowNode, WorkflowEdge, WorkflowTemplate, ValidationResult, ValidationError } from '@/types';

export const generateWorkflowJSON = (
  nodes: WorkflowNode[],
  edges: WorkflowEdge[],
  metadata?: any
): WorkflowTemplate => {
  return {
    id: `workflow-${Date.now()}`,
    name: metadata?.name || 'Untitled Workflow',
    description: metadata?.description || 'Generated workflow',
    version: '1.0.0',
    author: metadata?.author || 'System',
    tags: metadata?.tags || [],
    nodes: nodes.map(node => ({
      id: node.id,
      name: node.data?.label || node.id,
      type: node.data?.nodeType || 'action',
      functionality: node.data?.functionality || '',
      description: node.data?.description || '',
      operation: node.data?.operation || '',
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
    metadata: {
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      category: metadata?.category || 'general',
    },
  };
};

export const exportWorkflowToJSON = (workflow: WorkflowTemplate): string => {
  return JSON.stringify(workflow, null, 2);
};

export const exportWorkflowToYAML = (workflow: WorkflowTemplate): string => {
  // Simple YAML export - for production, use a proper YAML library
  const yamlLines: string[] = [];
  
  yamlLines.push(`id: ${workflow.id}`);
  yamlLines.push(`name: "${workflow.name}"`);
  yamlLines.push(`description: "${workflow.description}"`);
  yamlLines.push(`version: "${workflow.version}"`);
  yamlLines.push(`author: "${workflow.author || 'Unknown'}"`);
  yamlLines.push('');
  
  yamlLines.push('nodes:');
  workflow.nodes.forEach((node, index) => {
    yamlLines.push(`  - id: ${node.id}`);
    yamlLines.push(`    name: "${node.name}"`);
    yamlLines.push(`    type: ${node.type}`);
    yamlLines.push(`    functionality: "${node.functionality}"`);
    yamlLines.push(`    operation: ${node.operation}`);
    yamlLines.push(`    position:`);
    yamlLines.push(`      x: ${node.position.x}`);
    yamlLines.push(`      y: ${node.position.y}`);
    if (index < workflow.nodes.length - 1) yamlLines.push('');
  });
  
  yamlLines.push('');
  yamlLines.push('edges:');
  workflow.edges.forEach((edge, index) => {
    yamlLines.push(`  - id: ${edge.id}`);
    yamlLines.push(`    source: ${edge.source}`);
    yamlLines.push(`    target: ${edge.target}`);
    if (edge.sourceHandle) yamlLines.push(`    sourceHandle: ${edge.sourceHandle}`);
    if (edge.targetHandle) yamlLines.push(`    targetHandle: ${edge.targetHandle}`);
    if (index < workflow.edges.length - 1) yamlLines.push('');
  });
  
  return yamlLines.join('\n');
};

export const exportWorkflowToJavaScript = (workflow: WorkflowTemplate): string => {
  const jsLines: string[] = [];
  
  jsLines.push('// Generated Workflow JavaScript');
  jsLines.push(`// Workflow: ${workflow.name}`);
  jsLines.push(`// Generated: ${new Date().toISOString()}`);
  jsLines.push('');
  
  jsLines.push('const workflow = {');
  jsLines.push(`  id: '${workflow.id}',`);
  jsLines.push(`  name: '${workflow.name}',`);
  jsLines.push(`  description: '${workflow.description}',`);
  jsLines.push(`  version: '${workflow.version}',`);
  jsLines.push('');
  
  jsLines.push('  async execute(input) {');
  jsLines.push('    const context = { input, variables: {} };');
  jsLines.push('    const results = {};');
  jsLines.push('');
  
  // Generate execution logic based on nodes
  workflow.nodes.forEach(node => {
    switch (node.type) {
      case 'trigger':
        jsLines.push(`    // Trigger: ${node.name}`);
        jsLines.push(`    console.log('Starting workflow with trigger: ${node.name}');`);
        break;
      case 'action':
        jsLines.push(`    // Action: ${node.name}`);
        jsLines.push(`    results['${node.id}'] = await this.execute${node.operation}(context);`);
        break;
      case 'condition':
        jsLines.push(`    // Condition: ${node.name}`);
        jsLines.push(`    if (await this.evaluate${node.operation}(context)) {`);
        jsLines.push(`      // True path`);
        jsLines.push(`    } else {`);
        jsLines.push(`      // False path`);
        jsLines.push(`    }`);
        break;
      case 'transform':
        jsLines.push(`    // Transform: ${node.name}`);
        jsLines.push(`    context.variables = await this.transform${node.operation}(context);`);
        break;
      case 'output':
        jsLines.push(`    // Output: ${node.name}`);
        jsLines.push(`    await this.output${node.operation}(context);`);
        break;
    }
    jsLines.push('');
  });
  
  jsLines.push('    return results;');
  jsLines.push('  }');
  jsLines.push('};');
  jsLines.push('');
  jsLines.push('module.exports = workflow;');
  
  return jsLines.join('\n');
};

export const exportWorkflowToPython = (workflow: WorkflowTemplate): string => {
  const pyLines: string[] = [];
  
  pyLines.push('# Generated Workflow Python');
  pyLines.push(`# Workflow: ${workflow.name}`);
  pyLines.push(`# Generated: ${new Date().toISOString()}`);
  pyLines.push('');
  
  pyLines.push('import asyncio');
  pyLines.push('import json');
  pyLines.push('from typing import Dict, Any');
  pyLines.push('');
  
  pyLines.push('class Workflow:');
  pyLines.push(`    def __init__(self):`);
  pyLines.push(`        self.id = '${workflow.id}'`);
  pyLines.push(`        self.name = '${workflow.name}'`);
  pyLines.push(`        self.description = '${workflow.description}'`);
  pyLines.push(`        self.version = '${workflow.version}'`);
  pyLines.push('');
  
  pyLines.push('    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:');
  pyLines.push('        """Execute the workflow with given input data"""');
  pyLines.push('        context = {"input": input_data, "variables": {}}');
  pyLines.push('        results = {}');
  pyLines.push('');
  
  // Generate execution logic based on nodes
  workflow.nodes.forEach(node => {
    switch (node.type) {
      case 'trigger':
        pyLines.push(`        # Trigger: ${node.name}`);
        pyLines.push(`        print(f"Starting workflow with trigger: ${node.name}")`);
        break;
      case 'action':
        pyLines.push(`        # Action: ${node.name}`);
        pyLines.push(`        results['${node.id}'] = await self.execute_${node.operation}(context)`);
        break;
      case 'condition':
        pyLines.push(`        # Condition: ${node.name}`);
        pyLines.push(`        if await self.evaluate_${node.operation}(context):`);
        pyLines.push(`            # True path`);
        pyLines.push(`            pass`);
        pyLines.push(`        else:`);
        pyLines.push(`            # False path`);
        pyLines.push(`            pass`);
        break;
      case 'transform':
        pyLines.push(`        # Transform: ${node.name}`);
        pyLines.push(`        context['variables'] = await self.transform_${node.operation}(context)`);
        break;
      case 'output':
        pyLines.push(`        # Output: ${node.name}`);
        pyLines.push(`        await self.output_${node.operation}(context)`);
        break;
    }
    pyLines.push('');
  });
  
  pyLines.push('        return results');
  pyLines.push('');
  
  // Add placeholder methods
  pyLines.push('    # Placeholder methods - implement based on your requirements');
  const uniqueOperations = [...new Set(workflow.nodes.map(node => node.operation))];
  uniqueOperations.forEach(operation => {
    pyLines.push(`    async def execute_${operation}(self, context):`);
    pyLines.push(`        """Implement ${operation} operation"""`);
    pyLines.push(`        pass`);
    pyLines.push('');
  });
  
  return pyLines.join('\n');
};

export const validateWorkflow = (workflow: WorkflowTemplate): ValidationResult => {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  // Basic validation
  if (!workflow.name || workflow.name.trim() === '') {
    errors.push({
      id: 'workflow-name-empty',
      message: 'Workflow name cannot be empty',
      severity: 'error',
    });
  }

  if (!workflow.nodes || workflow.nodes.length === 0) {
    errors.push({
      id: 'workflow-no-nodes',
      message: 'Workflow must have at least one node',
      severity: 'error',
    });
  }

  // Node validation
  workflow.nodes.forEach(node => {
    if (!node.id || node.id.trim() === '') {
      errors.push({
        id: 'node-id-empty',
        message: 'Node ID cannot be empty',
        nodeId: node.id,
        severity: 'error',
      });
    }

    if (!node.name || node.name.trim() === '') {
      warnings.push({
        id: 'node-name-empty',
        message: 'Node name should not be empty',
        nodeId: node.id,
        severity: 'warning',
      });
    }

    if (!node.type) {
      errors.push({
        id: 'node-type-missing',
        message: 'Node type is required',
        nodeId: node.id,
        severity: 'error',
      });
    }
  });

  // Edge validation
  workflow.edges.forEach(edge => {
    const sourceExists = workflow.nodes.some(node => node.id === edge.source);
    const targetExists = workflow.nodes.some(node => node.id === edge.target);

    if (!sourceExists) {
      errors.push({
        id: 'edge-source-missing',
        message: `Edge source node '${edge.source}' does not exist`,
        edgeId: edge.id,
        severity: 'error',
      });
    }

    if (!targetExists) {
      errors.push({
        id: 'edge-target-missing',
        message: `Edge target node '${edge.target}' does not exist`,
        edgeId: edge.id,
        severity: 'error',
      });
    }
  });

  // Flow validation
  const triggerNodes = workflow.nodes.filter(node => node.type === 'trigger');
  if (triggerNodes.length === 0) {
    warnings.push({
      id: 'workflow-no-trigger',
      message: 'Workflow should have at least one trigger node',
      severity: 'warning',
    });
  }

  const outputNodes = workflow.nodes.filter(node => node.type === 'output');
  if (outputNodes.length === 0) {
    warnings.push({
      id: 'workflow-no-output',
      message: 'Workflow should have at least one output node',
      severity: 'warning',
    });
  }

  // Check for isolated nodes
  workflow.nodes.forEach(node => {
    const hasIncomingEdge = workflow.edges.some(edge => edge.target === node.id);
    const hasOutgoingEdge = workflow.edges.some(edge => edge.source === node.id);

    if (!hasIncomingEdge && !hasOutgoingEdge && node.type !== 'trigger') {
      warnings.push({
        id: 'node-isolated',
        message: 'Node is not connected to any other nodes',
        nodeId: node.id,
        severity: 'warning',
      });
    }
  });

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
  };
};

export const generateExecutionPayload = (
  workflow: WorkflowTemplate,
  inputData: any = {}
): any => {
  return {
    workflowId: workflow.id,
    workflowName: workflow.name,
    version: workflow.version,
    executionId: `exec-${Date.now()}`,
    input: inputData,
    nodes: workflow.nodes.map(node => ({
      id: node.id,
      name: node.name,
      type: node.type,
      functionality: node.functionality,
      operation: node.operation,
      parameters: node.data?.parameters || [],
    })),
    edges: workflow.edges,
    metadata: {
      executedAt: new Date().toISOString(),
      environment: 'development',
    },
  };
};

export const calculateWorkflowComplexity = (workflow: WorkflowTemplate): {
  nodeCount: number;
  edgeCount: number;
  complexity: 'low' | 'medium' | 'high';
  score: number;
} => {
  const nodeCount = workflow.nodes.length;
  const edgeCount = workflow.edges.length;
  const conditionalNodes = workflow.nodes.filter(node => node.type === 'condition').length;
  
  // Calculate complexity score
  const score = nodeCount + (edgeCount * 0.5) + (conditionalNodes * 2);
  
  let complexity: 'low' | 'medium' | 'high';
  if (score <= 10) {
    complexity = 'low';
  } else if (score <= 30) {
    complexity = 'medium';
  } else {
    complexity = 'high';
  }

  return {
    nodeCount,
    edgeCount,
    complexity,
    score,
  };
};

export const findWorkflowPaths = (workflow: WorkflowTemplate): string[][] => {
  const paths: string[][] = [];
  const triggerNodes = workflow.nodes.filter(node => node.type === 'trigger');
  
  triggerNodes.forEach(trigger => {
    const visited = new Set<string>();
    const currentPath: string[] = [];
    
    const dfs = (nodeId: string) => {
      if (visited.has(nodeId)) return;
      
      visited.add(nodeId);
      currentPath.push(nodeId);
      
      const outgoingEdges = workflow.edges.filter(edge => edge.source === nodeId);
      
      if (outgoingEdges.length === 0) {
        // End of path
        paths.push([...currentPath]);
      } else {
        outgoingEdges.forEach(edge => {
          dfs(edge.target);
        });
      }
      
      currentPath.pop();
      visited.delete(nodeId);
    };
    
    dfs(trigger.id);
  });
  
  return paths;
};