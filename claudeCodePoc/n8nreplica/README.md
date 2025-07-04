# N8N Replica - AI Workflow Builder

A modern, professional React-based workflow builder that replicates n8n functionality with a focus on agentic AI workflows. Built with Next.js, React Flow, PrimeReact, and Tailwind CSS.

## Features

### 🎨 **Professional UI/UX**
- Clean, modern interface with dark/light theme support
- Three-panel layout: Component palette, main canvas, properties panel
- Responsive design with mobile support
- Professional animations and transitions
- Glass morphism effects and gradient backgrounds

### 🔧 **Workflow Builder**
- Drag and drop interface for building workflows
- Multiple node types: Triggers, Actions, Conditions, Transforms, Outputs
- Visual connection system with handles and edges
- Real-time node property editing
- Canvas controls (zoom, pan, minimap)

### 📋 **Component System**
- Pre-built component library with 15+ components
- Component categories: Triggers, Actions, AI, Data, Integrations
- Search and filter functionality
- JSON template upload for custom components
- Extensible component architecture

### 🤖 **AI Integration**
- AI text generation components
- Support for multiple AI models (GPT, Claude)
- Configurable AI parameters (temperature, tokens, etc.)
- AI-powered workflow suggestions

### 💾 **Import/Export**
- JSON workflow export/import
- YAML export support
- JavaScript and Python code generation
- Workflow validation and error checking
- Template sharing capabilities

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **UI Library**: React with TypeScript
- **Flow Builder**: React Flow
- **Component Library**: PrimeReact
- **Styling**: Tailwind CSS
- **Icons**: Lucide React & PrimeIcons
- **Drag & Drop**: @dnd-kit

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Navigate to the project directory:
```bash
cd n8nreplica
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles and theme
│   └── page.tsx           # Main page component
├── components/            # React components
│   ├── nodes/            # Custom node components
│   ├── Header.tsx        # Application header
│   ├── LeftSidebar.tsx   # Component palette
│   ├── RightSidebar.tsx  # Properties panel
│   ├── ComponentCard.tsx # Component card
│   └── WorkflowBuilder.tsx # Main workflow canvas
├── data/                 # Static data and configurations
│   └── defaultComponents.ts # Default component library
├── types/                # TypeScript type definitions
│   └── index.ts          # Main type definitions
├── utils/                # Utility functions
│   └── workflowUtils.ts  # Workflow manipulation utilities
└── ...
```

## Usage

### Building Workflows

1. **Drag Components**: Drag components from the left sidebar to the canvas
2. **Connect Nodes**: Click and drag from output handles to input handles
3. **Configure Properties**: Select nodes to edit properties in the right sidebar
4. **Upload Templates**: Use the header upload button to add custom components
5. **Export Workflows**: Export your workflows as JSON, YAML, or code

### Component Types

- **🎯 Trigger Nodes** (Green): Start workflow execution
- **🌐 Action Nodes** (Blue): Perform operations
- **🔍 Condition Nodes** (Yellow): Control flow logic
- **🔄 Transform Nodes** (Purple): Data manipulation
- **📝 Output Nodes** (Red): End results

### JSON Template Upload

Upload custom components via the header upload button with this format:

```json
[
  {
    "id": "my-custom-component",
    "name": "My Component",
    "type": "action",
    "category": "actions",
    "icon": "⚡",
    "color": "#3b82f6",
    "description": "Custom action description",
    "functionality": "What this component does",
    "operation": "custom_operation",
    "inputs": [],
    "outputs": [],
    "parameters": [],
    "version": "1.0.0"
  }
]
```

## Development

### Build for Production

```bash
npm run build
npm start
```

### Linting and Type Checking

```bash
npm run lint
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License

## Acknowledgments

- React Flow team for the excellent flow library
- PrimeReact for the comprehensive component library
- Tailwind CSS for the utility-first CSS framework
- Next.js team for the amazing React framework
- n8n for inspiration and workflow concepts

---

**Built with ❤️ for the developer community**
