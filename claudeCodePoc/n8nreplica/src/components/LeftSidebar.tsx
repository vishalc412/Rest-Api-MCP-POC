'use client';

import React, { useState } from 'react';
import { 
  Search, 
  Play,
  Zap,
  GitBranch,
  RotateCcw as Transform,
  Target,
  Package,
  Brain,
  Database,
  Settings,
  PanelLeftClose,
  ChevronLeft,
  Bot,
  Wrench,
  Link2,
  Puzzle,
  Sparkles
} from 'lucide-react';
import { ComponentTemplate, ComponentCategory, NodeType } from '@/types';
import ComponentCard from './ComponentCard';

interface LeftSidebarProps {
  templates: ComponentTemplate[];
  onTemplateUpload: (templates: ComponentTemplate[]) => void;
  onToggle: () => void;
}

const categoryIcons = {
  agents: <Bot size={18} />,
  tools: <Wrench size={18} />,
  'api-calls': <Link2 size={18} />,
  integrations: <Puzzle size={18} />,
  triggers: <Play size={16} />,
  actions: <Zap size={16} />,
  conditions: <GitBranch size={16} />,
  transforms: <Transform size={16} />,
  outputs: <Target size={16} />,
  utilities: <Package size={16} />,
  ai: <Brain size={16} />,
  data: <Database size={16} />,
};

const categoryLabels = {
  agents: 'AI Agents',
  tools: 'Agent Tools',
  'api-calls': 'API Calls',
  integrations: '3rd Party Integrations',
  triggers: 'Triggers',
  actions: 'Actions',
  conditions: 'Conditions',
  transforms: 'Transforms',
  outputs: 'Outputs',
  utilities: 'Utilities',
  ai: 'AI Services',
  data: 'Data Processing',
};

export default function LeftSidebar({ templates, onTemplateUpload, onToggle }: LeftSidebarProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesSearch;
  });

  const groupedTemplates = filteredTemplates.reduce((acc, template) => {
    const category = template.category;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(template);
    return acc;
  }, {} as Record<string, ComponentTemplate[]>);

  return (
    <div className="ai-sidebar-left">
      <div className="ai-sidebar-header premium">
        <div className="warry-sidebar-title">
          <Sparkles size={20} />
          <span>WarryWorks Components</span>
        </div>
        <button 
          className="ai-sidebar-toggle premium"
          onClick={onToggle}
          title="Hide Components Panel"
        >
          <ChevronLeft size={16} />
        </button>
      </div>
      
      <div className="ai-sidebar-content">
        {/* Premium Search */}
        <div className="warry-search-container">
          <Search className="warry-search-icon" size={18} />
          <input
            className="warry-search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search components..."
          />
        </div>

        {/* Premium Component Categories */}
        {Object.entries(groupedTemplates).map(([category, categoryTemplates]) => (
          <div key={category} className="warry-category">
            <div className="warry-category-header">
              <div className="warry-category-icon">
                {categoryIcons[category as ComponentCategory]}
              </div>
              <div className="warry-category-title">
                {categoryLabels[category as ComponentCategory] || category}
              </div>
              <div className="warry-category-count">{categoryTemplates.length}</div>
            </div>
            
            <div className="warry-category-items">
              {categoryTemplates.map((template) => (
                <ComponentCard key={template.id} template={template} />
              ))}
            </div>
          </div>
        ))}
        
        {filteredTemplates.length === 0 && (
          <div className="ai-empty-state">
            <Package className="ai-empty-state-icon" size={48} />
            <div className="ai-empty-state-title">No nodes found</div>
            <div className="ai-empty-state-description">Try adjusting your search</div>
          </div>
        )}
      </div>
    </div>
  );
}