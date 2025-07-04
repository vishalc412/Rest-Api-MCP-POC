'use client';

import React from 'react';
import { ComponentTemplate } from '@/types';

interface ComponentCardProps {
  template: ComponentTemplate;
}

export default function ComponentCard({ template }: ComponentCardProps) {
  const onDragStart = (event: React.DragEvent, template: ComponentTemplate) => {
    event.dataTransfer.setData('application/reactflow', template.type);
    event.dataTransfer.setData('application/json', JSON.stringify(template));
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div
      className="ai-node-item"
      draggable
      onDragStart={(event) => onDragStart(event, template)}
      title={template.description}
    >
      <div className={`ai-node-icon ${template.type}`}>
        {template.icon}
      </div>
      
      <div className="ai-node-info">
        <div className="ai-node-name">
          {template.name}
        </div>
        <div className="ai-node-description">
          {template.description}
        </div>
      </div>
    </div>
  );
}