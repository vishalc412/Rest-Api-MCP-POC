'use client';

import React, { useRef } from 'react';
import { Button } from 'primereact/button';
import { Toolbar } from 'primereact/toolbar';
import { FileUpload } from 'primereact/fileupload';
import { Toast } from 'primereact/toast';
import { 
  Upload, 
  Download, 
  Moon, 
  Sun, 
  PanelLeftOpen, 
  PanelLeftClose,
  PanelRightOpen,
  PanelRightClose,
  Play,
  Save,
  FolderOpen,
  Settings
} from 'lucide-react';
import { ComponentTemplate } from '@/types';

interface HeaderProps {
  onTemplateUpload: (templates: ComponentTemplate[]) => void;
  onWorkflowExport: () => void;
  onWorkflowImport: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onWorkflowExecute: () => void;
  onToggleTheme: () => void;
  isDarkMode: boolean;
  onToggleLeftSidebar: () => void;
  onToggleRightSidebar: () => void;
  isLeftSidebarOpen: boolean;
  isRightSidebarOpen: boolean;
}

export default function Header({
  onTemplateUpload,
  onWorkflowExport,
  onWorkflowImport,
  onWorkflowExecute,
  onToggleTheme,
  isDarkMode,
  onToggleLeftSidebar,
  onToggleRightSidebar,
  isLeftSidebarOpen,
  isRightSidebarOpen,
}: HeaderProps) {
  const toast = useRef<Toast>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleTemplateUpload = (event: any) => {
    const files = event.files;
    if (files && files.length > 0) {
      const file = files[0];
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const templates = JSON.parse(e.target?.result as string);
          if (Array.isArray(templates)) {
            onTemplateUpload(templates);
            toast.current?.show({
              severity: 'success',
              summary: 'Success',
              detail: `Uploaded ${templates.length} templates successfully`,
              life: 3000,
            });
          } else {
            throw new Error('Invalid template format');
          }
        } catch (error) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to parse template file',
            life: 3000,
          });
        }
      };
      
      reader.readAsText(file);
    }
  };

  const handleWorkflowImportClick = () => {
    fileInputRef.current?.click();
  };

  const leftContent = (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-2 mr-4">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-sm">N8</span>
        </div>
        <h1 className="text-xl font-bold text-gradient">AI Workflow Builder</h1>
      </div>
      
      <Button
        icon={isLeftSidebarOpen ? <PanelLeftClose size={16} /> : <PanelLeftOpen size={16} />}
        onClick={onToggleLeftSidebar}
        className="p-button-text p-button-sm"
        tooltip={isLeftSidebarOpen ? 'Hide Components Panel' : 'Show Components Panel'}
        tooltipOptions={{ position: 'bottom' }}
      />
      
      <Button
        icon={isRightSidebarOpen ? <PanelRightClose size={16} /> : <PanelRightOpen size={16} />}
        onClick={onToggleRightSidebar}
        className="p-button-text p-button-sm"
        tooltip={isRightSidebarOpen ? 'Hide Properties Panel' : 'Show Properties Panel'}
        tooltipOptions={{ position: 'bottom' }}
      />
    </div>
  );

  const centerContent = (
    <div className="flex items-center gap-2">
      <Button
        icon={<Play size={16} />}
        label="Execute"
        className="p-button-success p-button-sm"
        tooltip="Execute Workflow"
        tooltipOptions={{ position: 'bottom' }}
      />
      
      <Button
        icon={<Save size={16} />}
        label="Save"
        className="p-button-outlined p-button-sm"
        tooltip="Save Workflow"
        tooltipOptions={{ position: 'bottom' }}
      />
    </div>
  );

  const rightContent = (
    <div className="flex items-center gap-2">
      <FileUpload
        mode="basic"
        name="templates"
        accept=".json"
        maxFileSize={1000000}
        onUpload={handleTemplateUpload}
        chooseLabel="Upload Templates"
        className="p-button-outlined p-button-sm"
        chooseOptions={{
          icon: <Upload size={16} />,
          iconOnly: false,
          className: 'p-button-outlined p-button-sm',
        }}
      />
      
      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={onWorkflowImport}
        style={{ display: 'none' }}
      />
      
      <Button
        icon={<FolderOpen size={16} />}
        onClick={handleWorkflowImportClick}
        className="p-button-outlined p-button-sm"
        tooltip="Import Workflow"
        tooltipOptions={{ position: 'bottom' }}
      />
      
      <Button
        icon={<Download size={16} />}
        onClick={onWorkflowExport}
        className="p-button-outlined p-button-sm"
        tooltip="Export Workflow"
        tooltipOptions={{ position: 'bottom' }}
      />
      
      <div className="h-6 w-px bg-gray-300 dark:bg-gray-600 mx-1" />
      
      <Button
        icon={<Settings size={16} />}
        className="p-button-text p-button-sm"
        tooltip="Settings"
        tooltipOptions={{ position: 'bottom' }}
      />
      
      <Button
        icon={isDarkMode ? <Sun size={16} /> : <Moon size={16} />}
        onClick={onToggleTheme}
        className="p-button-text p-button-sm"
        tooltip={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        tooltipOptions={{ position: 'bottom' }}
      />
    </div>
  );

  return (
    <>
      <Toast ref={toast} />
      <div className="ai-header-content">
        <div className="ai-header-left">
          <div className="warry-logo">
            <div className="warry-logo-icon">
              <img 
                src="/logo.png" 
                alt="WarryWorks Logo" 
                className="warry-logo-image"
              />
            </div>
            <div className="warry-logo-text">
              <div className="warry-brand">WarryWorks</div>
              <div className="warry-product">Agentic Builder</div>
            </div>
          </div>
        </div>
        
        <div className="ai-header-center">
          <button 
            className="warry-button primary"
            onClick={onWorkflowExecute}
          >
            <Play size={18} />
            <span>Execute Workflow</span>
          </button>
          
          <button 
            className="warry-button secondary"
            onClick={onWorkflowExport}
          >
            <Save size={16} />
            <span>Save Project</span>
          </button>
        </div>
        
        <div className="ai-header-right">
          <div className="warry-actions">
            <FileUpload
              mode="basic"
              name="templates"
              accept=".json"
              maxFileSize={1000000}
              onUpload={handleTemplateUpload}
              chooseLabel="Upload"
              className="warry-button ghost"
              chooseOptions={{
                icon: <Upload size={16} />,
                iconOnly: false,
                className: 'warry-button ghost',
              }}
            />
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={onWorkflowImport}
              style={{ display: 'none' }}
            />
            
            <button
              className="warry-button ghost icon-only"
              onClick={handleWorkflowImportClick}
              title="Import Workflow"
            >
              <FolderOpen size={18} />
            </button>
            
            <button
              className="warry-button ghost icon-only"
              onClick={onWorkflowExport}
              title="Export Workflow"
            >
              <Download size={18} />
            </button>
            
            <div className="warry-divider"></div>
            
            <button 
              className="warry-button ghost icon-only"
              title="Settings"
            >
              <Settings size={18} />
            </button>
            
            <button
              className="warry-button ghost icon-only"
              onClick={onToggleTheme}
              title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}